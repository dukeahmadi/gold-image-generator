"""Run the image pipelines on product photos.

    python -m gold_imagegen.render photo1.jpg photo2.jpg --types white solid set
    python -m gold_imagegen.render ring.jpg --types scene accessories display --plates plates

Types (all keep the product pixels unchanged; see docs/pipelines.md):
  white        white catalog image
  solid        one image per --colors entry (preset name or hex), optional reflection
  set          all photos together as one multi-piece set, per --colors entry
  scene        product on studio background plates        (plates of kind "scene")
  accessories  product on plates with props               (plates of kind "accessories")
  display      product on compatible display plates       (plates of kind "display_*")

Each photo is cut out once and reused for every type. Needs `pip install -e ".[cutout]"`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

from . import compose, cutout, plates

TYPES = ("white", "solid", "set", "scene", "accessories", "display")
DEFAULT_COLORS = ("navy", "black", "beige")
PLATE_KINDS_FOR = {"scene": ("scene",), "accessories": ("accessories",), "display": (
    "display_ring", "display_earrings", "display_box")}


def _background_kwargs(color: tuple[int, int, int], reflection: bool) -> dict:
    dark = compose.luminance(color) < 0.35
    return {"vignette": 0.25 if dark else 0.0, "reflection": reflection and dark}


def render_all(
    cutouts: dict[str, Image.Image],
    types: list[str],
    *,
    colors: list[str],
    reflection: bool = False,
    weights: list[float] | None = None,
    plate_dir: Path | None = None,
) -> dict[str, Image.Image]:
    """Returns {output file name: RGB image}. `cutouts` maps a photo stem to its RGBA cutout."""
    outputs: dict[str, Image.Image] = {}
    if "white" in types:
        for stem, cut in cutouts.items():
            outputs[f"{stem}_white.png"] = cutout.on_white(cut)
    if "solid" in types:
        for name in colors:
            color = compose.parse_color(name)
            for stem, cut in cutouts.items():
                outputs[f"{stem}_solid-{name.lstrip('#')}.png"] = compose.solid_background(
                    cut, color, **_background_kwargs(color, reflection)
                )
    if "set" in types:
        for name in colors:
            color = compose.parse_color(name)
            outputs[f"set_{name.lstrip('#')}.png"] = compose.set_layout(
                list(cutouts.values()), color, weights=weights, vignette=_background_kwargs(color, False)["vignette"]
            )
    for plate_type in ("scene", "accessories", "display"):
        if plate_type not in types:
            continue
        if plate_dir is None:
            raise ValueError(f"--plates is required for type {plate_type!r}")
        found = plates.iter_plates(plate_dir, PLATE_KINDS_FOR[plate_type])
        if not found:
            raise ValueError(f"no plates of kind {PLATE_KINDS_FOR[plate_type]} in {plate_dir}")
        for plate in found:
            for stem, cut in cutouts.items():
                outputs[f"{stem}_{plate.name}.png"] = plates.place_on_plate(cut, plate)
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("photos", nargs="+", type=Path)
    parser.add_argument("--types", nargs="+", choices=TYPES, default=["white"])
    parser.add_argument("--colors", nargs="+", default=list(DEFAULT_COLORS),
                        help=f"presets {sorted(compose.PRESETS)} or hex codes (default: {' '.join(DEFAULT_COLORS)})")
    parser.add_argument("--reflection", action="store_true", help="glossy-floor reflection on dark solid backgrounds")
    parser.add_argument("--weights", nargs="+", type=float, help="set only: size factor in (0, 1] per photo, in order")
    parser.add_argument("--plates", type=Path, help="directory of plates (scene/accessories/display)")
    parser.add_argument("--model", default=cutout.DEFAULT_MODEL, help="rembg model for the cutout")
    parser.add_argument("--out", type=Path, default=Path("out/render"))
    args = parser.parse_args(argv)

    try:
        for name in args.colors:
            compose.parse_color(name)
        cutouts = {}
        for path in args.photos:
            result = cutout.load_image(path.read_bytes())
            warning = cutout.resolution_warning(result.size)
            print(f"{path.name}: cutting out" + (f"  WARNING: {warning}" if warning else ""))
            cutouts[path.stem] = cutout.cut_out(result, args.model)
        outputs = render_all(
            cutouts, args.types, colors=args.colors, reflection=args.reflection,
            weights=args.weights, plate_dir=args.plates,
        )
    except (OSError, ValueError, ImportError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    for name, image in outputs.items():
        (args.out / name).write_bytes(cutout.to_png(image))
        print(f"wrote {args.out / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
