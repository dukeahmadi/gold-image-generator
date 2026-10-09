# Seedream 5.0 Pro on creative scenes (2026-10-09)

Model `bytedance-seed/seedream-5-0-pro` via OpenRouter `POST /api/v1/images`, same two ring photos and design brief as
before, per-prompt aspect ratios (`hero_banner` 16:9, three portraits 4:5, the rest 1:1).

**Brief:** A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom.

**Roles:** Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible.

| prompt | size | cost | time |
|---|---|---|---|
| `black_gold_luxury` | 2048x2048 | $0.093 | 110.2 s |
| `sunlit_window` | 1640x2048 | $0.093 | 102.8 s |
| `podium_minimal` | 1640x2048 | $0.093 | 100.7 s |
| `flowers_editorial` | 2048x2048 | $0.093 | 100.0 s |
| `hero_banner` | 2048x1152 | $0.048 | 81.9 s |

**Total $0.420** for 5 images. Seedream returns about 2K images; the 16:9 banner cost less ($0.048) than a
square ($0.093), so the price follows the pixel count.

**Not run:** `macro_closeup`, `turntable_sheet`, `hand_luxury`. OpenRouter answered HTTP 402 "Insufficient credits" even
with $0.51 left of $5: it seems to reserve the worst-case cost of a call before running it, and for this model that
is above the remaining balance. They need a credit top-up.

## Observations

Beauty: commercial quality in all five (lighting, depth of field, composition; the banner leaves the left two thirds
empty for a headline). Fidelity to the photos: the design family is kept in every image (flat black stone in a thin
gold frame, halo of small dark stones with a beaded edge, scroll ornament on the shoulders, matte bronze), but
- the **shoulder ornament changes from image to image** (a different scroll or leaf motif each time, bolder than the
  original's fine dense curls);
- the stone proportion varies (a vertical rectangle in `podium_minimal`; the original is nearly square);
- the band is chunkier than the original in several.

For a catalog the engraving must look the same in every image; extra reference photos (a close-up of the ornament)
and a post-check are the planned remedies.

## Exact prompts

### black_gold_luxury

```text
Dark, moody luxury jewelry advertisement of this ring on polished black marble with thin gold veins, dramatic rim lighting from behind and a soft warm golden glow, a faint reflection of the ring in the surface, deep shadows, three-quarter front view, ultra-sharp detail, cinematic. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### sunlit_window

```text
Warm golden-hour lifestyle photo of this ring resting on natural linen cloth on a sunlit windowsill, soft sunlight with gentle leaf-shaped shadows falling across the cloth but not across the face of the ring, shallow depth of field, a calm blurred garden outside, three-quarter front view. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### podium_minimal

```text
Modern minimalist product photo of this ring standing on a small cream plaster podium, a soft pastel beige background with a gentle arch shape, soft studio light with a clean long shadow, portrait composition with generous empty space above, premium catalog style. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### flowers_editorial

```text
Editorial still life of this ring on a pale stone slab, surrounded by a few dried flowers, eucalyptus leaves and a sprig of baby's breath placed around it without touching or covering it, soft natural light, muted earthy palette, shallow depth of field. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### hero_banner

```text
Wide website hero banner: this ring large on the right third of the frame on a dark charcoal gradient background with soft golden bokeh lights, the left two thirds empty and calm for headline text, luxurious elegant mood, sharp focus on the ring, three-quarter front view. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### macro_closeup

```text
Extreme macro close-up of the main face of this ring: the central stone, its halo of small stones and the engraved shoulder ornament in razor-sharp focus, very shallow depth of field, soft warm studio light, rich reflections on the metal. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### turntable_sheet

```text
A clean 2x2 product sheet on a pure white background showing the same ring from four angles: front, three-quarter left, side profile and top-down looking through the band, evenly lit, equal size, thin light-grey separators, no text. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```

### hand_luxury

```text
Dark, moody lifestyle photo of this ring worn on the ring finger of a man's hand resting on the edge of a dark leather armchair, a tailored dark suit sleeve with a white shirt cuff visible, low-key warm lighting, shallow depth of field. Skin tone: natural medium (wheat); natural short clean nails; no other jewelry, no watch, no tattoos; the hand is cropped at the wrist or forearm and no face is visible. Correct hand anatomy: exactly five fingers with natural proportions, and the ring fits the finger snugly at a realistic scale for a man's hand. The reference images show ONE real piece of jewelry. Image 1 shows the front of the ring, with the black stone facing the camera. Image 2 shows the same ring from above and the side, with the head seen at the top and the inside of the band visible. A men's signet-style ring in a warm antique-gold (bronze) colored metal with a matte, slightly brushed finish. The head is a square bezel holding a flat, square, glossy black stone with a thin gold frame, surrounded by a halo of tiny dark round stones set in a serrated, beaded border. Both shoulders of the ring are wide panels carved with a flowing scroll (swirl) ornament with dark recesses. The band is smooth and tapers toward the bottom. Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, add or remove any detail, and never replace a motif with a different one. Where a detail is not visible in the references, continue only what is visible. Do not change any other element of the design.
```
