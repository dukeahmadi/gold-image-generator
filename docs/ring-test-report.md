# Ring test: reference-photo edits across models (2026-10-09)

Two real photos of one ring (front view; view from above/side with the inside of the band) were cropped to a
square around the ring (crop only, no resampling), sent as `input_references` together with each prompt, and run
through several models via OpenRouter `POST /api/v1/images` at `aspect_ratio` `1:1`. The models redraw the whole
piece, so **every output differs from the photos in small ways**; compare each one zoomed in before using it.

## Inputs sent with every prompt

**Design brief** (written by hand from the photos; it is part of each prompt):

> A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom.

**Image roles:**

> Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible.

## Cost

| model | white_catalog | solid_navy | studio_marble | accessories_silk | display_cushion | display_box | hero_3d | total |
|---|---|---|---|---|---|---|---|---|
| `openai/gpt-image-2.5-sunburst` | $0.0229 / 17.8 s | $0.0302 / 17.2 s | $0.0301 / 20.0 s | $0.0302 / 19.3 s | $0.0302 / 19.0 s | $0.0302 / 18.4 s | $0.0302 / 19.7 s | $0.2039 |
| `black-forest-labs/flux-3-image` | $0.0480 / 30.1 s | $0.0480 / 44.9 s | $0.0480 / 27.9 s | $0.0480 / 23.7 s | $0.0480 / 27.0 s | $0.0480 / 25.8 s | $0.0480 / 35.3 s | $0.3360 |
| `google/gemini-nano-banana-2.1` | failed | failed | failed | failed | failed | failed | failed | $0.0000 |
| `bytedance-seed/seedream-5-0-pro` | $0.0930 / 43.5 s | $0.0930 / 48.8 s | $0.0930 / 93.9 s | $0.0930 / 103.3 s | $0.0930 / 129.1 s | $0.0930 / 86.8 s | $0.0930 / 102.3 s | $0.6510 |
| `x-ai/grok-imagine-image-2.0` | $0.0800 / 10.1 s | $0.0800 / 13.3 s | $0.0800 / 9.8 s | $0.0800 / 11.6 s | $0.0800 / 10.0 s | $0.0800 / 12.8 s | $0.0800 / 12.0 s | $0.5600 |
| `microsoft/mai-image-2.6` | $0.0443 / 25.9 s | $0.0443 / 24.7 s | $0.0442 / 22.7 s | $0.0443 / 22.7 s | $0.0443 / 23.4 s | $0.0442 / 22.0 s | $0.0443 / 26.1 s | $0.3098 |
| `meta/muse-image` | failed | not run | not run | not run | not run | not run | not run | $0.0000 |

**Suite total: $2.0607** (35 images). OpenRouter account usage after the run: $2.3727 = $0.312 (13 plates,
see plate-report.md) + $2.0607, so the reported costs match the account.

Failed (no cost):

- `google/gemini-nano-banana-2.1`: google/gemini-nano-banana-2.1: HTTP 429: {"error":{"message":"You exceeded your current quota, please check your plan and billing details. For more in
- `meta/muse-image`: meta/muse-image: HTTP 403: {"error":{"message":"This model requires you to complete the following before use: 18+ age confirmation. Confirm at https:/

## Exact prompts (the same text went to every model)

### white_catalog

```text
Professional e-commerce product photo of this ring on a pure white (#FFFFFF) seamless studio background, shown in a three-quarter front view so the main face of the design is clearly visible, soft even studio lighting, a subtle soft contact shadow, sharp focus, true-to-life metal color. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### solid_navy

```text
Luxury jewelry advertisement of this ring on a deep navy blue (#0B1F3A) seamless background with a soft vignette, standing on a glossy black surface with a subtle mirror reflection below it, soft-box lighting that makes the metal glow, three-quarter front view. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### studio_marble

```text
Studio product photo of this ring on a clean white marble surface with fine grey veining, three-quarter front view, soft diffused window light from the upper left, a gentle natural shadow, softly blurred background. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### accessories_silk

```text
Product photo of this ring on smooth champagne-colored silk with soft folds. A few soft pink rose petals and a thin satin ribbon lie near the edges and corners of the frame; none of them touches or covers the ring. Soft window light from the upper left, shallow depth of field. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### display_cushion

```text
Product photo of this ring standing upright in the slit of a beige-grey velvet ring display cushion, seen from the front at eye level against a soft neutral backdrop. The lower part of the band sits inside the slit and the main face of the design is turned toward the camera. Soft diffused light. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### display_box

```text
Product photo of this ring in an open cream jewelry gift box, standing upright in the slot of the white satin cushion, photographed from slightly above at a three-quarter angle, the main face of the design toward the camera, soft diffused light, shallow depth of field. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### hero_3d

```text
Photorealistic 3D render of this ring: a hero shot at a three-quarter angle, floating slightly above a soft gradient grey studio backdrop, crisp reflections on the metal, premium product-visualization look. It must read as the same physical object as in the photos, with its true geometry. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```
