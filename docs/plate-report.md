# Plate generation report (2026-10-08)

Model `black-forest-labs/flux-3-image` through OpenRouter `POST /api/v1/images`, one image per call,
`aspect_ratio` `1:1` (accepted by the model; without it the first plate came out 1184x880).
Compositing the products onto the plates is local and costs nothing.

| plate | kind | cost | time | status |
|---|---|---|---|---|
| `accessories_silk_roses_01` | accessories | $0.024 | 148.3 s | used |
| `accessories_velvet_pearls_01` | accessories | $0.024 | 21.6 s | used |
| `accessories_white_marble_baby_breath_01` | accessories | $0.024 | 28.8 s | used |
| `display_box_01` | display_box | $0.024 | 26.7 s | used |
| `display_box_02` | display_box | $0.024 | 20.4 s | used |
| `display_earrings_01` | display_earrings | $0.024 | 22.2 s | used |
| `display_ring_01` | display_ring | $0.024 | 20.1 s | used |
| `scene_silk_01` | scene | $0.024 | 18.9 s | used |
| `scene_velvet_01` | scene | $0.024 | 18.2 s | used |
| `scene_white_marble_01` | scene | $0.024 | 21.7 s | used |
| `scene_white_marble_02` | scene | $0.024 | 22.0 s | used |
| `scene_wood_01` | scene | $0.024 | 28.2 s | used |
| `rejected_display_ring_02` | display_ring | $0.024 | 19.9 s | rejected: 3/4 view from above, angle cannot match a front-view ring photo |

**Total: $0.312 for 13 plates ($0.024 each).** Cross-check: the OpenRouter account usage
endpoint reported exactly $0.312 after the run. Plates are generated once and reused for every product, so the
per-product cost of the scene, accessories and display images is zero.

One call (`accessories_silk_roses_01`) took 148 s; the rest took 18-29 s.

## Exact prompts

**`accessories_silk_roses_01`**

```text
Professional jewelry product photography background plate. Smooth champagne-colored silk fabric with soft, gentle folds. A few soft pink rose petals and a thin satin ribbon lie near the edges and corners of the frame. Props stay near the edges, never in the center. Photographed straight from above (flat lay, camera perpendicular to the surface), soft diffused window light from the upper left, gentle natural shadows, high resolution, sharp, realistic. The center of the frame is completely empty and uncluttered, clear space reserved for placing a piece of jewelry later. No jewelry, no people, no hands, no text, no logos, no watermarks.
```
**`accessories_velvet_pearls_01`**

```text
Professional jewelry product photography background plate. Deep navy blue velvet fabric with a soft, even texture. A short strand of loose pearls lies in one corner of the frame. Props stay near the edges, never in the center. Photographed straight from above (flat lay, camera perpendicular to the surface), soft diffused window light from the upper left, gentle natural shadows, high resolution, sharp, realistic. The center of the frame is completely empty and uncluttered, clear space reserved for placing a piece of jewelry later. No jewelry, no people, no hands, no text, no logos, no watermarks.
```
**`accessories_white_marble_baby_breath_01`**

```text
Professional jewelry product photography background plate. A clean white marble surface with subtle grey veining. Small sprigs of baby's breath flowers lie near the edges of the frame. Props stay near the edges, never in the center. Photographed straight from above (flat lay, camera perpendicular to the surface), soft diffused window light from the upper left, gentle natural shadows, high resolution, sharp, realistic. The center of the frame is completely empty and uncluttered, clear space reserved for placing a piece of jewelry later. No jewelry, no people, no hands, no text, no logos, no watermarks.
```
**`display_box_01`, `display_box_02`**

```text
Professional jewelry product photography background plate. An open jewelry gift box with an empty satin-lined cushion inside. Photographed straight from directly above (top-down), soft diffused window light from the upper left, gentle natural shadows, high resolution, sharp, realistic. The display is completely empty: nothing is placed on it. No jewelry, no people, no hands, no text, no logos, no watermarks.
```
**`display_earrings_01`**

```text
Professional jewelry product photography background plate. A plain cream earring display card standing upright, with two small empty holes near its top edge where earrings would hang. The card is empty. Soft neutral backdrop. Photographed straight from the front, soft diffused window light from the upper left, gentle natural shadows, high resolution, sharp, realistic. The display is completely empty: nothing is placed on it. No jewelry, no people, no hands, no text, no logos, no watermarks.
```
**`display_ring_01`, `rejected_display_ring_02`**

```text
Professional jewelry product photography background plate. A velvet ring display cushion with a clean horizontal slit across its top, where a ring would stand upright. The slit is empty. Soft neutral backdrop. Photographed straight from the front at eye level, soft diffused window light from the upper left, gentle natural shadows, high resolution, sharp, realistic. The display is completely empty: nothing is placed on it. No jewelry, no people, no hands, no text, no logos, no watermarks.
```
**`scene_silk_01`**

```text
Professional jewelry product photography background plate. Smooth champagne-colored silk fabric with soft, gentle folds. Photographed straight from above (flat lay, camera perpendicular to the surface), soft diffused window light from the upper left, gentle natural shadows, high resolution, sharp, realistic. The center of the frame is completely empty and uncluttered, clear space reserved for placing a piece of jewelry later. No jewelry, no people, no hands, no text, no logos, no watermarks.
```
**`scene_velvet_01`**

```text
Professional jewelry product photography background plate. Deep navy blue velvet fabric with a soft, even texture. Photographed straight from above (flat lay, camera perpendicular to the surface), soft diffused window light from the upper left, gentle natural shadows, high resolution, sharp, realistic. The center of the frame is completely empty and uncluttered, clear space reserved for placing a piece of jewelry later. No jewelry, no people, no hands, no text, no logos, no watermarks.
```
**`scene_white_marble_01`, `scene_white_marble_02`**

```text
Professional jewelry product photography background plate. A clean white marble surface with subtle grey veining. Photographed straight from above (flat lay, camera perpendicular to the surface), soft diffused window light from the upper left, gentle natural shadows, high resolution, sharp, realistic. The center of the frame is completely empty and uncluttered, clear space reserved for placing a piece of jewelry later. No jewelry, no people, no hands, no text, no logos, no watermarks.
```
**`scene_wood_01`**

```text
Professional jewelry product photography background plate. A light oak wooden table surface with fine natural grain. Photographed straight from above (flat lay, camera perpendicular to the surface), soft diffused window light from the upper left, gentle natural shadows, high resolution, sharp, realistic. The center of the frame is completely empty and uncluttered, clear space reserved for placing a piece of jewelry later. No jewelry, no people, no hands, no text, no logos, no watermarks.
```

## Review and hand-tuned metadata

Every plate was looked at before use. All scene and accessory plates had an empty center and no jewelry, text or
people. Display plates need metadata set by hand (read off a 0.1 grid):

| plate | slot (x, y, w, h) | anchor | occlude_below |
|---|---|---|---|
| `display_ring_01` | 0.30, 0.10, 0.40, 0.42 | bottom | 0.50 (front lip of the cushion) |
| `display_earrings_01` | 0.31, 0.28, 0.38, 0.50 | top | none |
| `display_box_01` | 0.33, 0.52, 0.34, 0.30 | center | none |
| `display_box_02` | 0.34, 0.52, 0.36, 0.30 | center | none |
