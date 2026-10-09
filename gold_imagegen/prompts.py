"""Prompt templates for jewelry photo edits.

Models drift less outside the edit when the prompt names what must stay and ends with
an explicit "do not change anything else" line.
"""
from __future__ import annotations

KEEP_REST = "Do not change any other elements of the image."

PLACEMENT = {
    "necklace": "neck",
    "ring": "finger",
    "earrings": "ears",
    "bracelet": "wrist",
}

PRESERVE_JEWELRY = (
    "Keep the jewelry exactly as in image 1: same shape, design, metal color and finish "
    "(gold, silver, rose gold or two-tone), engravings, gemstones, chain links and "
    "proportions. Do not redesign, add or remove any detail."
)


def white_background(jewelry: str = "jewelry") -> str:
    return (
        f"Image 1 is a product photo of {jewelry}. Place the {jewelry} on a pure white "
        "(#FFFFFF) seamless studio background with soft, natural lighting and a subtle "
        "contact shadow, like an e-commerce catalog photo. "
        f"{PRESERVE_JEWELRY} Keep the original camera angle and framing. {KEEP_REST}"
    )


def on_model(jewelry: str) -> str:
    if jewelry not in PLACEMENT:
        raise ValueError(
            f"unknown jewelry type {jewelry!r}; choose one of {sorted(PLACEMENT)}"
        )
    where = PLACEMENT[jewelry]
    return (
        f"Image 1 is a product photo of a {jewelry}. Image 2 is a photo of a person. "
        f"Put the {jewelry} from image 1 on the person's {where} in image 2, worn "
        "naturally with realistic scale, position, perspective and gravity. "
        f"{PRESERVE_JEWELRY} Keep the person, face, pose, skin, clothing, background and "
        "lighting of image 2 unchanged. Match the lighting of image 2 on the jewelry and "
        f"add natural contact shadows. {KEEP_REST}"
    )


# --- background "plates" for studio scenes, accessory scenes and compatible displays -------------
# A plate is an AI-generated background WITHOUT the product. The product's own pixels are composited
# on top later (see plates.py), so the model never draws or redraws the jewelry.

PLATE_BASE = (
    "Professional jewelry product photography background plate. {subject} "
    "Photographed {view}, soft diffused window light from the upper left, gentle natural shadows, "
    "high resolution, sharp, realistic. The center of the frame is completely empty and uncluttered, "
    "clear space reserved for placing a piece of jewelry later. "
    "No jewelry, no people, no hands, no text, no logos, no watermarks."
)
PLATE_BASE_DISPLAY = (
    "Professional jewelry product photography background plate. {subject} "
    "Photographed {view}, soft diffused window light from the upper left, gentle natural shadows, "
    "high resolution, sharp, realistic. The display is completely empty: nothing is placed on it. "
    "No jewelry, no people, no hands, no text, no logos, no watermarks."
)
FLAT_LAY = "straight from above (flat lay, camera perpendicular to the surface)"

STUDIO_SURFACES = {
    "white_marble": "A clean white marble surface with subtle grey veining.",
    "grey_marble": "A polished light grey marble surface with fine white veining.",
    "silk": "Smooth champagne-colored silk fabric with soft, gentle folds.",
    "velvet": "Deep navy blue velvet fabric with a soft, even texture.",
    "wood": "A light oak wooden table surface with fine natural grain.",
    "linen": "Natural beige linen fabric with a fine weave.",
    "stone": "A pale honed limestone surface with a soft matte texture.",
}
ACCESSORY_PROPS = {
    "roses": "A few soft pink rose petals and a thin satin ribbon lie near the edges and corners of the frame.",
    "baby_breath": "Small sprigs of baby's breath flowers lie near the edges of the frame.",
    "gift": "The corner of a small white gift box with a satin ribbon enters the frame at one edge.",
    "pearls": "A short strand of loose pearls lies in one corner of the frame.",
}
# Compatible displays only: the product photo must already have the matching angle (front view
# upright for rings and earrings, top-down for the box), because its pixels are not redrawn.
DISPLAY_SUBJECTS = {
    "display_ring": (
        "A velvet ring display cushion with a clean horizontal slit across its top, where a ring "
        "would stand upright. The slit is empty. Soft neutral backdrop.",
        "straight from the front at eye level",
    ),
    "display_earrings": (
        "A plain cream earring display card standing upright, with two small empty holes near its "
        "top edge where earrings would hang. The card is empty. Soft neutral backdrop.",
        "straight from the front",
    ),
    "display_box": (
        "An open jewelry gift box with an empty satin-lined cushion inside.",
        "straight from directly above (top-down)",
    ),
}
PLATE_KINDS = ("scene", "accessories", *DISPLAY_SUBJECTS)


