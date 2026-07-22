import re
from urllib.parse import urlparse, parse_qs


def youtube_embed_url(url: str) -> str:
    """Convert a YouTube watch/short/embed URL into an embeddable URL. Returns '' if not parseable."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        video_id = ""
        if "youtu.be" in parsed.netloc:
            video_id = parsed.path.lstrip("/")
        elif "youtube.com" in parsed.netloc:
            if parsed.path.startswith("/embed/"):
                video_id = parsed.path.split("/embed/")[1]
            elif parsed.path.startswith("/shorts/"):
                video_id = parsed.path.split("/shorts/")[1]
            else:
                qs = parse_qs(parsed.query)
                video_id = qs.get("v", [""])[0]
        video_id = re.split(r"[?&/]", video_id)[0]
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
    except Exception:
        pass
    return ""


# --- File upload helpers ---
import os
from django.core.exceptions import ValidationError
from django.utils.text import get_valid_filename
from PIL import Image


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing path components and unsafe characters.

    Uses Django's get_valid_filename and os.path.basename to prevent path traversal.
    """
    if not filename:
        return filename
    # Prevent path traversal
    base = os.path.basename(filename)
    # Remove any remaining unsafe chars
    return get_valid_filename(base)


def validate_image_file(uploaded_file, allowed_mime_types=None, max_bytes: int = None):
    """Validate uploaded image for MIME type, size and integrity.

    - uploaded_file: an UploadedFile-like object
    - allowed_mime_types: list of allowed content types (defaults to JPEG/PNG)
    - max_bytes: maximum allowed bytes

    Raises ValidationError on failure.
    """
    if allowed_mime_types is None:
        allowed_mime_types = ["image/jpeg", "image/png"]

    # Content type check (best-effort; content_type might not be reliable but helps)
    content_type = getattr(uploaded_file, 'content_type', None)
    if content_type and content_type not in allowed_mime_types:
        raise ValidationError("Unsupported image type.")

    # File size check
    if max_bytes is not None:
        size = getattr(uploaded_file, 'size', None)
        if size is not None and size > max_bytes:
            raise ValidationError(f"Image file too large ( > {max_bytes} bytes ).")

    # Verify image content using Pillow
    try:
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        img.verify()
    except Exception:
        raise ValidationError("Uploaded file is not a valid image or is corrupted.")
    finally:
        try:
            uploaded_file.seek(0)
        except Exception:
            pass
