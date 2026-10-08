"""Local background removal for product photos: no API call, no generative model.

A segmentation model only predicts an alpha mask. The original product pixels are then
composited onto a white canvas, so shape, stones and engraving stay exactly as photographed.

Known limits (seen on real photos):
- thin chains over skin keep skin-tinted edge pixels (a silver chain can turn rose-gold);
- a product held between fingers is not separated from the fingers;
- small photos give small results: the product is never upscaled;
- a product cut off by the photo frame stays cut off; stray bits of fingers can remain.
"""
from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any

from PIL import Image, ImageOps

from .compose import solid_background, trim

__all__ = [
    "DEFAULT_MODEL", "QUALITY_MODEL", "MIN_LONG_SIDE", "CutoutResult", "load_image",
    "resolution_warning", "cut_out", "trim", "on_white", "process", "to_png",
]

# Measured on a 16 GB CPU container (see README): lite ~23 s/photo, 6.6 GB peak; dis ~37 s/photo, 7.7 GB peak.
DEFAULT_MODEL = "birefnet-general-lite"
QUALITY_MODEL = "birefnet-dis"  # slightly cleaner around filigree openings in the 6 photos tried
# Heuristic, not measured: below this a catalog-quality result is unlikely. Tune on real photos.
MIN_LONG_SIDE = 1500

_sessions: dict[str, Any] = {}


@dataclass(frozen=True)
class CutoutResult:
    cutout: Image.Image  # RGBA, same size as the input photo
    white: Image.Image  # RGB catalog-style image
    warning: str | None = None


def load_image(data: bytes) -> Image.Image:
    """Decode photo bytes to RGB, honoring the EXIF rotation that phones write."""
    image = ImageOps.exif_transpose(Image.open(io.BytesIO(data)))
    return image.convert("RGB")


def resolution_warning(size: tuple[int, int], min_long_side: int = MIN_LONG_SIDE) -> str | None:
    if max(size) >= min_long_side:
        return None
    return (
        f"photo is {size[0]}x{size[1]}px; use at least {min_long_side}px on the long side "
        "for catalog quality (the product is never upscaled)"
    )


def _session(model: str) -> Any:
    session = _sessions.get(model)
    if session is None:
        try:
            import onnxruntime as ort
            from rembg import new_session
        except ImportError as exc:
            raise ImportError(
                "background removal needs the cutout extras: pip install -e '.[cutout]'"
            ) from exc
        options = ort.SessionOptions()
        # Measured with birefnet-dis: without these two settings memory peaked near 14 GB and the
        # process was OOM-killed after a few photos; with them it stays near 7.7 GB, no growth.
        options.enable_cpu_mem_arena = False
        options.enable_mem_pattern = False
        session = _sessions[model] = new_session(model, sess_opts=options)
    return session


def cut_out(image: Image.Image, model: str = DEFAULT_MODEL) -> Image.Image:
    """Return an RGBA image: original pixels plus a predicted alpha mask."""
    session = _session(model)
    from rembg import remove

    return remove(image, session=session).convert("RGBA")


def on_white(cutout: Image.Image, *, margin: float = 0.08, shadow: bool = True) -> Image.Image:
    """Center the product on a square white canvas with a soft shadow (see compose.solid_background)."""
    return solid_background(cutout, (255, 255, 255), margin=margin, shadow=shadow)


def process(
    data: bytes, *, model: str = DEFAULT_MODEL, margin: float = 0.08, shadow: bool = True
) -> CutoutResult:
    image = load_image(data)
    cutout = cut_out(image, model)
    return CutoutResult(
        cutout=cutout,
        white=on_white(cutout, margin=margin, shadow=shadow),
        warning=resolution_warning(image.size),
    )


def to_png(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
