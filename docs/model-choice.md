# Model choice for ring edits (2026-10-09)

One ring (two photos), 7 scenes + 4 hand poses on 6 models, then a premium round (Sunburst `quality=high`, Flare `high`,
Nano Banana Pro). Judged by looking at the ring face (stone shape, halo of small stones, shoulder ornament, metal) next
to the original photo. **One ring and one run per prompt: this is a visual judgement, not a statistical result.**

## Verdict

**`openai/gpt-image-2.5-sunburst` with `quality=high`** is the most faithful to the original in the front-view
comparison, and it is also cheap ($0.07 per image at high quality, $0.03 at the default) and succeeded on every call.

| rank | model | what it did to the design |
|---|---|---|
| 1 | GPT Image 2.5 Sunburst (high) | flat, nearly square black stone in a thin gold frame, halo of dark stones with a beaded edge, delicate scroll panels, matte bronze patina |
| 2 | GPT Image 2.5 Flare (high) | close to Sunburst; slightly simpler ornament |
| 3 | MAI Image 2.6 | good look, but the stone is chamfered/taller and the shoulder ornament is leafy rather than scrolled |
| 4 | Seedream 5.0 Pro | very detailed, but the shoulder relief is bolder than the original and the ring chunkier |
| 5 | Grok Imagine 2.0 | plausible; stone proportion and ornament drift |
| 6 | Nano Banana Pro / 2.1 | Pro invented a bold arabesque ornament and grey halo stones; 2.1 was blocked by a Google quota error 13 times before working |
| 7 | FLUX.3 | domed glossy stone, thin band, brassy color |

## Color is not a differentiator

Median color of the segmented ring (black stone and glare excluded), averaged over white catalog, marble and 3D hero:

| | L* | chroma | hue | hue shift | chroma gain |
|---|---|---|---|---|---|
| original photos | 29.7 | 16.2 | 59 | | |
| MAI | 43.7 | 24.9 | 65 | 5.7 | +8.7 |
| Seedream | 43.9 | 20.5 | 66 | 7.4 | +4.3 |
| Grok | 46.4 | 24.3 | 66 | 7.5 | +8.1 |
| Sunburst | 45.1 | 25.5 | 67 | 7.7 | +9.3 |
| FLUX | 42.1 | 17.6 | 67 | 8.1 | +1.4 |

Every model draws the bronze brighter, more saturated and a little more yellow than the dim original photo. Part of that
is the photo's own dull lighting, so the measurement is crude.

## Cost per image (1024x1024)

Sunburst $0.023-0.030 default, $0.070 high; Flare high $0.070; MAI $0.044; FLUX $0.048; Nano Banana 2.1 $0.04; Nano
Banana Pro $0.137; Grok $0.080; Seedream $0.093. Account usage after all runs: $4.0694.

## Not tested yet (decides the final choice)

- A ring with a **figurative motif** (an eagle, a lion) or **Arabic/Persian text**: the failure the product must avoid
  (an eagle turned into a snake). The current ring has only ornament.
- A thin women's ring with many small stones.
- Hands: in `hand_flat` Sunburst's ring looked small for the finger (not measured).
