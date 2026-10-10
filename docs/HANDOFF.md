# Handoff: where the project stands (2026-10-10)

Read this first in a new session. Everything below is already in the repo (branch `claude/scaffold-provider-layer`).

## Decisions made by the owner

- Product: jewelry photo tool for the owner's own website (not a Telegram bot for now). First product: rings.
- **Fidelity comes first**: the product must not change (an eagle must never become a snake). Pixel-preserving pipelines
  (`render.py`: white, solid color, set, scene, accessories, display) exist for the "exact" mode.
- **Model: `bytedance-seed/seedream-5-0-pro`** via OpenRouter (`POST /api/v1/images`, reference photos as
  `input_references` of `{"type": "image_url", "image_url": {"url": <data URL>}}`). See `docs/model-choice.md` for why and what it costs.
- 29 presets for rings in 6 groups: `docs/presets.md` (`python -m gold_imagegen.presets`). Chosen by the owner:
  white, macro of stone and ornament, next to a coin or ruler, three man's hand poses, a woman's hand with manicure and
  flower, an engagement couple set, in a box, an open box held in a hand (proposal), studio scenes, six Iranian
  backgrounds and five occasions (Nowruz, Yalda, Sepandarmazgan, Mother's/Father's Day).

## Test product

Two photos of one men's signet ring (front view; view from above/side). They are not in git; ask the owner to send
them again. Use this brief and these roles (they are part of every prompt):

**Brief:** A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom.

**Roles:** Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible.

## Pending

1. **Run the 17 new presets with Seedream** (never run yet; about $1.6). The OpenRouter balance was $0.51 and Seedream
   refuses calls (HTTP 402) below roughly $0.65-0.7 of balance, so the account needs credit first:

```bash
python -m gold_imagegen.suite --images ring_front.jpg ring_top.jpg --item ring \
  --brief "<brief above>" --roles "<roles above>" \
  --prompts macro_stone macro_ornament coin_scale ruler_scale woman_hand_flowers proposal_box \
            persian_tile persian_rug copper_tray hafez_book tea_nabat pomegranate_saffron \
            nowruz yalda sepandarmazgan mothers_day fathers_day \
  --models bytedance-seed/seedream-5-0-pro --max-cost 1.8 --concurrency 3
```

   Check the balance first: `GET https://openrouter.ai/api/v1/credits` (`total_credits - total_usage`).
2. `couple_rings_set` needs photos of two rings; `woman_hand_flowers` and the Father's/Mother's Day scenes need a
   fitting ring (the test ring is a men's signet).
3. Not yet run with Seedream: `macro_closeup`, `turntable_sheet`, `hand_luxury`.
4. Biggest open risk: the engraving changes from image to image. Ideas: a close-up of the ornament as a third
   reference photo, a post-check against the original, extra views. Also untested: a ring with an animal motif or
   Persian/Arabic text.
5. The website form (`ring` form: basics, design card, 3 photos + optional close-up, outputs, consent) is designed
   in chat only; a clickable prototype has not been built.

## Money so far

OpenRouter usage $4.4894 of $5 (every call is recorded in `docs/*report*.md`; the ledger matched the account to the
last decimal). Costs per 1024-2048 px image: Seedream $0.093 (16:9: $0.048), Sunburst $0.03 ($0.07 at quality high),
MAI $0.044, FLUX.3 $0.048, Grok $0.08.

## Secrets

The OpenRouter key was pasted in chat once; it should be rotated. Never put a key in chat or git: set
`OPENROUTER_API_KEY` in the environment (it is read only when a session starts).
