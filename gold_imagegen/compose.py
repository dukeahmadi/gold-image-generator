"""Pixel-preserving composition of cutouts: solid backgrounds, multi-piece sets.

Product pixels are copied onto the canvas; they are only ever scaled DOWN (never up), and only
when several pieces share one canvas. Everything here is deterministic: no model is involved.
"""
from __future__ import annotations

import math

from PIL import Image, ImageChops, ImageFilter, ImageOps

VISIBLE_ALPHA = 8
SHADOW_OPACITY = 0.22
DARK_SHADOW_OPACITY = 0.5  # shadows must be stronger to read on dark backgrounds
REFLECTION_HEIGHT = 0.35  # fraction of the product height
REFLECTION_OPACITY = 0.35

PRESETS: dict[str, tuple[int, int, int]] = {
    "white": (255, 255, 255),
    "black": (13, 13, 13),
    "charcoal": (38, 38, 42),
    "navy": (11, 31, 58),
    "burgundy": (90, 15, 31),
    "emerald": (14, 59, 46),
    "beige": (232, 220, 200),
    "blush": (240, 222, 218),
}


def parse_color(value: str) -> tuple[int, int, int]:
    """A preset name (see PRESETS) or a hex color like '#0B1F3A' / '0B1F3A'."""
    key = value.strip().lower()
    if key in PRESETS:
        return PRESETS[key]
    hex_value = key.lstrip("#")
    try:
        if len(hex_value) != 6:
            raise ValueError
        return tuple(int(hex_value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError:
        raise ValueError(
            f"unknown color {value!r}: use a hex code like #0B1F3A or one of {sorted(PRESETS)}"
        ) from None


def luminance(color: tuple[int, int, int]) -> float:
    r, g, b = color
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255


def trim(cutout: Image.Image) -> Image.Image:
    """Crop to the bounding box of visible pixels."""
    mask = cutout.getchannel("A").point(lambda a: 255 if a > VISIBLE_ALPHA else 0)
    box = mask.getbbox()
    if box is None:
        raise ValueError("no product found in the photo")
    return cutout.crop(box)


def shadow_layer(
    alpha: Image.Image,
    size: tuple[int, int],
    position: tuple[int, int],
    *,
    blur: float,
    offset: tuple[int, int],
    opacity: float,
) -> Image.Image:
    """A black, blurred copy of `alpha` shifted by `offset`, as an RGBA layer of `size`."""
    mask = Image.new("L", size, 0)
    mask.paste(alpha, (position[0] + offset[0], position[1] + offset[1]))
    mask = mask.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * opacity))
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    layer.putalpha(mask)
    return layer


def _default_shadow(product: Image.Image, side: int, position: tuple[int, int], color) -> Image.Image:
    blur = max(2.0, side * 0.012)
    offset = round(blur * 0.8)
    opacity = DARK_SHADOW_OPACITY if luminance(color) < 0.35 else SHADOW_OPACITY
    return shadow_layer(
        product.getchannel("A"), (side, side), position, blur=blur, offset=(offset, offset), opacity=opacity
    )


def _vignette(canvas: Image.Image, strength: float) -> Image.Image:
    mask = Image.radial_gradient("L").resize(canvas.size).point(lambda v: int(v * strength))
    return Image.composite(Image.new("RGBA", canvas.size, (0, 0, 0, 255)), canvas, mask)


def _reflection(product: Image.Image, height: int) -> Image.Image:
    """Mirror image of the product's bottom edge, fading out downwards."""
    w, _ = product.size
    flipped = ImageOps.flip(product).crop((0, 0, w, height))
    fade = ImageOps.invert(Image.linear_gradient("L")).resize((w, height))
    fade = fade.point(lambda v: int(v * REFLECTION_OPACITY))
    flipped.putalpha(ImageChops.multiply(flipped.getchannel("A"), fade))
    return flipped


