"""Run the same edit through several models and write a side-by-side contact sheet.

    # product photo -> white background
    python -m gold_imagegen.compare --task white_background --product samples/ring.jpg
    python -m gold_imagegen.compare --task white_background --product samples/ring.jpg --local-cutout

    # product photo + model photo -> jewelry worn by the model
    python -m gold_imagegen.compare --task on_model --jewelry necklace \\
        --product samples/necklace.jpg --model-photo samples/neck.jpg

Output goes to out/<timestamp>/ (index.html, results.json, one image per model).
`--max-cost` stops the run once the reported spend reaches that many USD.
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
)
LOCAL_CUTOUT = "local/cutout"  # or local/cutout:<rembg model>; white_background only, no API call
EXTENSIONS = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}


@dataclass
class ModelRun:
    model: str
    ok: bool
    file: str | None = None
    cost_usd: float | None = None
    seconds: float = 0.0
    error: str | None = None


def slug(model: str) -> str:
    return model.replace("/", "__").replace(":", "_")


def is_local(model: str) -> bool:
    return model.startswith(LOCAL_CUTOUT)


def make_provider(api_key: str | None, model: str) -> ImageEditProvider:
    if is_local(model):
        from .providers.local_cutout import LocalCutoutProvider  # needs the cutout extras

        return LocalCutoutProvider(model.partition(":")[2] or None)
    if api_key is None:
        raise ConfigError("an API key is required for non-local models")
    return OpenRouterProvider(api_key, model)


async def run_comparison(
    models: list[str],
    request: EditRequest,
    out_dir: Path,
    make_provider: Callable[[str], ImageEditProvider],
    max_cost: float,
) -> list[ModelRun]:
    out_dir.mkdir(parents=True, exist_ok=True)
    spent = 0.0
    runs: list[ModelRun] = []
    for model in models:
        if spent >= max_cost:
            runs.append(
                ModelRun(model, False, error=f"skipped: budget ${max_cost:.2f} reached")
            )
            continue
        provider = make_provider(model)
        try:
            result = await provider.edit(request)
        except ProviderError as exc:
            runs.append(ModelRun(model, False, error=str(exc)))
            continue
        finally:
            await provider.aclose()
        ext = EXTENSIONS.get(result.media_type, "png")
        filename = f"{slug(model)}.{ext}"
        (out_dir / filename).write_bytes(result.image)
        if result.cost_usd is not None:
            spent += result.cost_usd
        runs.append(
            ModelRun(model, True, filename, result.cost_usd, round(result.elapsed_s, 1))
        )
    return runs


def write_index(out_dir: Path, task: str, prompt: str, inputs: list[str], runs: list[ModelRun]) -> None:
    esc = html.escape
    cards = []
    for run in runs:
        if run.ok:
            cost = f"${run.cost_usd:.4f}" if run.cost_usd is not None else "cost n/a"
            body = f'<img src="{esc(run.file)}">'
            meta = f"{cost} &middot; {run.seconds}s"
        else:
            body = f'<p class="err">{esc(run.error or "failed")}</p>'
            meta = "failed"
        cards.append(
            f"<figure><figcaption><b>{esc(run.model)}</b><br>{meta}</figcaption>{body}</figure>"
        )
    originals = "".join(
        f'<figure><figcaption><b>input {i}</b></figcaption><img src="{esc(name)}"></figure>'
        for i, name in enumerate(inputs, 1)
    )
    (out_dir / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><title>Model comparison</title>"
        "<style>body{font:14px system-ui;margin:16px}"
        ".row{display:flex;flex-wrap:wrap;gap:16px;margin-bottom:24px}"
        "figure{margin:0;max-width:340px}img{max-width:100%;border:1px solid #ccc}"
        ".err{color:#b00;white-space:pre-wrap;word-break:break-word}</style>"
        f"<h2>{esc(task)}</h2><p><code>{esc(prompt)}</code></p>"
        f'<div class="row">{originals}</div><div class="row">{"".join(cards)}</div>',
        encoding="utf-8",
    )


def _copy_inputs(paths: list[Path], out_dir: Path) -> list[str]:
    names = []
    for i, path in enumerate(paths, 1):
        name = f"input_{i}{path.suffix.lower() or '.jpg'}"
        shutil.copyfile(path, out_dir / name)
        names.append(name)
    return names


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--task", choices=("white_background", "on_model"), required=True)
    parser.add_argument("--product", type=Path, required=True, help="product (jewelry) photo")
    parser.add_argument("--model-photo", type=Path, help="person photo (on_model only)")
    parser.add_argument("--jewelry", default="necklace", choices=sorted(prompts.PLACEMENT))
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS), help="comma-separated OpenRouter model ids")
    parser.add_argument(
        "--local-cutout", action="store_true",
        help="also run the local background-removal baseline (white_background only, free)",
    )
    parser.add_argument("--out", type=Path, default=Path("out"))
    parser.add_argument("--max-cost", type=float, default=1.0, help="stop after this many USD (default 1.0)")
    parser.add_argument("--quality", help="pass-through quality (low|medium|high|auto); not all models accept it")
    parser.add_argument("--dry-run", action="store_true", help="print the plan, call nothing")
    args = parser.parse_args(argv)

    if args.task == "on_model" and not args.model_photo:
        parser.error("--model-photo is required for --task on_model")
    input_paths = [args.product] + ([args.model_photo] if args.task == "on_model" else [])
    for path in input_paths:
        if not path.is_file():
            parser.error(f"file not found: {path}")

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if args.local_cutout and LOCAL_CUTOUT not in models:
        models.append(LOCAL_CUTOUT)
    if args.task != "white_background" and any(is_local(m) for m in models):
        parser.error("local/cutout only supports --task white_background")
    prompt = (
        prompts.white_background()
        if args.task == "white_background"
        else prompts.on_model(args.jewelry)
    )
    print(f"task: {args.task}\nmodels: {', '.join(models)}\nmax cost: ${args.max_cost:.2f}\nprompt: {prompt}")
    if args.dry_run:
        return 0

    api_key = None
    if not all(is_local(m) for m in models):
        try:
            api_key = openrouter_api_key()
        except ConfigError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    out_dir = args.out / datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    request = EditRequest(
        prompt=prompt,
        images=tuple(p.read_bytes() for p in input_paths),
        quality=args.quality,
    )
    runs = asyncio.run(
        run_comparison(
            models, request, out_dir,
            lambda model: make_provider(api_key, model),
            args.max_cost,
        )
    )
    write_index(out_dir, args.task, prompt, _copy_inputs(input_paths, out_dir), runs)
    (out_dir / "results.json").write_text(
        json.dumps([asdict(r) for r in runs], indent=2), encoding="utf-8"
    )

    for run in runs:
        status = f"ok ${run.cost_usd}" if run.ok else f"FAILED {run.error}"
        print(f"- {run.model}: {status}")
    total = sum(r.cost_usd or 0 for r in runs)
    print(f"\nreported cost: ${total:.4f}\nopen {out_dir / 'index.html'}")
    return 0 if any(r.ok for r in runs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
