from io import BytesIO

from PIL import Image

from images import make_cover_images


def test_cover_images_use_real_topic_matched_photos():
    cases = (
        ("Best before and use by food dates", "food.jpg"),
        ("Android phone security and backup", "phone.jpg"),
        ("NHS sports activity guidelines", "sport.jpg"),
        ("Celebrity concert dates and tickets", "concert.jpg"),
        ("When do clocks change in the UK", "clock.jpg"),
        ("UK consumer rights and faulty goods", "law.jpg"),
        ("How to report scam emails and texts", "news.jpg"),
    )
    for title, filename in cases:
        cover, thumbnail = make_cover_images(title)
        with Image.open(BytesIO(cover)) as image:
            assert image.size == (1200, 630)
            assert image.getcolors(maxcolors=256) is None
        with Image.open(BytesIO(thumbnail)) as image:
            assert image.size == (400, 210)
