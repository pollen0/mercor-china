import httpx
import logging
import tempfile
import os
from typing import Optional
from ..config import settings
from .storage import storage_service

logger = logging.getLogger("pathway.transcription")


class TranscriptionService:
    """Service for transcribing audio/video using DeepSeek ASR API."""

    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url

    async def transcribe_from_url(self, video_url: str, language: str = "en") -> str:
        """
        Transcribe audio from a video URL.

        Args:
            video_url: URL of the video to transcribe
            language: Language code (default "zh" for Chinese)

        Returns:
            Transcribed text
        """
        # Download the video to a temp file
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(video_url)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name

        try:
            return await self.transcribe_file(tmp_path, language)
        finally:
            os.unlink(tmp_path)

    async def transcribe_from_key(self, storage_key: str, language: str = "en") -> str:
        """
        Transcribe audio from a video stored in R2.

        Args:
            storage_key: R2 storage key of the video
            language: Language code (default "zh" for Chinese)

        Returns:
            Transcribed text
        """
        # Get signed URL and transcribe
        signed_url = storage_service.get_signed_url(storage_key)
        return await self.transcribe_from_url(signed_url, language)

    async def transcribe_file(self, file_path: str, language: str = "en") -> str:
        """
        Transcribe audio from a local file using DeepSeek ASR.

        Args:
            file_path: Path to the audio/video file
            language: Language code (default "zh" for Chinese)

        Returns:
            Transcribed text
        """
        with open(file_path, "rb") as audio_file:
            audio_data = audio_file.read()

        return await self._transcribe_with_deepseek(audio_data, file_path, language)

    async def _transcribe_with_deepseek(
        self, audio_data: bytes, filename: str, language: str = "en"
    ) -> str:
        """
        Transcribe using DeepSeek ASR API (OpenAI Whisper-compatible).

        Args:
            audio_data: Raw audio bytes
            filename: Original filename
            language: Language code

        Returns:
            Transcribed text
        """
        if not self.api_key:
            return "[Transcription unavailable - DeepSeek API not configured]"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # DeepSeek uses OpenAI-compatible audio transcription endpoint
                response = await client.post(
                    f"{self.base_url}/v1/audio/transcriptions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    files={
                        "file": (os.path.basename(filename), audio_data, "audio/webm"),
                    },
                    data={
                        "model": "whisper-1",
                        "language": language,
                        "response_format": "text",
                    },
                )
                response.raise_for_status()
                return response.text.strip()

        except httpx.HTTPStatusError as e:
            # If DeepSeek doesn't support audio API, fall back to placeholder
            if e.response.status_code == 404:
                return "[Transcription unavailable - ASR endpoint not available]"
            logger.error(f"DeepSeek transcription error: {e}")
            return f"[Transcription error: {str(e)}]"
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return f"[Transcription error: {str(e)}]"

    async def transcribe_bytes(
        self, data: bytes, filename: str = "audio.webm", language: str = "en"
    ) -> str:
        """
        Transcribe audio from raw bytes.

        Args:
            data: Raw audio/video bytes
            filename: Filename hint for the API
            language: Language code (default "zh" for Chinese)

        Returns:
            Transcribed text
        """
        return await self._transcribe_with_deepseek(data, filename, language)


# Global instance
transcription_service = TranscriptionService()
