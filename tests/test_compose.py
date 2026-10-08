import random

import pytest
from PIL import Image, ImageChops

from gold_imagegen import compose

NAVY = (11, 31, 58)


def _block(w=60, h=40, seed=1):
    """Noisy opaque block, so any changed pixel is detectable."""
    rng = random.Random(seed)
    block = Image.new("RGBA", (w, h))
    block.putdata([(rng.randrange(256), rng.randrange(256), rng.randrange(256), 255) for _ in range(w * h)])
    return block


def _cutout(block, pad=20):
    img = Image.new("RGBA", (block.width + 2 * pad, block.height + 2 * pad), (0, 0, 0, 0))
    img.paste(block, (pad, pad))
    return img


def _same(a, b):
    return ImageChops.difference(a.convert("RGB"), b.convert("RGB")).getbbox() is None


def test_parse_color():
    assert compose.parse_color("Navy") == compose.PRESETS["navy"]
    assert compose.parse_color("#0B1F3A") == (11, 31, 58)
    assert compose.parse_color("0b1f3a") == (11, 31, 58)
    for bad in ("nope", "#12345", "#GGGGGG", ""):
        with pytest.raises(ValueError, match="unknown color"):
            compose.parse_color(bad)


@pytest.mark.parametrize("shadow", [True, False])
def test_solid_background_keeps_pixels_and_color(shadow):
    block = _block()
    out = compose.solid_background(_cutout(block), NAVY, margin=0.1, shadow=shadow)
    w, h = block.size
    side = round(max(w, h) / 0.8)
    x, y = (side - w) // 2, (side - h) // 2
    assert out.size == (side, side)
    assert out.getpixel((0, 0)) == NAVY
    assert _same(out.crop((x, y, x + w, y + h)), block)


def test_reflection_sits_below_the_product_and_keeps_pixels():
    block = _block()
    bg = (13, 13, 13)
    out = compose.solid_background(_cutout(block), bg, margin=0.1, reflection=True, shadow=True)
    w, h = block.size
    reflect_h = round(h * compose.REFLECTION_HEIGHT)
    gap = round(h * 0.01)
    side = round(max(w, h + gap + reflect_h) / 0.8)
    x, y = (side - w) // 2, (side - (h + gap + reflect_h)) // 2
    assert _same(out.crop((x, y, x + w, y + h)), block)
    assert max(out.getpixel((x + w // 2, y + h + gap + 1))) > max(bg)  # reflection is lighter than the floor
    assert out.getpixel((0, 0)) == bg


def test_vignette_darkens_corners_without_touching_the_product():
    block = _block()
    plain = compose.solid_background(_cutout(block), (200, 200, 200), shadow=False)
    vignetted = compose.solid_background(_cutout(block), (200, 200, 200), shadow=False, vignette=0.5)
    assert plain.getpixel((0, 0)) == (200, 200, 200)
    assert vignetted.getpixel((0, 0))[0] < 200
    w, h = block.size
    side = plain.width
    x, y = (side - w) // 2, (side - h) // 2
    assert _same(vignetted.crop((x, y, x + w, y + h)), block)


def test_set_layout_places_each_piece_exactly_when_sizes_match():
    blocks = [_block(30, 30, seed=i) for i in (1, 2, 3)]
    out = compose.set_layout([_cutout(b, 5) for b in blocks], (255, 255, 255), margin=0.1, shadow=False)
    side, positions = compose._grid_positions([b.size for b in blocks], 0.1)
    assert out.size == (side, side)
    for block, (x, y) in zip(blocks, positions):
        assert _same(out.crop((x, y, x + block.width, y + block.height)), block)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 7])
def test_grid_positions_stay_inside_and_never_overlap(n):
    sizes = [(30 + 5 * i, 20 + 3 * i) for i in range(n)]
    side, positions = compose._grid_positions(sizes, 0.08)
    rects = [(x, y, x + w, y + h) for (x, y), (w, h) in zip(positions, sizes)]
    for left, top, right, bottom in rects:
        assert 0 <= left and 0 <= top and right <= side and bottom <= side
    for i, a in enumerate(rects):
        for b in rects[i + 1 :]:
            assert a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1]


def test_set_layout_shrinks_larger_pieces_and_never_enlarges():
    big, small = _block(80, 40), _block(30, 20)
    out = compose.set_layout([_cutout(big), _cutout(small)], shadow=False, margin=0.1)
    # common size = longest side of the smallest piece (30): big becomes 30x15, small stays 30x20
    side, _ = compose._grid_positions([(30, 15), (30, 20)], 0.1)
    assert out.size == (side, side)


def test_set_layout_validates_input():
    piece = _cutout(_block())
    with pytest.raises(ValueError, match="at least one"):
        compose.set_layout([])
    with pytest.raises(ValueError, match="weights"):
        compose.set_layout([piece, piece], weights=[1.0])
    with pytest.raises(ValueError, match="weights"):
        compose.set_layout([piece], weights=[1.5])
