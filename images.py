"""Create deterministic, locally generated social covers and WebP thumbnails."""

from __future__ import annotations

import io
import unicodedata
from pathlib import Path

from PIL import Image, ImageOps


PHOTO_ROOT = Path(__file__).resolve().parent / "static" / "images"
PHOTO_THEMES = (
    (("food", "eat", "cook", "date label", "best-before", "use-by"), "food.jpg"),
    (("sport", "activity", "exercise", "fitness", "nhs"), "sport.jpg"),
    (("phone", "android", "security", "backup", "tech"), "phone.jpg"),
    (("clock", "time", "bst", "gmt", "lifestyle"), "clock.jpg"),
    (("law", "consumer", "faulty", "refund", "rights"), "law.jpg"),
    (("celebrity", "concert", "ticket", "artist"), "concert.jpg"),
    (("scam", "news", "email", "text", "report"), "news.jpg"),
)


def make_cover_images(title: str, site_name: str = "Firstread.co.uk") -> tuple[bytes, bytes]:
    """Return a locally sourced, topic-matched photo cover and WebP thumbnail."""
    normalized = unicodedata.normalize("NFKC", title).casefold()
    photo_path = PHOTO_ROOT / "news.jpg"
    for words, filename in PHOTO_THEMES:
        if any(word in normalized for word in words):
            photo_path = PHOTO_ROOT / filename
            break
    if not photo_path.is_file():
        raise FileNotFoundError(f"Editorial cover photo is missing: {photo_path}")

    with Image.open(photo_path) as source:
        image = ImageOps.fit(source.convert("RGB"), (1200, 630), method=Image.Resampling.LANCZOS)

    thumbnail = image.resize((400, 210), Image.Resampling.LANCZOS)
    full_buffer = io.BytesIO()
    thumbnail_buffer = io.BytesIO()
    image.save(full_buffer, format="PNG", optimize=True)
    thumbnail.save(thumbnail_buffer, format="WEBP", quality=82, method=4)
    return full_buffer.getvalue(), thumbnail_buffer.getvalue()
