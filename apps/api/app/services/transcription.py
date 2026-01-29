import httpx
from openai import OpenAI
from typing import Optional
import tempfile
import os
from ..config import settings
from .storage import storage_service


class TranscriptionService:
    """Service for transcribing audio/video using OpenAI Whisper."""

    def __init__(self):
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            self._client = OpenAI(api_key=settings.openai_api_key)
        return self._client

    async def transcribe_from_url(self, video_url: str, language: str = "zh") -> str:
        """
        Transcribe audio from a video URL.

        Args:
            video_url: URL of the video to transcribe
            language: Language code (default "zh" for Chinese)

        Returns:
            Transcribed text
        """
        # Download the video to a temp file
        async with httpx.AsyncClient() as client:
            response = await client.get(video_url)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name

        try:
            return await self.transcribe_file(tmp_path, language)
        finally:
            os.unlink(tmp_path)

    async def transcribe_from_key(self, storage_key: str, language: str = "zh") -> str:
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

    async def transcribe_file(self, file_path: str, language: str = "zh") -> str:
        """
        Transcribe audio from a local file.

        Args:
            file_path: Path to the audio/video file
            language: Language code (default "zh" for Chinese)

        Returns:
            Transcribed text
        """
        with open(file_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="text"
            )
        return transcript

    async def transcribe_bytes(self, data: bytes, filename: str = "audio.webm", language: str = "zh") -> str:
        """
        Transcribe audio from raw bytes.

        Args:
            data: Raw audio/video bytes
            filename: Filename hint for the API
            language: Language code (default "zh" for Chinese)

        Returns:
            Transcribed text
        """
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name

        try:
            return await self.transcribe_file(tmp_path, language)
        finally:
            os.unlink(tmp_path)

    async def transcribe_with_timestamps(self, file_path: str, language: str = "zh") -> dict:
        """
        Transcribe audio with word-level timestamps.

        Args:
            file_path: Path to the audio/video file
            language: Language code

        Returns:
            Dictionary with text and word timestamps
        """
        with open(file_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )
        return {
            "text": transcript.text,
            "words": transcript.words if hasattr(transcript, 'words') else [],
            "duration": transcript.duration if hasattr(transcript, 'duration') else None
        }


# Global instance
transcription_service = TranscriptionService()