def plate_prompt(kind: str, style: str = "white_marble", props: str | None = None) -> str:
    if kind not in PLATE_KINDS:
        raise ValueError(f"unknown plate kind {kind!r}; choose one of {list(PLATE_KINDS)}")
    if kind in DISPLAY_SUBJECTS:
        subject, view = DISPLAY_SUBJECTS[kind]
        return PLATE_BASE_DISPLAY.format(subject=subject, view=view)
    if style not in STUDIO_SURFACES:
        raise ValueError(f"unknown style {style!r}; choose one of {sorted(STUDIO_SURFACES)}")
    subject = STUDIO_SURFACES[style]
    if kind == "accessories":
        props = props or "roses"
        if props not in ACCESSORY_PROPS:
            raise ValueError(f"unknown props {props!r}; choose one of {sorted(ACCESSORY_PROPS)}")
        subject += " " + ACCESSORY_PROPS[props] + " Props stay near the edges, never in the center."
    return PLATE_BASE.format(subject=subject, view=FLAT_LAY)


# --- reference-based suite prompts ----------------------------------------------------------------
# The model is shown real photos of ONE piece and may re-render it in a new scene (3D, in a box, ...).
# The design must not change, so every prompt carries the same explicit "keep exactly" block plus a
# short design brief (what the piece looks like) written per product.

