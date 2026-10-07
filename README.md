# gold-image-generator

Edit gold jewelry product photos with image models:

- **white background** — product photo -> clean catalog shot
- **on model** — product photo + person photo -> the jewelry worn on the neck / finger / ears / wrist

Models are called through [OpenRouter](https://openrouter.ai), so one API key reaches GPT Image 2.5,
FLUX.3, Nano Banana, Seedream and others. Switching model = changing a model id.

Status: provider layer + model comparison tool. The Telegram bot (aiogram) comes after a model is chosen.

## Setup

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env      # then put your OPENROUTER_API_KEY in .env (never commit it)
pytest
```

## Choose a model

```bash
python -m gold_imagegen.list_models          # editable models + price per 1M image-output tokens (no key needed)

# put your own photos under samples/ (git-ignored)
python -m gold_imagegen.compare --task white_background --product samples/ring.jpg
python -m gold_imagegen.compare --task on_model --jewelry necklace \
    --product samples/necklace.jpg --model-photo samples/neck.jpg
```

Open `out/<timestamp>/index.html` to compare the results side by side. Each run records the cost
OpenRouter reports. `--max-cost` (default `1.0` USD) stops the run once that much has been spent;
`--models a/b,c/d` picks the models and `--dry-run` prints the plan without calling anything.

Judge the results on the details that matter for gold: shape, engraving, stones, color and finish
must match the original photo. A generative model can subtly change them; for plain white
backgrounds a background-removal + composite step keeps the original pixels exactly.

## Layout

```
gold_imagegen/
  providers/    ImageEditProvider interface + OpenRouter implementation
  prompts.py    edit prompts (white background, on-model per jewelry type)
  compare.py    run one edit through several models, write a contact sheet
  list_models.py
tests/
```
