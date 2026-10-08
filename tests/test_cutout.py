import io
import random

import pytest
from PIL import Image, ImageChops

from gold_imagegen import cutout

MARGIN = 0.1


def _product(w=60, h=40, pad=20):
    """Noisy opaque block on a transparent border, so any changed pixel is detectable."""
    rng = random.Random(1)
    block = Image.new("RGBA", (w, h))
    block.putdata([(rng.randrange(256), rng.randrange(256), rng.randrange(256), 255) for _ in range(w * h)])
    img = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    img.paste(block, (pad, pad))
    return img, block


def _layout(block):
    w, h = block.size
    side = round(max(w, h) / (1 - 2 * MARGIN))
    return side, (side - w) // 2, (side - h) // 2


@pytest.mark.parametrize("shadow", [True, False])
def test_on_white_keeps_opaque_product_pixels_exactly(shadow):
    img, block = _product()
    out = cutout.on_white(img, margin=MARGIN, shadow=shadow)
    side, x, y = _layout(block)
    w, h = block.size
    assert out.size == (side, side)
    got = out.crop((x, y, x + w, y + h))
    assert ImageChops.difference(got, block.convert("RGB")).getbbox() is None


def test_on_white_background_is_pure_white_far_from_product():
    img, _ = _product()
    out = cutout.on_white(img, margin=MARGIN)
    assert out.getpixel((0, 0)) == (255, 255, 255)
    assert out.getpixel((out.width - 1, out.height - 1)) == (255, 255, 255)


def test_shadow_darkens_only_next_to_the_product():
    img, block = _product()
    side, x, y = _layout(block)
    w, h = block.size
    probe = (x + w // 2, y + h + 1)  # just below the product
    with_shadow = cutout.on_white(img, margin=MARGIN, shadow=True).getpixel(probe)
    without = cutout.on_white(img, margin=MARGIN, shadow=False).getpixel(probe)
    assert without == (255, 255, 255)
    assert 0 < with_shadow[0] < 255


def test_on_white_rejects_empty_cutout():
    with pytest.raises(ValueError, match="no product"):
        cutout.on_white(Image.new("RGBA", (10, 10), (0, 0, 0, 0)))


def test_trim_crops_to_product():
    img, block = _product()
    assert cutout.trim(img).size == block.size


def test_load_image_honors_exif_rotation():
    exif = Image.Exif()
    exif[0x0112] = 6  # rotate 90 degrees clockwise to display
    buffer = io.BytesIO()
    Image.new("RGB", (40, 20), (200, 10, 10)).save(buffer, format="JPEG", exif=exif)
    assert cutout.load_image(buffer.getvalue()).size == (20, 40)


def test_resolution_warning():
    assert cutout.resolution_warning((2000, 1500)) is None
    assert "554x554" in cutout.resolution_warning((554, 554))
