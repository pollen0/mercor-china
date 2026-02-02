import httpx
import logging
import tempfile
import os
from typing import Optional
from ..config import settings
from .storage import storage_service

logger = logging.getLogger("pathway.transcription")


class TranscriptionService:
    """Service for transcribing audio/video using OpenAI Whisper API."""

    def __init__(self):
        # OpenAI Whisper for speech-to-text (Claude doesn't have native STT)
        self.api_key = settings.openai_api_key
        self.base_url = "https://api.openai.com"

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
        Transcribe audio from a local file using OpenAI Whisper.

        Args:
            file_path: Path to the audio/video file
            language: Language code (default "en" for English)

        Returns:
            Transcribed text
        """
        with open(file_path, "rb") as audio_file:
            audio_data = audio_file.read()

        return await self._transcribe_with_whisper(audio_data, file_path, language)

    async def _transcribe_with_whisper(
        self, audio_data: bytes, filename: str, language: str = "en"
    ) -> str:
        """
        Transcribe using OpenAI Whisper API.

        Args:
            audio_data: Raw audio bytes
            filename: Original filename
            language: Language code

        Returns:
            Transcribed text
        """
        if not self.api_key:
            return "[Transcription unavailable - OpenAI API not configured]"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # OpenAI Whisper audio transcription endpoint
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
            if e.response.status_code == 404:
                return "[Transcription unavailable - Whisper endpoint not available]"
            logger.error(f"OpenAI Whisper transcription error: {e}")
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
            language: Language code (default "en" for English)

        Returns:
            Transcribed text
        """
        return await self._transcribe_with_whisper(data, filename, language)


# Global instance
transcription_service = TranscriptionService()
