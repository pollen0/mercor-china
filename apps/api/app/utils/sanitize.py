"""
XSS Sanitization utilities for user-generated content.
Removes potentially dangerous HTML/JavaScript from user input.
"""
import re
import html
import logging
from typing import Optional, Any, Dict, List, Union

logger = logging.getLogger("pathway.sanitize")

# Dangerous HTML tags that should be removed
DANGEROUS_TAGS = [
    'script', 'iframe', 'object', 'embed', 'form', 'input', 'button',
    'textarea', 'select', 'style', 'link', 'meta', 'base', 'applet',
    'frame', 'frameset', 'layer', 'ilayer', 'bgsound', 'title', 'head',
]

# Dangerous attributes that should be removed
DANGEROUS_ATTRS = [
    'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover',
    'onmousemove', 'onmouseout', 'onkeydown', 'onkeypress', 'onkeyup',
    'onload', 'onunload', 'onerror', 'onabort', 'onblur', 'onchange',
    'onfocus', 'onreset', 'onselect', 'onsubmit', 'onresize', 'onscroll',
    'oncontextmenu', 'ondrag', 'ondrop', 'onmouseenter', 'onmouseleave',
    'onwheel', 'oncopy', 'oncut', 'onpaste', 'onbeforeunload', 'formaction',
    'xlink:href', 'xmlns', 'style', 'srcdoc', 'data',
]

# Pattern to match HTML tags
HTML_TAG_PATTERN = re.compile(r'<[^>]+>', re.IGNORECASE | re.DOTALL)

# Pattern to match dangerous protocols in URLs
DANGEROUS_PROTOCOL_PATTERN = re.compile(
    r'(javascript|vbscript|data|file):', re.IGNORECASE
)

# Pattern to match event handlers
EVENT_HANDLER_PATTERN = re.compile(
    r'\s*on\w+\s*=', re.IGNORECASE
)


def strip_html_tags(text: str) -> str:
    """
    Remove all HTML tags from text.
    Use when you want plain text only.
    """
    if not text:
        return text
    return HTML_TAG_PATTERN.sub('', text)


def escape_html(text: str) -> str:
    """
    Escape HTML special characters.
    Converts < > & " ' to their HTML entity equivalents.
    """
    if not text:
        return text
    return html.escape(text, quote=True)


def sanitize_string(
    text: Optional[str],
    allow_newlines: bool = True,
    max_length: Optional[int] = None,
    strip_html: bool = True
) -> Optional[str]:
    """
    Sanitize a string for safe storage and display.

    Args:
        text: Input text to sanitize
        allow_newlines: Whether to preserve newline characters
        max_length: Maximum length (truncates if exceeded)
        strip_html: If True, removes HTML tags; if False, escapes them

    Returns:
        Sanitized string or None if input was None
    """
    if text is None:
        return None

    if not isinstance(text, str):
        text = str(text)

    # Strip leading/trailing whitespace
    text = text.strip()

    # Remove null bytes and other control characters (except newlines/tabs if allowed)
    if allow_newlines:
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    else:
        text = re.sub(r'[\x00-\x1f\x7f]', ' ', text)
        text = ' '.join(text.split())  # Normalize whitespace

    # Strip or escape HTML
    if strip_html:
        text = strip_html_tags(text)
    else:
        text = escape_html(text)

    # Remove dangerous protocols from any URLs that might remain
    text = DANGEROUS_PROTOCOL_PATTERN.sub('', text)

    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text


def sanitize_name(name: Optional[str]) -> Optional[str]:
    """
    Sanitize a person's name.
    Removes HTML, limits length, normalizes whitespace.
    """
    if not name:
        return name

    sanitized = sanitize_string(name, allow_newlines=False, max_length=200, strip_html=True)

    # Additional name-specific validation
    # Remove any remaining special characters that shouldn't be in names
    # but allow international characters, spaces, hyphens, apostrophes
    if sanitized:
        # Just ensure no HTML entities remain
        sanitized = html.unescape(sanitized)
        sanitized = sanitize_string(sanitized, allow_newlines=False, strip_html=True)

    return sanitized


