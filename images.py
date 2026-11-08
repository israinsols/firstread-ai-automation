"""Create deterministic, locally generated social covers and WebP thumbnails."""

from __future__ import annotations

import io
import math
import re
import unicodedata

from PIL import Image, ImageDraw, ImageFont


def _font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_cover_images(title: str, site_name: str = "Firstread.co.uk") -> tuple[bytes, bytes]:
    """Return original topic-themed editorial artwork as a PNG and WebP."""
    normalized = unicodedata.normalize("NFKC", title).casefold()
    themes = (
        (("food", "eat", "cook", "date label", "best-before", "use-by"), "#f3dfb3", "#315e4b", "plate"),
        (("sport", "activity", "exercise", "fitness", "nhs"), "#c8e3d2", "#1e665a", "ball"),
        (("phone", "android", "security", "backup", "tech"), "#d3d9f4", "#3d4d8c", "phone"),
        (("clock", "time", "bst", "gmt", "lifestyle"), "#f0d7c8", "#955d43", "clock"),
        (("law", "consumer", "faulty", "refund", "rights"), "#e7d8c0", "#6f423b", "scales"),
        (("celebrity", "concert", "ticket", "artist"), "#ebcfe0", "#8b456b", "ticket"),
        (("scam", "news", "email", "text", "report"), "#cadfe3", "#315d72", "envelope"),
    )
    background, ink, motif = "#e7e9e3", "#435c56", "spark"
    for words, candidate_background, candidate_ink, candidate_motif in themes:
        if any(word in normalized for word in words):
            background, ink, motif = candidate_background, candidate_ink, candidate_motif
            break

    image = Image.new("RGB", (1200, 630), background)
    draw = ImageDraw.Draw(image)
    paper = "#f8f5ed"
    draw.rounded_rectangle((42, 42, 1158, 588), radius=42, fill=paper)
    draw.ellipse((650, 63, 1128, 541), fill=background)
    draw.ellipse((734, 146, 1044, 456), fill=paper, outline=ink, width=5)

    if motif == "plate":
        draw.ellipse((786, 198, 992, 404), fill="#e7b77e", outline=ink, width=5)
        draw.ellipse((818, 230, 960, 372), fill=paper, outline=ink, width=4)
        for angle in range(0, 360, 60):
            radians = math.radians(angle)
            x = 889 + math.cos(radians) * 55
            y = 301 + math.sin(radians) * 55
            draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill="#7fa06d")
        draw.line((1040, 220, 1040, 382), fill=ink, width=8)
        draw.line((1026, 220, 1026, 272), fill=ink, width=4)
        draw.line((1054, 220, 1054, 272), fill=ink, width=4)
    elif motif == "phone":
        draw.rounded_rectangle((824, 164, 968, 438), radius=28, fill=ink)
        draw.rounded_rectangle((836, 184, 956, 412), radius=16, fill="#e9eef8")
        draw.rounded_rectangle((851, 206, 941, 337), radius=10, fill="#91b8bd")
        draw.ellipse((884, 365, 908, 389), fill="#f3bf85")
        draw.line((864, 350, 928, 350), fill=ink, width=5)
        draw.ellipse((962, 164, 1018, 220), fill="#e8a878")
        draw.line((977, 193, 991, 207), fill=paper, width=6)
        draw.line((991, 207, 1007, 177), fill=paper, width=6)
    elif motif == "clock":
        draw.ellipse((790, 198, 1002, 410), fill="#f4e9d8", outline=ink, width=7)
        for angle in range(0, 360, 30):
            radians = math.radians(angle - 90)
            x1, y1 = 896 + math.cos(radians) * 82, 304 + math.sin(radians) * 82
            x2, y2 = 896 + math.cos(radians) * 92, 304 + math.sin(radians) * 92
            draw.line((x1, y1, x2, y2), fill=ink, width=4)
        draw.line((896, 304, 896, 242), fill=ink, width=8)
        draw.line((896, 304, 947, 329), fill=ink, width=7)
        draw.ellipse((887, 295, 905, 313), fill="#d68963")
    elif motif == "ball":
        draw.ellipse((786, 194, 1006, 414), fill="#e8a779", outline=ink, width=6)
        draw.polygon(((896, 263), (936, 292), (921, 337), (871, 337), (856, 292)), fill="#f5eee0", outline=ink)
        draw.arc((790, 204, 1000, 414), 205, 325, fill=ink, width=5)
        draw.arc((790, 204, 1000, 414), 25, 145, fill=ink, width=5)
        draw.line((856, 292, 817, 270), fill=ink, width=5)
        draw.line((936, 292, 978, 270), fill=ink, width=5)
        draw.line((871, 337, 850, 382), fill=ink, width=5)
        draw.line((921, 337, 942, 382), fill=ink, width=5)
    elif motif == "scales":
        draw.line((896, 194, 896, 400), fill=ink, width=11)
        draw.line((820, 238, 972, 238), fill=ink, width=10)
        draw.ellipse((876, 176, 916, 216), fill="#d49b69")
        draw.line((839, 241, 817, 330), fill=ink, width=5)
        draw.line((875, 241, 897, 330), fill=ink, width=5)
        draw.line((989, 241, 967, 330), fill=ink, width=5)
        draw.line((953, 241, 931, 330), fill=ink, width=5)
        draw.arc((790, 304, 924, 370), 0, 180, fill=ink, width=8)
        draw.arc((910, 304, 1044, 370), 0, 180, fill=ink, width=8)
        draw.line((838, 400, 954, 400), fill=ink, width=10)
    elif motif == "ticket":
        draw.rounded_rectangle((786, 236, 1006, 370), radius=22, fill="#d68cab", outline=ink, width=5)
        draw.line((934, 242, 934, 364), fill=paper, width=5)
        for y in range(258, 351, 22):
            draw.ellipse((922, y, 946, y + 12), fill=paper)
        draw.polygon(((850, 263), (858, 282), (879, 282), (862, 295), (868, 316), (850, 303), (832, 316), (838, 295), (821, 282), (842, 282)), fill=paper)
    elif motif == "envelope":
        draw.rounded_rectangle((778, 232, 1014, 380), radius=20, fill="#f2e7d5", outline=ink, width=6)
        draw.line((786, 248, 896, 330, 1006, 248), fill=ink, width=7)
        draw.line((786, 366, 862, 306), fill=ink, width=5)
        draw.line((1006, 366, 930, 306), fill=ink, width=5)
        draw.ellipse((950, 175, 1030, 255), fill="#86aa91", outline=ink, width=4)
        draw.line((972, 216, 989, 233), fill=paper, width=7)
        draw.line((989, 233, 1011, 197), fill=paper, width=7)
    else:
        draw.polygon(((896, 192), (1006, 304), (896, 416), (786, 304)), fill="#e8b47e", outline=ink)
        draw.ellipse((874, 282, 918, 326), fill=paper)

    draw.text((82, 82), site_name.upper(), fill=ink, font=_font(23))
    draw.line((82, 125, 232, 125), fill=ink, width=3)
    draw.ellipse((1044, 464, 1084, 504), fill="#d68c68")
    draw.ellipse((1081, 500, 1101, 520), fill=ink)

    thumbnail = image.resize((400, 210), Image.Resampling.LANCZOS)
    full_buffer = io.BytesIO()
    thumbnail_buffer = io.BytesIO()
    image.save(full_buffer, format="PNG", optimize=True)
    thumbnail.save(thumbnail_buffer, format="WEBP", quality=82, method=4)
    return full_buffer.getvalue(), thumbnail_buffer.getvalue()
