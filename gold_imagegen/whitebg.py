"""Put product photos on a white background locally (no API, product pixels unchanged).

    python -m gold_imagegen.whitebg photo1.jpg photo2.jpg --out out/whitebg
    python -m gold_imagegen.whitebg ring.jpg --model birefnet-dis     # slower, slightly cleaner

Writes <name>_white.png and <name>_cutout.png (transparent) per photo. Needs `pip install -e ".[cutout]"`.
The model weights download on first use. The model loads once and is reused across photos.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import cutout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("photos", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out/whitebg"))
    parser.add_argument(
        "--model",
        default=cutout.DEFAULT_MODEL,
        help=f"rembg model (default {cutout.DEFAULT_MODEL}; best quality: {cutout.QUALITY_MODEL})",
    )
    parser.add_argument("--margin", type=float, default=0.08, help="white border as a fraction of the canvas")
    parser.add_argument("--no-shadow", action="store_true")
    args = parser.parse_args(argv)

    args.out.mkdir(parents=True, exist_ok=True)
    failed = 0
    for path in args.photos:
        try:
            result = cutout.process(
                path.read_bytes(), model=args.model, margin=args.margin, shadow=not args.no_shadow
            )
        except (OSError, ValueError, ImportError) as exc:
            print(f"{path.name}: FAILED {exc}", file=sys.stderr)
            failed += 1
            continue
        (args.out / f"{path.stem}_white.png").write_bytes(cutout.to_png(result.white))
        (args.out / f"{path.stem}_cutout.png").write_bytes(cutout.to_png(result.cutout))
        print(f"{path.name}: ok" + (f"  WARNING: {result.warning}" if result.warning else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
