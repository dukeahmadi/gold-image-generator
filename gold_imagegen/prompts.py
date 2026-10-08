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
