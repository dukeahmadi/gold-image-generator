"""Generate background plates with an image model, once, for human review. Needs OPENROUTER_API_KEY.

    python -m gold_imagegen.make_plates --kind scene --style white_marble --count 4 --out plates
    python -m gold_imagegen.make_plates --kind accessories --style silk --props roses --count 3 --out plates
    python -m gold_imagegen.make_plates --kind display_ring --count 3 --out plates

Look at every plate before using it; delete the bad ones. Plates are reused for every product, so the
model cost is paid once. A plate must not contain jewelry: the product pixels are added afterwards.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from collections.abc import Callable
from pathlib import Path

from . import plates, prompts
from .config import ConfigError, openrouter_api_key
from .providers import EditRequest, ImageEditProvider, OpenRouterProvider, ProviderError

DEFAULT_MODEL = "black-forest-labs/flux-3-image"


async def generate_plates(
    make_provider: Callable[[], ImageEditProvider],
    *,
    kind: str,
    style: str,
    props: str | None,
    count: int,
    out_dir: Path,
    max_cost: float,
    aspect_ratio: str | None = None,
) -> tuple[list[Path], float, list[str]]:
    """Returns (written plate JSON paths, reported cost in USD, error messages)."""
    prompt = prompts.plate_prompt(kind, style, props)
    label = kind if kind in prompts.DISPLAY_SUBJECTS else f"{kind}_{style}" + (f"_{props}" if props else "")
    written: list[Path] = []
    errors: list[str] = []
    spent = 0.0
    start = len(list(out_dir.glob(f"{label}_*.json"))) + 1 if out_dir.exists() else 1
    for i in range(count):
        if spent >= max_cost:
            errors.append(f"stopped: budget ${max_cost:.2f} reached")
            break
        provider = make_provider()
        try:
            result = await provider.edit(EditRequest(prompt=prompt, aspect_ratio=aspect_ratio))
        except ProviderError as exc:
            errors.append(str(exc))
            continue
        finally:
            await provider.aclose()
        spent += result.cost_usd or 0.0
        generation = {
            "model": result.model,
            "prompt": prompt,
            "cost_usd": result.cost_usd,
            "seconds": round(result.elapsed_s, 1),
        }
        written.append(
            plates.write_plate(out_dir, f"{label}_{start + i:02d}", result.image, kind, generation=generation)
        )
    return written, spent, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kind", required=True, choices=prompts.PLATE_KINDS)
    parser.add_argument("--style", default="white_marble", choices=sorted(prompts.STUDIO_SURFACES))
    parser.add_argument("--props", choices=sorted(prompts.ACCESSORY_PROPS), help="accessories kind only")
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--aspect", default="1:1", help='aspect ratio sent to the model (default "1:1")')
    parser.add_argument("--no-aspect", action="store_true", help="do not send an aspect ratio (not every model accepts it)")
    parser.add_argument("--out", type=Path, default=Path("plates"))
    parser.add_argument("--max-cost", type=float, default=0.5, help="stop after this many USD (default 0.5)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    prompt = prompts.plate_prompt(args.kind, args.style, args.props)
    print(f"model: {args.model}\ncount: {args.count}  max cost: ${args.max_cost:.2f}\nprompt: {prompt}")
    if args.dry_run:
        return 0
    try:
        api_key = openrouter_api_key()
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    written, spent, errors = asyncio.run(
        generate_plates(
            lambda: OpenRouterProvider(api_key, args.model),
            kind=args.kind, style=args.style, props=args.props, count=args.count,
            out_dir=args.out, max_cost=args.max_cost,
            aspect_ratio=None if args.no_aspect else args.aspect,
        )
    )
    for path in written:
        print(f"wrote {path}")
    for message in errors:
        print(f"error: {message}", file=sys.stderr)
    print(f"reported cost: ${spent:.4f}. Review the images before using them.")
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())
