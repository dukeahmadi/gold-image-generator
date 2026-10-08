"""Background plates: an image plus where the product goes and where the light comes from.

A plate is stored as `<name>.png` + `<name>.json`:

    {"image": "marble_01.png", "kind": "scene",
     "slot": [0.18, 0.18, 0.64, 0.64],     # x, y, w, h as fractions of the image
     "light": [1, 1],                       # direction shadows fall (x right, y down)
     "anchor": "center",                    # where the product sits in the slot: center, top or bottom
     "occlude_below": null}                 # fraction of image height; product pixels below are hidden

`anchor` is "bottom" for a ring standing in a cushion and "top" for earrings hanging from a card.
`occlude_below` is for cushions and boxes: the product's lower part is hidden behind the plate's own
pixels (e.g. a ring standing in a slit). Set it by hand after looking at the plate.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .compose import DARK_SHADOW_OPACITY, SHADOW_OPACITY, luminance, shadow_layer, trim
from .prompts import PLATE_KINDS

DEFAULT_SLOTS = {
    "scene": (0.18, 0.18, 0.64, 0.64),
    "accessories": (0.22, 0.22, 0.56, 0.56),
    "display_ring": (0.30, 0.10, 0.40, 0.55),
    "display_earrings": (0.25, 0.10, 0.50, 0.70),
    "display_box": (0.20, 0.20, 0.60, 0.60),
}
ANCHORS = ("center", "top", "bottom")
DEFAULT_ANCHORS = {"display_ring": "bottom", "display_earrings": "top"}
DEFAULT_LIGHT = (1.0, 1.0)  # matches "light from the upper left" in the plate prompts


@dataclass(frozen=True)
class Plate:
    image: Image.Image
    kind: str = "scene"
    slot: tuple[float, float, float, float] = DEFAULT_SLOTS["scene"]
    light: tuple[float, float] = DEFAULT_LIGHT
    occlude_below: float | None = None
    name: str = ""
    anchor: str = "center"


def _validate(kind: str, slot, light, occlude_below, anchor: str = "center") -> None:
    if anchor not in ANCHORS:
        raise ValueError(f"unknown anchor {anchor!r}; choose one of {list(ANCHORS)}")
    if kind not in PLATE_KINDS:
        raise ValueError(f"unknown plate kind {kind!r}; choose one of {list(PLATE_KINDS)}")
    x, y, w, h = slot
    if not (0 <= x < 1 and 0 <= y < 1 and 0 < w <= 1 and 0 < h <= 1 and x + w <= 1 and y + h <= 1):
        raise ValueError(f"slot {slot} must lie inside the image (fractions of its size)")
    if light == (0, 0):
        raise ValueError("light direction cannot be (0, 0)")
    if occlude_below is not None and not 0 < occlude_below < 1:
        raise ValueError("occlude_below must be a fraction between 0 and 1")


def load_plate(json_path: Path) -> Plate:
    meta = json.loads(json_path.read_text(encoding="utf-8"))
    kind = meta.get("kind", "scene")
    slot = tuple(meta.get("slot", DEFAULT_SLOTS.get(kind, DEFAULT_SLOTS["scene"])))
    light = tuple(meta.get("light", DEFAULT_LIGHT))
    occlude_below = meta.get("occlude_below")
    anchor = meta.get("anchor", DEFAULT_ANCHORS.get(kind, "center"))
    _validate(kind, slot, light, occlude_below, anchor)
    image = Image.open(json_path.parent / meta["image"]).convert("RGB")
    return Plate(image, kind, slot, light, occlude_below, json_path.stem, anchor)  # type: ignore[arg-type]


def iter_plates(directory: Path, kinds: tuple[str, ...] | None = None) -> list[Plate]:
    plates = [load_plate(p) for p in sorted(directory.glob("*.json"))]
    return [p for p in plates if kinds is None or p.kind in kinds]


def write_plate(
    directory: Path, name: str, image_bytes: bytes, kind: str, light=DEFAULT_LIGHT,
    generation: dict | None = None,
) -> Path:
    """Save a generated plate with default metadata; edit the JSON by hand if the slot needs moving.

    `generation` (model, prompt, cost, seconds) is stored alongside so every plate stays auditable."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{name}.png").write_bytes(image_bytes)
    meta = {
        "image": f"{name}.png",
        "kind": kind,
        "slot": list(DEFAULT_SLOTS[kind]),
        "light": list(light),
        "anchor": DEFAULT_ANCHORS.get(kind, "center"),
        "occlude_below": None,
    }
    if generation:
        meta["generation"] = generation
    path = directory / f"{name}.json"
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return path


def place_on_plate(cutout: Image.Image, plate: Plate, *, shadow: bool = True) -> Image.Image:
    """Put the product into the plate's slot. Product pixels are copied; shrunk only if too big for the slot."""
    product = trim(cutout)
    width, height = plate.image.size
    sx, sy, sw, sh = plate.slot
    slot_x, slot_y, slot_w, slot_h = round(sx * width), round(sy * height), round(sw * width), round(sh * height)

    scale = min(1.0, slot_w / product.width, slot_h / product.height)
    if scale < 1.0:
        product = product.resize(
            (max(1, round(product.width * scale)), max(1, round(product.height * scale))), Image.LANCZOS
        )
    x = slot_x + (slot_w - product.width) // 2
    if plate.anchor == "top":
        y = slot_y
    elif plate.anchor == "bottom":
        y = slot_y + slot_h - product.height
    else:
        y = slot_y + (slot_h - product.height) // 2

    if plate.occlude_below is not None:
        cut = round(plate.occlude_below * height) - y
        if cut <= 0:
            raise ValueError("occlude_below hides the whole product; move the slot or the line")
        if cut < product.height:
            alpha = product.getchannel("A")
            alpha.paste(0, (0, cut, product.width, product.height))
            product = product.copy()
            product.putalpha(alpha)

    canvas = plate.image.convert("RGBA")
    if shadow:
        blur = max(2.0, width * 0.008)
        lx, ly = plate.light
        norm = math.hypot(lx, ly)
        offset = (round(lx / norm * blur * 1.6), round(ly / norm * blur * 1.6))
        mean = plate.image.resize((1, 1)).getpixel((0, 0))
        opacity = DARK_SHADOW_OPACITY if luminance(mean) < 0.35 else SHADOW_OPACITY
        canvas.alpha_composite(
            shadow_layer(product.getchannel("A"), canvas.size, (x, y), blur=blur, offset=offset, opacity=opacity)
        )
    canvas.alpha_composite(product, (x, y))
    return canvas.convert("RGB")