def sanitize_email(email: Optional[str]) -> Optional[str]:
    """
    Sanitize an email address.
    """
    if not email:
        return email

    # Basic sanitization
    sanitized = sanitize_string(email, allow_newlines=False, max_length=320, strip_html=True)

    # Remove any whitespace
    if sanitized:
        sanitized = sanitized.replace(' ', '')

    return sanitized


def sanitize_url(url: Optional[str]) -> Optional[str]:
    """
    Sanitize a URL. Removes dangerous protocols.
    """
    if not url:
        return url

    sanitized = sanitize_string(url, allow_newlines=False, max_length=2048, strip_html=True)

    if sanitized:
        # Check for dangerous protocols
        if DANGEROUS_PROTOCOL_PATTERN.match(sanitized):
            logger.warning(f"Blocked dangerous URL protocol: {sanitized[:50]}...")
            return None

        # Only allow http, https, and relative URLs
        lower_url = sanitized.lower()
        if not (lower_url.startswith('http://') or
                lower_url.startswith('https://') or
                lower_url.startswith('/') or
                lower_url.startswith('#')):
            # Prepend https:// if no protocol
            if '://' not in sanitized and sanitized and sanitized[0].isalnum():
                sanitized = 'https://' + sanitized

    return sanitized


def sanitize_text_content(
    text: Optional[str],
    max_length: int = 50000
) -> Optional[str]:
    """
    Sanitize longer text content like descriptions, notes, bios.
    Preserves newlines but removes HTML.
    """
    return sanitize_string(text, allow_newlines=True, max_length=max_length, strip_html=True)


def sanitize_dict(
    data: Optional[Dict[str, Any]],
    string_keys: Optional[List[str]] = None,
    recursive: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Sanitize string values in a dictionary.

    Args:
        data: Dictionary to sanitize
        string_keys: Specific keys to sanitize (if None, sanitizes all string values)
        recursive: Whether to recursively sanitize nested dicts/lists

    Returns:
        Sanitized dictionary
    """
    if data is None:
        return None

    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        if string_keys is None or key in string_keys:
            if isinstance(value, str):
                result[key] = sanitize_string(value)
            elif isinstance(value, dict) and recursive:
                result[key] = sanitize_dict(value, string_keys, recursive)
            elif isinstance(value, list) and recursive:
                result[key] = sanitize_list(value, recursive)
            else:
                result[key] = value
        else:
            result[key] = value

    return result


def sanitize_list(
    data: Optional[List[Any]],
    recursive: bool = True
) -> Optional[List[Any]]:
    """
    Sanitize string values in a list.
    """
    if data is None:
        return None

    if not isinstance(data, list):
        return data

    result = []
    for item in data:
        if isinstance(item, str):
            result.append(sanitize_string(item))
        elif isinstance(item, dict) and recursive:
            result.append(sanitize_dict(item, recursive=recursive))
        elif isinstance(item, list) and recursive:
            result.append(sanitize_list(item, recursive))
        else:
            result.append(item)

    return result


def sanitize_resume_data(resume_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Sanitize parsed resume data specifically.
    Handles common resume fields.
    """
    if not resume_data:
        return resume_data

    # Deep copy to avoid modifying original
    sanitized = {}

    for key, value in resume_data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_text_content(value)
        elif isinstance(value, list):
            sanitized[key] = sanitize_list(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        else:
            sanitized[key] = value

    return sanitized


def sanitize_github_data(github_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Sanitize GitHub profile data.
    """
    if not github_data:
        return github_data

    sanitized = {}

    # Known string fields
    string_fields = ['username', 'name', 'bio', 'company', 'location', 'blog', 'email']

    for key, value in github_data.items():
        if key in string_fields and isinstance(value, str):
            sanitized[key] = sanitize_string(value, allow_newlines=key == 'bio')
        elif key == 'avatar_url':
            sanitized[key] = sanitize_url(value)
        elif isinstance(value, list):
            sanitized[key] = sanitize_list(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        else:
            sanitized[key] = value

    return sanitized


# Convenience function for model validators
def sanitize_for_storage(value: Any) -> Any:
    """
    Generic sanitization for values being stored in the database.
    """
    if isinstance(value, str):
        return sanitize_string(value)
    elif isinstance(value, dict):
        return sanitize_dict(value)
    elif isinstance(value, list):
        return sanitize_list(value)
    return value