SUITE_PRESERVE = (
    "The reference images show ONE real piece of jewelry. {roles} {brief} "
    "Reproduce exactly this piece: keep every engraving, motif, stone (count, shape and color), setting, "
    "proportion, metal color and finish exactly as in the references. Do not redesign, simplify, stylize, "
    "add or remove any detail, and never replace a motif with a different one. Where a detail is not visible "
    "in the references, continue only what is visible. Do not change any other element of the design."
)
_HAND_RULES = (
    "Skin tone: {skin}; {nails}; no other jewelry, no watch, no tattoos; the hand is cropped "
    "at the wrist or forearm and no face is visible. Correct hand anatomy: exactly five fingers with natural "
    "proportions, and the {item} fits the finger snugly at a realistic scale for {wearer} hand."
)
# For scenes where the hand holds something and the ring is not worn.
_HOLD_RULES = (
    "Skin tone: {skin}; {nails}; no other jewelry, no watch, no tattoos; the hand is cropped at the wrist or "
    "forearm and no face is visible. Correct hand anatomy: exactly five fingers with natural proportions."
)
# For scenes with two products (a couple's set): reference photos of both rings are given.
SUITE_PRESERVE_PAIR = (
    "The reference images show TWO real rings. {roles} {brief} "
    "Reproduce exactly both rings: keep every engraving, motif, stone (count, shape and color), setting, "
    "proportion, metal color and finish of each ring exactly as in its own references. Never merge the two "
    "designs, never replace a motif with a different one, and do not add or remove any detail."
)
SUITE_SCENES = {
    "white_catalog": (
        "Professional e-commerce product photo of this {item} on a pure white (#FFFFFF) seamless studio "
        "background, shown in a three-quarter front view so the main face of the design is clearly visible, "
        "soft even studio lighting, a subtle soft contact shadow, sharp focus, true-to-life metal color."
    ),
    "solid_navy": (
        "Luxury jewelry advertisement of this {item} on a deep navy blue (#0B1F3A) seamless background with a "
        "soft vignette, standing on a glossy black surface with a subtle mirror reflection below it, soft-box "
        "lighting that makes the metal glow, three-quarter front view."
    ),
    "studio_marble": (
        "Studio product photo of this {item} on a clean white marble surface with fine grey veining, "
        "three-quarter front view, soft diffused window light from the upper left, a gentle natural shadow, "
        "softly blurred background."
    ),
    "accessories_silk": (
        "Product photo of this {item} on smooth champagne-colored silk with soft folds. A few soft pink rose "
        "petals and a thin satin ribbon lie near the edges and corners of the frame; none of them touches or "
        "covers the {item}. Soft window light from the upper left, shallow depth of field."
    ),
    "display_cushion": (
        "Product photo of this {item} standing upright in the slit of a beige-grey velvet ring display "
        "cushion, seen from the front at eye level against a soft neutral backdrop. The lower part of the band "
        "sits inside the slit and the main face of the design is turned toward the camera. Soft diffused light."
    ),
    "display_box": (
        "Product photo of this {item} in an open cream jewelry gift box, standing upright in the slot of the "
        "white satin cushion, photographed from slightly above at a three-quarter angle, the main face of the "
        "design toward the camera, soft diffused light, shallow depth of field."
    ),
    "hero_3d": (
        "Photorealistic 3D render of this {item}: a hero shot at a three-quarter angle, floating slightly above "
        "a soft gradient grey studio backdrop, crisp reflections on the metal, premium product-visualization "
        "look. It must read as the same physical object as in the photos, with its true geometry."
    ),
    "hand_flat": (
        "Photorealistic close-up product photo of this {item} worn on the ring finger of {wearer} hand, the back "
        "of the hand facing the camera, fingers relaxed and slightly apart, the hand resting on a soft neutral "
        "surface. " + _HAND_RULES + " Soft diffused window light, shallow depth of field."
    ),
    "hand_fist": (
        "Photorealistic product photo of this {item} worn on the ring finger of {wearer} hand held in a loose "
        "fist and seen from the front, the knuckles toward the camera so the main face of the design is clearly "
        "visible. " + _HAND_RULES + " Soft studio light, shallow depth of field, neutral blurred background."
    ),
    "hand_resting": (
        "Photorealistic product photo of this {item} worn on the ring finger of {wearer} hand resting on a dark "
        "polished wooden table, seen from a low three-quarter side angle with the ring turned toward the camera "
        "so the main face of the design is visible. " + _HAND_RULES + " Warm soft light, shallow depth of field."
    ),
    "hand_raised": (
        "Photorealistic lifestyle product photo of this {item} worn on the ring finger of {wearer} hand raised "
        "in front of the chest, fingers gently curled and the back of the hand slightly turned toward the camera, "
        "the ring catching the light. " + _HAND_RULES + " Soft blurred neutral studio background."
    ),
    "black_gold_luxury": (
        "Dark, moody luxury jewelry advertisement of this {item} on polished black marble with thin gold veins, "
        "dramatic rim lighting from behind and a soft warm golden glow, a faint reflection of the {item} in the "
        "surface, deep shadows, three-quarter front view, ultra-sharp detail, cinematic."
    ),
    "sunlit_window": (
        "Warm golden-hour lifestyle photo of this {item} resting on natural linen cloth on a sunlit windowsill, "
        "soft sunlight with gentle leaf-shaped shadows falling across the cloth but not across the face of the "
        "{item}, shallow depth of field, a calm blurred garden outside, three-quarter front view."
    ),
    "podium_minimal": (
        "Modern minimalist product photo of this {item} standing on a small cream plaster podium, a soft pastel "
        "beige background with a gentle arch shape, soft studio light with a clean long shadow, portrait "
        "composition with generous empty space above, premium catalog style."
    ),
    "flowers_editorial": (
        "Editorial still life of this {item} on a pale stone slab, surrounded by a few dried flowers, eucalyptus "
        "leaves and a sprig of baby's breath placed around it without touching or covering it, soft natural "
        "light, muted earthy palette, shallow depth of field."
    ),
    "hero_banner": (
        "Wide website hero banner: this {item} large on the right third of the frame on a dark charcoal gradient "
        "background with soft golden bokeh lights, the left two thirds empty and calm for headline text, "
        "luxurious elegant mood, sharp focus on the {item}, three-quarter front view."
    ),
    "macro_closeup": (
        "Extreme macro close-up of the main face of this {item}: the central stone, its halo of small stones and "
        "the engraved shoulder ornament in razor-sharp focus, very shallow depth of field, soft warm studio "
        "light, rich reflections on the metal."
    ),
    "turntable_sheet": (
        "A clean 2x2 product sheet on a pure white background showing the same {item} from four angles: front, "
        "three-quarter left, side profile and top-down looking through the band, evenly lit, equal size, thin "
        "light-grey separators, no text."
    ),
    "hand_luxury": (
        "Dark, moody lifestyle photo of this {item} worn on the ring finger of {wearer} hand resting on the "
        "edge of a dark leather armchair, a tailored dark suit sleeve with a white shirt cuff visible, low-key "
        "warm lighting, shallow depth of field. " + _HAND_RULES
    ),
    "macro_stone": (
        "Extreme macro close-up of the central stone of this {item} with its frame and halo of small stones, "
        "razor-sharp focus on the stone's edge and the setting, very shallow depth of field, soft warm studio "
        "light, rich reflections on the metal."
    ),
    "macro_ornament": (
        "Extreme macro close-up of the engraved ornament on the shoulder of this {item}, razor-sharp focus on "
        "the carved lines and the dark recesses, the metal texture clearly visible, very shallow depth of "
        "field, soft warm studio light."
    ),
    "coin_scale": (
        "Product photo of this {item} lying next to a plain round silver coin with no writing or numbers on a "
        "neutral light-grey surface, to show its true size, top-down view, both objects fully in the frame, "
        "soft even studio light, sharp focus. {scale_note}"
    ),
    "ruler_scale": (
        "Product photo of this {item} lying next to a flat steel ruler with fine millimetre tick marks and no "
        "numbers on a neutral light-grey surface, to show its size, top-down view, both objects fully in the "
        "frame, soft even studio light, sharp focus. {ruler_note}"
    ),
    "woman_hand_flowers": (
        "Photorealistic product photo of this {item} worn on the ring finger of {wearer} hand, the hand gently "
        "holding a single long-stem pink rose, the back of the hand toward the camera, soft window light, a "
        "creamy blurred background, shallow depth of field. " + _HAND_RULES
    ),
    "proposal_box": (
        "Romantic marriage-proposal photo: {wearer} hand holds out an open ring box toward the camera, this "
        "{item} standing upright in the slot of the box's cushion with the main face of the design toward the "
        "camera, a softly blurred candlelit background with a few rose petals, warm light, shallow depth of "
        "field. " + _HOLD_RULES
    ),
    "couple_rings_set": (
        "Romantic engagement still life of the two rings from the reference photos, a larger one and a smaller "
        "one, resting side by side on a white satin cushion with a few soft rose petals near the edges, soft "
        "warm light, shallow depth of field, three-quarter view, both rings clearly visible."
    ),
    "persian_tile": (
        "Product photo of this {item} resting on a surface of hand-painted Persian turquoise tiles with blue "
        "and white floral arabesque patterns, soft window light, shallow depth of field, three-quarter front "
        "view. The tile pattern is only the surface, never on the {item}."
    ),
    "persian_rug": (
        "Product photo of this {item} resting on a fine Persian rug with a red and navy medallion pattern, warm "
        "soft light, shallow depth of field, three-quarter front view. The rug pattern is only the surface, "
        "never on the {item}."
    ),
    "copper_tray": (
        "Product photo of this {item} on a round hand-engraved antique copper tray with fine Persian patterns, "
        "warm soft light, shallow depth of field, three-quarter front view. The engraving of the tray is only "
        "the surface, never on the {item}."
    ),
    "hafez_book": (
        "Product photo of this {item} resting on the open pages of an old leather-bound book of Persian poetry "
        "whose calligraphy is softly blurred and illegible, a single dried rose beside it, warm lamp light, "
        "shallow depth of field, three-quarter front view."
    ),
    "tea_nabat": (
        "Product photo of this {item} in the foreground beside a small clear glass of amber tea in a saucer and "
        "a few crystals of rock candy on a small plate, a little steam, cozy warm light, shallow depth of "
        "field. Nothing covers or touches the {item}."
    ),
    "pomegranate_saffron": (
        "Product photo of this {item} on a dark wooden table beside a halved pomegranate with glistening red "
        "seeds and a small bowl of saffron threads, warm light, shallow depth of field. Nothing covers or "
        "touches the {item}."
    ),
    "nowruz": (
        "Nowruz still life: this {item} in the foreground on a spring table, with a haft-sin setting softly "
        "blurred behind it: green wheat sprouts in a dish, a hyacinth, painted eggs, a small mirror and a bowl "
        "with a goldfish, soft bright spring light. Everything else is only a background; nothing covers or "
        "touches the {item}."
    ),
    "yalda": (
        "Shab-e Yalda still life: this {item} in the foreground on a dark table beside halved pomegranates with "
        "glistening seeds, a few lit candles giving warm flame light, dried fruits and nuts softly blurred "
        "behind, a deep red and gold palette, cozy mood. Nothing covers or touches the {item}."
    ),
    "sepandarmazgan": (
        "Romantic Persian Valentine (Sepandarmazgan) gift scene: this {item} on a soft satin cloth surrounded by "
        "red and pink roses and a thin satin ribbon, warm bokeh candle lights in the background, tender "
        "romantic mood, shallow depth of field. Nothing covers or touches the {item}."
    ),
    "mothers_day": (
        "Mother's Day gift scene: this {item} on pastel silk beside a small bouquet of pink tulips and baby's "
        "breath tied with a ribbon, soft morning light, tender mood, shallow depth of field. Nothing covers or "
        "touches the {item}."
    ),
    "fathers_day": (
        "Father's Day gift scene for a men's ring: this {item} on a dark wooden desk beside a leather-bound "
        "notebook and a fountain pen, with a small wrapped gift box softly blurred behind, warm lamp light, "
        "shallow depth of field. Nothing covers or touches the {item}."
    ),
}
SUITE_NAMES = tuple(SUITE_SCENES)
# Prompts that want a different frame; everything else is square. `--aspect` overrides this for all prompts.
SUITE_ASPECTS = {
    "sunlit_window": "4:5", "podium_minimal": "4:5", "hand_luxury": "4:5", "hero_banner": "16:9",
    "woman_hand_flowers": "4:5", "proposal_box": "4:5", "mothers_day": "4:5",
}
# Scenes that fix part of the hand description whatever the caller passes.
SCENE_OVERRIDES = {
    "woman_hand_flowers": {"wearer": "a woman's", "nails": "neatly shaped nails with a soft nude manicure"},
    "proposal_box": {"wearer": "a man's"},
}
PAIR_SCENES = frozenset({"couple_rings_set"})


