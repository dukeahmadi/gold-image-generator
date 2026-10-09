# Ring on a hand: four poses across six models (2026-10-09)

Same two ring photos as in ring-test-report.md (cropped square around the ring, no resampling), same design brief and
image roles, four hand poses of a man's hand with natural medium (wheat) skin, run through six models via OpenRouter
`POST /api/v1/images` at `aspect_ratio` `1:1`. The models redraw the ring AND draw the hand, so check both: finger
count and proportions, the ring's scale on the finger, and every detail of the design against the photos.

**Design brief:** A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom.

**Image roles:** Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible.

## Cost

| model | hand_flat | hand_fist | hand_resting | hand_raised | total |
|---|---|---|---|---|---|
| `openai/gpt-image-2.5-sunburst` | $0.0305 / 22.1 s | $0.0305 / 28.6 s | $0.0305 / 22.5 s | $0.0305 / 23.2 s | $0.1221 |
| `black-forest-labs/flux-3-image` | $0.0480 / 28.3 s | $0.0480 / 39.1 s | $0.0480 / 41.9 s | $0.0480 / 28.3 s | $0.1920 |
| `google/gemini-nano-banana-2.1` | $0.0405 / 21.2 s | $0.0439 / 23.7 s | $0.0408 / 13.7 s | $0.0406 / 16.7 s | $0.1659 |
| `bytedance-seed/seedream-5-0-pro` | $0.0930 / 122.4 s | $0.0930 / 110.7 s | $0.0930 / 96.4 s | $0.0930 / 93.6 s | $0.3720 |
| `x-ai/grok-imagine-image-2.0` | $0.0800 / 16.8 s | $0.0800 / 15.0 s | $0.0800 / 14.5 s | $0.0800 / 14.3 s | $0.3200 |
| `microsoft/mai-image-2.6` | $0.0446 / 25.0 s | $0.0446 / 26.7 s | $0.0446 / 27.7 s | $0.0446 / 30.5 s | $0.1784 |

**Run total: $1.3504** (24 images, all succeeded; Nano Banana 2.1 worked this time after failing with a Google quota
error in the previous run). OpenRouter account usage after this run: $3.7231
(= 0.312 plates + 2.0607 ring suite + 1.3504 hands).

## Exact prompts (the same text went to every model)

### hand_flat

```text
Photorealistic close-up product photo of this ring worn on the ring finger of a man's hand, the back of the hand facing the camera, fingers relaxed and slightly apart, the hand resting on a soft neutral surface. Skin tone: natural medium (wheat); natural short clean nails; no other jewelry, no watch, no tattoos; the hand is cropped at the wrist or forearm and no face is visible. Correct hand anatomy: exactly five fingers with natural proportions, and the ring fits the finger snugly at a realistic scale for a man's hand. Soft diffused window light, shallow depth of field. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### hand_fist

```text
Photorealistic product photo of this ring worn on the ring finger of a man's hand held in a loose fist and seen from the front, the knuckles toward the camera so the main face of the design is clearly visible. Skin tone: natural medium (wheat); natural short clean nails; no other jewelry, no watch, no tattoos; the hand is cropped at the wrist or forearm and no face is visible. Correct hand anatomy: exactly five fingers with natural proportions, and the ring fits the finger snugly at a realistic scale for a man's hand. Soft studio light, shallow depth of field, neutral blurred background. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### hand_resting

```text
Photorealistic product photo of this ring worn on the ring finger of a man's hand resting on a dark polished wooden table, seen from a low three-quarter side angle with the ring turned toward the camera so the main face of the design is visible. Skin tone: natural medium (wheat); natural short clean nails; no other jewelry, no watch, no tattoos; the hand is cropped at the wrist or forearm and no face is visible. Correct hand anatomy: exactly five fingers with natural proportions, and the ring fits the finger snugly at a realistic scale for a man's hand. Warm soft light, shallow depth of field. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### hand_raised

```text
Photorealistic lifestyle product photo of this ring worn on the ring finger of a man's hand raised in front of the chest, fingers gently curled and the back of the hand slightly turned toward the camera, the ring catching the light. Skin tone: natural medium (wheat); natural short clean nails; no other jewelry, no watch, no tattoos; the hand is cropped at the wrist or forearm and no face is visible. Correct hand anatomy: exactly five fingers with natural proportions, and the ring fits the finger snugly at a realistic scale for a man's hand. Soft blurred neutral studio background. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```
