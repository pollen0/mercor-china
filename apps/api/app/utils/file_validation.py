"""
File validation utilities for uploads.
Validates file types using magic bytes, not just extensions.
"""
import logging
from typing import Optional, Tuple

logger = logging.getLogger("pathway.file_validation")

# Magic bytes for common file types
# Format: {extension: [(magic_bytes, offset), ...]}
MAGIC_BYTES = {
    # PDF
    "pdf": [(b"%PDF", 0)],

    # Microsoft Office formats (DOCX, XLSX, PPTX)
    "docx": [(b"PK\x03\x04", 0)],  # ZIP archive (Office Open XML)
    "xlsx": [(b"PK\x03\x04", 0)],
    "pptx": [(b"PK\x03\x04", 0)],

    # Legacy Office formats
    "doc": [(b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1", 0)],  # OLE compound doc
    "xls": [(b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1", 0)],

    # Images
    "jpg": [(b"\xFF\xD8\xFF", 0)],
    "jpeg": [(b"\xFF\xD8\xFF", 0)],
    "png": [(b"\x89PNG\r\n\x1A\n", 0)],
    "gif": [(b"GIF87a", 0), (b"GIF89a", 0)],
    "webp": [(b"RIFF", 0)],  # Also check for WEBP at offset 8
    "bmp": [(b"BM", 0)],

    # Video formats
    "mp4": [(b"\x00\x00\x00", 0)],  # ftyp box, need additional check
    "webm": [(b"\x1A\x45\xDF\xA3", 0)],  # EBML header (Matroska/WebM)
    "mkv": [(b"\x1A\x45\xDF\xA3", 0)],
    "avi": [(b"RIFF", 0)],  # Also check for AVI at offset 8
    "mov": [(b"\x00\x00\x00", 0)],  # moov or ftyp

    # Audio formats
    "mp3": [(b"\xFF\xFB", 0), (b"\xFF\xFA", 0), (b"\xFF\xF3", 0), (b"\xFF\xF2", 0), (b"ID3", 0)],
    "wav": [(b"RIFF", 0)],  # Also check for WAVE at offset 8
    "ogg": [(b"OggS", 0)],

    # Text formats (no magic bytes, use extension only)
    "txt": [],
    "json": [],
    "csv": [],
}

# File size limits in bytes
FILE_SIZE_LIMITS = {
    "resume": 10 * 1024 * 1024,      # 10 MB for resumes
    "transcript": 10 * 1024 * 1024,  # 10 MB for transcripts
    "video": 500 * 1024 * 1024,      # 500 MB for interview videos
    "image": 5 * 1024 * 1024,        # 5 MB for profile images
    "default": 10 * 1024 * 1024,     # 10 MB default
}

# Allowed extensions by category
ALLOWED_EXTENSIONS = {
    "resume": ["pdf", "docx", "doc"],
    "transcript": ["pdf", "docx", "doc", "jpg", "jpeg", "png"],
    "video": ["webm", "mp4", "mov"],
    "image": ["jpg", "jpeg", "png", "gif", "webp"],
}


def get_extension(filename: str) -> str:
    """Extract file extension from filename."""
    if not filename or "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def validate_magic_bytes(content: bytes, expected_ext: str) -> bool:
    """
    Validate file content against expected magic bytes.

    Args:
        content: File content (at least first 16 bytes)
        expected_ext: Expected file extension

    Returns:
        True if magic bytes match, False otherwise
    """
    if not content:
        return False

    ext = expected_ext.lower()

    # No magic bytes defined for this type (text files)
    if ext not in MAGIC_BYTES or not MAGIC_BYTES[ext]:
        return True

    # Check each possible magic byte sequence
    for magic, offset in MAGIC_BYTES[ext]:
        if len(content) >= offset + len(magic):
            if content[offset:offset + len(magic)] == magic:
                # Additional checks for formats that share magic bytes
                if ext in ["webp", "avi", "wav"]:
                    # RIFF formats need secondary check
                    if len(content) >= 12:
                        format_id = content[8:12]
                        if ext == "webp" and format_id != b"WEBP":
                            continue
                        if ext == "avi" and format_id != b"AVI ":
                            continue
                        if ext == "wav" and format_id != b"WAVE":
                            continue
                return True

    return False


def validate_file_size(content: bytes, category: str = "default") -> Tuple[bool, Optional[str]]:
    """
    Validate file size against limits.

    Args:
        content: File content
        category: File category for size limit

    Returns:
        (is_valid, error_message)
    """
    size = len(content)
    limit = FILE_SIZE_LIMITS.get(category, FILE_SIZE_LIMITS["default"])

    if size > limit:
        limit_mb = limit / (1024 * 1024)
        size_mb = size / (1024 * 1024)
        return False, f"File size ({size_mb:.1f}MB) exceeds limit ({limit_mb:.0f}MB)"

    if size == 0:
        return False, "File is empty"

    return True, None


def validate_extension(filename: str, category: str) -> Tuple[bool, Optional[str]]:
    """
    Validate file extension against allowed types.

    Args:
        filename: File name with extension
        category: File category

    Returns:
        (is_valid, error_message)
    """
    ext = get_extension(filename)

    if not ext:
        return False, "File has no extension"

    allowed = ALLOWED_EXTENSIONS.get(category, [])
    if not allowed:
        return True, None  # No restrictions for this category

    if ext not in allowed:
        return False, f"File type '.{ext}' not allowed. Allowed types: {', '.join(allowed)}"

    return True, None


def validate_file(
    content: bytes,
    filename: str,
    category: str = "default"
) -> Tuple[bool, Optional[str]]:
    """
    Comprehensive file validation.

    Args:
        content: File content
        filename: File name with extension
        category: File category (resume, transcript, video, image)

    Returns:
        (is_valid, error_message)
    """
    # Validate size
    is_valid, error = validate_file_size(content, category)
    if not is_valid:
        return False, error

    # Validate extension
    is_valid, error = validate_extension(filename, category)
    if not is_valid:
        return False, error

    # Validate magic bytes
    ext = get_extension(filename)
    if not validate_magic_bytes(content, ext):
        logger.warning(f"Magic bytes validation failed for {filename}")
        return False, f"File content does not match .{ext} format. File may be corrupted or misnamed."

    return True, None


def validate_video_file(content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate video file specifically for interview recordings.

    Args:
        content: Video file content
        filename: Video file name

    Returns:
        (is_valid, error_message)
    """
    # Basic file validation
    is_valid, error = validate_file(content, filename, "video")
    if not is_valid:
        return False, error

    ext = get_extension(filename)

    # Check for WebM specifically (preferred format for browser recordings)
    if ext == "webm":
        # WebM files start with EBML header
        if not content.startswith(b"\x1A\x45\xDF\xA3"):
            return False, "Invalid WebM file format"

        # Check for WebM DocType (should contain 'webm' string)
        # This is a simplified check - full validation would parse EBML
        if b"webm" not in content[:1000].lower():
            logger.warning(f"WebM file may be invalid: doctype not found in header")
            # Don't reject, just warn - some valid WebM files might not have it early

    # Check for MP4
    elif ext == "mp4":
        # MP4 files should have 'ftyp' box near the start
        if b"ftyp" not in content[:100]:
            return False, "Invalid MP4 file format"

    return True, None


def validate_resume_file(content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate resume file (PDF or DOCX).

    Args:
        content: File content
        filename: File name

    Returns:
        (is_valid, error_message)
    """
    return validate_file(content, filename, "resume")


def validate_transcript_file(content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate transcript file.

    Args:
        content: File content
        filename: File name

    Returns:
        (is_valid, error_message)
    """
    return validate_file(content, filename, "transcript")


def validate_image_file(content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate image file.

    Args:
        content: File content
        filename: File name

    Returns:
        (is_valid, error_message)
    """
    return validate_file(content, filename, "image")


# Quick check functions that return just bool
def is_valid_pdf(content: bytes) -> bool:
    """Quick check if content is a valid PDF."""
    return validate_magic_bytes(content, "pdf")


def is_valid_docx(content: bytes) -> bool:
    """Quick check if content is a valid DOCX."""
    return validate_magic_bytes(content, "docx")


def is_valid_webm(content: bytes) -> bool:
    """Quick check if content is a valid WebM."""
    return validate_magic_bytes(content, "webm")


def is_valid_mp4(content: bytes) -> bool:
    """Quick check if content is a valid MP4."""
    if not content.startswith(b"\x00\x00\x00"):
        return False
    return b"ftyp" in content[:100]
