"""Run several prompts through several models on reference photos of ONE piece, and keep every output.

    python -m gold_imagegen.suite --images ring_front.jpg ring_top.jpg \\
        --item ring --brief "A men's signet ring ... square black stone ..." \\
        --roles "Image 1 shows the front of the ring; image 2 shows it from above." \\
        --prompts white_catalog hero_3d --max-cost 2

Writes out/suite/<timestamp>/<prompt>/<model>.png, results.json (prompt, model, cost, time per output)
and index.html. The models REDRAW the piece, so compare every output with the originals.
By default each photo is cropped (not resampled) to a square around the product first.
"""
from __future__ import annotations

import argparse
import asyncio
import html
import json
import shutil
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from . import prompts
from .config import ConfigError, openrouter_api_key
from .providers import EditRequest, ImageEditProvider, OpenRouterProvider, ProviderError

DEFAULT_MODELS = (
    "openai/gpt-image-2.5-sunburst",
    "black-forest-labs/flux-3-image",
    "google/gemini-nano-banana-2.1",
    "bytedance-seed/seedream-5-0-pro",
    "x-ai/grok-imagine-image-2.0",
    "microsoft/mai-image-2.6",
    "meta/muse-image",
)
EXTENSIONS = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}


@dataclass
class SuiteRun:
    prompt_name: str
    model: str
    prompt: str
    ok: bool
    file: str | None = None
    cost_usd: float | None = None
    seconds: float = 0.0
    error: str | None = None
    note: str | None = None


def slug(model: str) -> str:
    return model.replace("/", "__").replace(":", "_")


async def run_suite(
    models: list[str],
    prompt_texts: dict[str, str],
    images: tuple[bytes, ...],
    out_dir: Path,
    make_provider: Callable[[str], ImageEditProvider],
    *,
    max_cost: float,
    concurrency: int = 3,
    aspect_ratio: str | None = "1:1",
    quality: str | None = None,
    aspect_by_prompt: dict[str, str] | None = None,
) -> list[SuiteRun]:
    """One call per (prompt, model). Stops starting new calls once the reported spend reaches max_cost."""
    gate = asyncio.Semaphore(concurrency)
    spent = 0.0

    async def one(name: str, text: str, model: str) -> SuiteRun:
        nonlocal spent
        async with gate:
            if spent >= max_cost:
                return SuiteRun(name, model, text, False, error=f"skipped: budget ${max_cost:.2f} reached")
            provider = make_provider(model)
            note = None
            aspect = (aspect_by_prompt or {}).get(name, aspect_ratio)
            try:
                try:
                    result = await provider.edit(
                        EditRequest(text, images, aspect_ratio=aspect, quality=quality)
                    )
                except ProviderError as exc:
                    if exc.status != 400 or not (aspect or quality):
                        raise
                    note = "aspect_ratio/quality was rejected; retried without them"
                    result = await provider.edit(EditRequest(text, images))
            except ProviderError as exc:
                return SuiteRun(name, model, text, False, error=str(exc), note=note)
            finally:
                await provider.aclose()
            spent += result.cost_usd or 0.0
            target = out_dir / name
            target.mkdir(parents=True, exist_ok=True)
            filename = f"{slug(model)}.{EXTENSIONS.get(result.media_type, 'png')}"
            (target / filename).write_bytes(result.image)
            return SuiteRun(
                name, model, text, True, f"{name}/{filename}", result.cost_usd, round(result.elapsed_s, 1), note=note
            )

    jobs = [one(name, text, model) for name, text in prompt_texts.items() for model in models]
    return list(await asyncio.gather(*jobs))


