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
    "Keep the jewelry exactly as in image 1: same shape, design, gold color and finish, "
    "engravings, gemstones, chain links and proportions. Do not redesign, add or remove "
    "any detail."
)


def white_background(jewelry: str = "gold jewelry") -> str:
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
        f"Image 1 is a product photo of a gold {jewelry}. Image 2 is a photo of a person. "
        f"Put the {jewelry} from image 1 on the person's {where} in image 2, worn "
        "naturally with realistic scale, position, perspective and gravity. "
        f"{PRESERVE_JEWELRY} Keep the person, face, pose, skin, clothing, background and "
        "lighting of image 2 unchanged. Match the lighting of image 2 on the jewelry and "
        f"add natural contact shadows. {KEEP_REST}"
    )
