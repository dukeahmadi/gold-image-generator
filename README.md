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

Status: provider layer, model comparison tool, local cutout and the pixel-preserving image pipelines (white, solid
color, multi-piece set, studio scene, accessories, compatible displays; see [docs/pipelines.md](docs/pipelines.md)).
The Telegram bot (aiogram) is postponed until the pipelines are chosen.

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

## Image pipelines

```bash
python -m gold_imagegen.render photo1.jpg photo2.jpg --types white solid set --colors navy black --reflection
python -m gold_imagegen.make_plates --kind scene --style white_marble --count 4 --out plates   # needs the API key
python -m gold_imagegen.render photo1.jpg --types scene accessories display --plates plates
```

The product's pixels are never redrawn; models only paint empty background plates, once, for human review.
Details, prompts, risks and what has (and has not) been tested: [docs/pipelines.md](docs/pipelines.md).
A set takes its resolution from the lowest-resolution photo, since nothing is enlarged.

## Reference-photo edits across models (suite)

```bash
python -m gold_imagegen.suite --images front.jpg top.jpg --item ring \
    --brief "A men's signet ring ... square black stone ..." \
    --roles "Image 1 is the front view; image 2 is from above." --max-cost 2
```

Runs several prompts (white catalog, navy luxury, marble, silk with petals, ring cushion, jewelry box, 3D hero, and four
hand poses: `hand_flat`, `hand_fist`, `hand_resting`, `hand_raised`; `--wearer` and `--skin` set whose hand) on
several models with the same reference photos and keeps every output with its prompt, model, cost and time. These
models redraw the piece, so compare each output zoomed in against the photos. First real run:
[docs/ring-test-report.md](docs/ring-test-report.md) and
[docs/ring-hand-test-report.md](docs/ring-hand-test-report.md).

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
  compose.py       solid backgrounds, reflection, vignette, multi-piece sets
  plates.py        background plates (slot, light, occlusion) and placing a product on them
  render.py        run the pixel-preserving pipelines on photos
  suite.py         several prompts x several models on reference photos of one piece
  make_plates.py   generate plates with an image model, for human review
  whitebg.py       CLI: white background only
  providers/       ImageEditProvider interface, OpenRouter and local-cutout implementations
  prompts.py       plate prompts and (dormant) on-model edit prompts
docs/pipelines.md  what each image type does, its prompts, risks and test status
  compare.py       run one edit through several models, write a contact sheet
  list_models.py
tests/
```
