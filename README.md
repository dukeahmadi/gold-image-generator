# gold-image-generator

Edit jewelry product photos:

- **white background** — product photo -> clean catalog shot
- **on model** — product photo + person photo -> the jewelry worn on the neck / finger / ears / wrist

Accuracy of the product comes first (a customer must see the piece that is sold), so there are two kinds of
pipeline:

- **Pixel-preserving** (`gold_imagegen.cutout`): a segmentation model only predicts a mask; the original product
  pixels are placed on white unchanged. Local, free, no API.
- **Generative** (OpenRouter models): the model redraws the whole image, so stones, engraving or metal color can
  drift. Useful for on-model shots; compare it against the original before trusting it.

Status: provider layer, model comparison tool and local white-background cutout. The Telegram bot (aiogram) is
postponed until the pipeline is chosen.

## Setup

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev,cutout]"   # "cutout" adds rembg + onnxruntime; omit it if you only use the API models
cp .env.example .env             # then put your OPENROUTER_API_KEY in .env (never commit it)
pytest
```

## White background without a generative model

```bash
python -m gold_imagegen.whitebg photo1.jpg photo2.jpg --out out/whitebg
python -m gold_imagegen.whitebg ring.jpg --model birefnet-dis        # slower, slightly cleaner
```

Writes `<name>_white.png` (square canvas, soft shadow, product pixels untouched and never upscaled) and
`<name>_cutout.png` (transparent). Weights download on first use. The model loads once per run.

Measured on a 16 GB CPU container with six small web photos (wall time includes the one-time model load):

| model | weights | per photo | peak RAM |
|---|---|---|---|
| `birefnet-general-lite` (default) | 214 MB | ~23 s | 6.6 GB |
| `birefnet-dis` | 928 MB | ~37 s | 7.7 GB |

The ONNX session is created with `enable_cpu_mem_arena=False` and `enable_mem_pattern=False`. Without them
`birefnet-dis` peaked near 14 GB and was OOM-killed after a few photos in one process. A bot server needs a GPU, a
lot of RAM, or a hosted background-removal API.

Known limits (all seen on real photos):

- Thin chains over skin keep skin-tinted edge pixels: a silver chain turned rose-gold. A foreground-color
  re-estimation pass (`pymatting`) did not fix it. Ask customers for a plain surface, not a hand.
- A product held between fingers (ring) is not separated from the fingers.
- Photos below ~1500 px on the long side trigger a warning (`MIN_LONG_SIDE`, a heuristic to tune on real photos);
  the six test photos were 174-668 px, too small to judge final quality.
- A product cut off by the photo frame stays cut off. A faint pale fringe remains along some edges, and stray bits
  of fingers can remain.

## Generative models (OpenRouter)

```bash
python -m gold_imagegen.list_models          # editable models + price per 1M image-output tokens (no key needed)

# put your own photos under samples/ (git-ignored)
python -m gold_imagegen.compare --task white_background --product samples/ring.jpg --local-cutout
python -m gold_imagegen.compare --task on_model --jewelry necklace \
    --product samples/necklace.jpg --model-photo samples/neck.jpg
```

Open `out/<timestamp>/index.html` to compare the results side by side. Each run records the cost OpenRouter
reports. `--max-cost` (default `1.0` USD) stops the run once that much has been spent; `--models a/b,c/d` picks the
models; `--local-cutout` adds the free local baseline (white background only); `--dry-run` prints the plan without
calling anything.

Judge the results on the details that matter for jewelry: shape, engraving, stones, color and finish must match the
original photo. Zoom in on the stones.

## Layout

```
gold_imagegen/
  cutout.py        local background removal + white canvas (pixel-preserving)
  whitebg.py       CLI for the above
  providers/       ImageEditProvider interface, OpenRouter and local-cutout implementations
  prompts.py       edit prompts (white background, on-model per jewelry type)
  compare.py       run one edit through several models, write a contact sheet
  list_models.py
tests/
```