def suite_prompt(
    name: str, *, item: str = "piece", brief: str = "", roles: str = "",
    wearer: str = "a man's", skin: str = "natural medium (wheat)", nails: str = "natural short clean nails",
    head_width_mm: float | None = None, coin_mm: float = 24.0,
) -> str:
    """The scene sentence plus the "keep the design exactly" block.

    `head_width_mm` (the ring's face width) makes the coin/ruler scenes state a true size; without it
    they only ask for a realistic one. The model still draws the proportion, so it is approximate.
    """
    if name not in SUITE_SCENES:
        raise ValueError(f"unknown prompt {name!r}; choose one of {list(SUITE_NAMES)}")
    if head_width_mm:
        scale_note = (
            f"True scale: the coin is {coin_mm:g} mm wide and the ring's face is {head_width_mm:g} mm wide, so "
            f"the coin is {coin_mm / head_width_mm:.1f} times as wide as the ring's face."
        )
        ruler_note = f"True scale: the ring's face is {head_width_mm:g} mm wide, measured along the ruler's ticks."
    else:
        scale_note = "The coin is about twice as wide as the ring's face."
        ruler_note = "Show the ring at a realistic size against the ruler."
    values = {
        "item": item, "wearer": wearer, "skin": skin, "nails": nails,
        "scale_note": scale_note, "ruler_note": ruler_note, **SCENE_OVERRIDES.get(name, {}),
    }
    scene = SUITE_SCENES[name].format(**values)
    block = SUITE_PRESERVE_PAIR if name in PAIR_SCENES else SUITE_PRESERVE
    preserve = block.format(roles=roles, brief=brief)
    return f"{scene} {' '.join(preserve.split())}"