def solid_background(
    cutout: Image.Image,
    color: tuple[int, int, int] = (255, 255, 255),
    *,
    margin: float = 0.08,
    shadow: bool = True,
    reflection: bool = False,
    vignette: float = 0.0,
) -> Image.Image:
    """Center the product on a square canvas of one color.

    Layout: block = product (+ reflection below it); side = round(max(w, block_h) / (1 - 2 * margin));
    the block is centered. A glossy-floor reflection replaces the drop shadow.
    """
    product = trim(cutout)
    w, h = product.size
    reflect_h = round(h * REFLECTION_HEIGHT) if reflection else 0
    gap = round(h * 0.01) if reflection else 0
    block_h = h + gap + reflect_h
    side = round(max(w, block_h) / (1 - 2 * margin))
    x, y = (side - w) // 2, (side - block_h) // 2

    canvas = Image.new("RGBA", (side, side), color + (255,))
    if vignette:
        canvas = _vignette(canvas, vignette)
    if reflection:
        canvas.alpha_composite(_reflection(product, reflect_h), (x, y + h + gap))
    elif shadow:
        canvas.alpha_composite(_default_shadow(product, side, (x, y), color))
    canvas.alpha_composite(product, (x, y))
    return canvas.convert("RGB")


def _grid_positions(
    sizes: list[tuple[int, int]], margin: float
) -> tuple[int, list[tuple[int, int]]]:
    """Square canvas side and top-left position of each piece in a centered grid."""
    n = len(sizes)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    cell_w = max(w for w, _ in sizes)
    cell_h = max(h for _, h in sizes)
    gap = round(0.06 * max(cell_w, cell_h))
    grid_w = cols * cell_w + (cols - 1) * gap
    grid_h = rows * cell_h + (rows - 1) * gap
    side = round(max(grid_w, grid_h) / (1 - 2 * margin))
    origin_x, origin_y = (side - grid_w) // 2, (side - grid_h) // 2

    positions = []
    for i, (w, h) in enumerate(sizes):
        row, col = divmod(i, cols)
        in_row = cols if row < rows - 1 else n - cols * (rows - 1)
        row_w = in_row * cell_w + (in_row - 1) * gap
        x0 = origin_x + (grid_w - row_w) // 2 + col * (cell_w + gap)
        y0 = origin_y + row * (cell_h + gap)
        positions.append((x0 + (cell_w - w) // 2, y0 + (cell_h - h) // 2))
    return side, positions


def set_layout(
    cutouts: list[Image.Image],
    color: tuple[int, int, int] = (255, 255, 255),
    *,
    margin: float = 0.08,
    weights: list[float] | None = None,
    shadow: bool = True,
    vignette: float = 0.0,
) -> Image.Image:
    """Arrange several pieces (necklace + earrings + ring...) on one square canvas.

    Pieces are shrunk, never enlarged, to the longest side of the smallest piece, then multiplied by
    `weights` (each in (0, 1]; use it to make e.g. earrings smaller). This balances visual weight;
    it does NOT reproduce real-world proportions, which a photo cannot tell us.
    """
    if not cutouts:
        raise ValueError("a set needs at least one piece")
    weights = weights or [1.0] * len(cutouts)
    if len(weights) != len(cutouts) or any(not 0 < wt <= 1 for wt in weights):
        raise ValueError("weights must be one number in (0, 1] per piece")

    products = [trim(c) for c in cutouts]
    common = min(max(p.size) for p in products)
    scaled = []
    for product, weight in zip(products, weights, strict=True):
        scale = min(1.0, common * weight / max(product.size))
        if scale < 1.0:
            size = (max(1, round(product.width * scale)), max(1, round(product.height * scale)))
            product = product.resize(size, Image.LANCZOS)
        scaled.append(product)

    side, positions = _grid_positions([p.size for p in scaled], margin)
    canvas = Image.new("RGBA", (side, side), color + (255,))
    if vignette:
        canvas = _vignette(canvas, vignette)
    if shadow:
        for product, position in zip(scaled, positions, strict=True):
            canvas.alpha_composite(_default_shadow(product, side, position, color))
    for product, position in zip(scaled, positions, strict=True):
        canvas.alpha_composite(product, position)
    return canvas.convert("RGB")