def write_index(out_dir: Path, inputs: list[str], runs: list[SuiteRun]) -> None:
    esc = html.escape
    sections = []
    for name in dict.fromkeys(r.prompt_name for r in runs):
        group = [r for r in runs if r.prompt_name == name]
        cards = []
        for r in group:
            if r.ok:
                cost = f"${r.cost_usd:.4f}" if r.cost_usd is not None else "cost n/a"
                body, meta = f'<img src="{esc(r.file)}">', f"{cost} &middot; {r.seconds}s"
            else:
                body, meta = f'<p class="err">{esc(r.error or "failed")}</p>', "failed"
            cards.append(f"<figure><figcaption><b>{esc(r.model)}</b><br>{meta}</figcaption>{body}</figure>")
        sections.append(
            f"<h3>{esc(name)}</h3><p><code>{esc(group[0].prompt)}</code></p><div class=row>{''.join(cards)}</div>"
        )
    originals = "".join(f'<figure><figcaption><b>input {i}</b></figcaption><img src="{esc(n)}"></figure>' for i, n in enumerate(inputs, 1))
    (out_dir / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><title>Model suite</title>"
        "<style>body{font:14px system-ui;margin:16px}.row{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:24px}"
        "figure{margin:0;max-width:300px}img{max-width:100%;border:1px solid #ccc}"
        ".err{color:#b00;white-space:pre-wrap;word-break:break-word}code{white-space:pre-wrap}</style>"
        f"<h2>Inputs</h2><div class=row>{originals}</div>{''.join(sections)}",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--images", nargs="+", type=Path, required=True, help="reference photos of the same piece, in order")
    parser.add_argument("--item", default="piece", help='what it is, e.g. "ring"')
    parser.add_argument("--brief", default="", help="what the piece looks like (stones, engraving, metal): it is part of every prompt")
    parser.add_argument("--wearer", default="a man's", help='hand prompts: whose hand, e.g. "a woman\'s"')
    parser.add_argument("--skin", default="natural medium (wheat)", help="hand prompts: skin tone")
    parser.add_argument("--roles", default="", help="what each photo shows, e.g. 'Image 1 is the front view; image 2 is from above.'")
    parser.add_argument("--prompts", nargs="+", choices=prompts.SUITE_NAMES, default=list(prompts.SUITE_NAMES))
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    parser.add_argument("--out", type=Path, default=Path("out/suite"))
    parser.add_argument("--max-cost", type=float, default=1.0, help="stop starting calls after this many USD (default 1.0)")
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--aspect", help="one aspect ratio for every prompt (default: 1:1, or the prompt's own, e.g. 16:9 for hero_banner)")
    parser.add_argument("--quality", help="low|medium|high|auto; sent to every model (retried without it on a 400)")
    parser.add_argument("--no-crop", action="store_true", help="send the photos as they are")
    parser.add_argument("--crop-margin", type=float, default=0.3)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    for path in args.images:
        if not path.is_file():
            parser.error(f"file not found: {path}")
    texts = {
        name: prompts.suite_prompt(
            name, item=args.item, brief=args.brief, roles=args.roles, wearer=args.wearer, skin=args.skin
        )
        for name in args.prompts
    }
    print(f"images: {len(args.images)}  models: {len(args.models)}  prompts: {len(texts)}  max cost: ${args.max_cost:.2f}")
    for name, text in texts.items():
        print(f"\n[{name}]\n{text}")
    if args.dry_run:
        return 0

    try:
        api_key = openrouter_api_key()
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    from . import cutout

    out_dir = args.out / datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    sent, inputs = [], []
    for i, path in enumerate(args.images, 1):
        if args.no_crop:
            data = path.read_bytes()
        else:
            image = cutout.load_image(path.read_bytes())
            data = cutout.to_png(cutout.crop_around_product(image, cutout.cut_out(image), args.crop_margin))
        name = f"input_{i}.png" if not args.no_crop else f"input_{i}{path.suffix.lower()}"
        (out_dir / name).write_bytes(data)
        sent.append(data)
        inputs.append(name)

    runs = asyncio.run(
        run_suite(
            args.models, texts, tuple(sent), out_dir, lambda m: OpenRouterProvider(api_key, m),
            max_cost=args.max_cost, concurrency=args.concurrency, aspect_ratio=args.aspect or None,
            quality=args.quality,
            aspect_by_prompt=None if args.aspect else {n: prompts.SUITE_ASPECTS.get(n, "1:1") for n in texts},
        )
    )
    write_index(out_dir, inputs, runs)
    (out_dir / "results.json").write_text(json.dumps([asdict(r) for r in runs], indent=2), encoding="utf-8")
    for r in runs:
        print(f"- {r.prompt_name:18} {r.model:36} " + (f"ok ${r.cost_usd} {r.seconds}s" if r.ok else f"FAILED {r.error}"))
    print(f"\nreported cost: ${sum(r.cost_usd or 0 for r in runs):.4f}\nopen {out_dir / 'index.html'}")
    return 0 if any(r.ok for r in runs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
