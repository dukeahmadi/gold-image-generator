"""The preset catalog for rings: what the website offers, grouped, with what each needs from the user.

Each preset is one scene in `prompts.SUITE_SCENES` (same key) plus the product-level facts the form needs:
a Persian title, the extra inputs to collect, how likely the model is to change the design, and the
pixel-preserving alternative when there is one (see render.py).

    python -m gold_imagegen.presets              # the menu
    python -m gold_imagegen.presets --json       # for the website form
    python -m gold_imagegen.presets --markdown   # docs/presets.md
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from . import prompts

GROUPS = {
    "catalog": "کاتالوگ و جزئیات",
    "hands": "روی دست",
    "gift": "هدیه و خواستگاری",
    "studio": "صحنه‌های استودیویی",
    "persian": "زمینه‌های ایرانی",
    "occasion": "مناسبتی",
}
NEEDS = {
    "gender": "جنسیت (زنانه / مردانه)",
    "skin_tone": "رنگ پوست دست",
    "head_width_mm": "عرض سر انگشتر (میلی‌متر)",
    "second_ring_photos": "عکس‌های حلقهٔ دوم",
}
RISKS = ("low", "medium", "high")  # how likely the model is to change the design


@dataclass(frozen=True)
class Preset:
    key: str
    group: str
    title: str
    needs: tuple[str, ...] = ()
    risk: str = "medium"
    exact: str | None = None  # pixel-preserving alternative in render.py, if any
    note: str = ""

    @property
    def aspect(self) -> str:
        return prompts.SUITE_ASPECTS.get(self.key, "1:1")


PRESETS = (
    # catalog and detail
    Preset("white_catalog", "catalog", "سفید خالص", exact="white", note="نسخهٔ دقیق (پیکسل‌های اصلی) هم دارد"),
    Preset("macro_stone", "catalog", "ماکرو از سنگ", note="نگین‌های ریز ممکن است کمی عوض شوند"),
    Preset("macro_ornament", "catalog", "ماکرو از نقش", note="نقش ممکن است کمی عوض شود؛ عکس نزدیک مرجع کمک می‌کند"),
    Preset("coin_scale", "catalog", "کنار سکه (اندازه)", needs=("head_width_mm",),
           note="نسبت اندازه تقریبی است؛ برای اندازهٔ واقعی عرض سر انگشتر لازم است"),
    Preset("ruler_scale", "catalog", "کنار خط‌کش (اندازه)", needs=("head_width_mm",),
           note="نسبت اندازه تقریبی است؛ برای اندازهٔ واقعی عرض سر انگشتر لازم است"),
    # on a hand
    Preset("hand_flat", "hands", "پشت دست", needs=("gender", "skin_tone"), risk="high"),
    Preset("hand_fist", "hands", "مشت", needs=("gender", "skin_tone"), risk="high"),
    Preset("hand_resting", "hands", "دست روی میز", needs=("gender", "skin_tone"), risk="high"),
    Preset("woman_hand_flowers", "hands", "دست خانم با مانیکور و گل", needs=("skin_tone",), risk="high",
           note="مناسب انگشتر زنانه"),
    # gift
    Preset("display_box", "gift", "توی جعبه", exact="display"),
    Preset("proposal_box", "gift", "جعبهٔ باز در دست (خواستگاری)", needs=("skin_tone",), risk="high"),
    Preset("couple_rings_set", "gift", "ست زوج (حلقهٔ نامزدی)", needs=("second_ring_photos",), risk="high",
           note="هر دو حلقه باید عکس داشته باشند"),
    # studio
    Preset("studio_marble", "studio", "مرمر سفید", exact="scene"),
    Preset("accessories_silk", "studio", "ابریشم با گلبرگ و روبان", exact="accessories"),
    Preset("podium_minimal", "studio", "پایهٔ مینیمال"),
    Preset("black_gold_luxury", "studio", "مشکی-طلایی لوکس"),
    Preset("flowers_editorial", "studio", "گل خشک و سنگ"),
    Preset("sunlit_window", "studio", "نور آفتاب پنجره"),
    # Iranian backgrounds
    Preset("persian_tile", "persian", "کاشی فیروزه‌ای"),
    Preset("persian_rug", "persian", "قالی"),
    Preset("copper_tray", "persian", "سینی مسی"),
    Preset("hafez_book", "persian", "دیوان حافظ", note="متن کتاب عمداً محو و ناخوانا است"),
    Preset("tea_nabat", "persian", "استکان چای و نبات"),
    Preset("pomegranate_saffron", "persian", "انار و زعفران"),
    # occasions
    Preset("nowruz", "occasion", "نوروز", note="هفت‌سین فقط پس‌زمینه است"),
    Preset("yalda", "occasion", "شب یلدا"),
    Preset("sepandarmazgan", "occasion", "سپندارمذگان"),
    Preset("mothers_day", "occasion", "روز مادر", note="مناسب انگشتر زنانه"),
    Preset("fathers_day", "occasion", "روز پدر", note="مناسب انگشتر مردانه"),
)


def by_group() -> dict[str, list[Preset]]:
    return {group: [p for p in PRESETS if p.group == group] for group in GROUPS}


def menu() -> list[dict]:
    """JSON-ready menu for the website form."""
    return [
        {**asdict(p), "group_title": GROUPS[p.group], "aspect": p.aspect, "needs": list(p.needs)}
        for p in PRESETS
    ]


def markdown() -> str:
    risk_fa = {"low": "کم", "medium": "متوسط", "high": "زیاد"}
    lines = [
        "# فهرست مسیرهای آماده برای انگشتر",
        "",
        "هر مسیر یک صحنه در `gold_imagegen/prompts.py` است (کلید یکسان). «ریسک» یعنی احتمال اینکه مدل طرح را کمی عوض کند.",
        "ستون «نسخهٔ دقیق» مسیر معادلی است که پیکسل‌های اصلی کالا را دست‌نخورده نگه می‌دارد.",
        "",
    ]
    for group, items in by_group().items():
        lines += [f"## {GROUPS[group]}", "", "| مسیر | کلید | نسبت | ورودی لازم | ریسک | نسخهٔ دقیق | توضیح |", "|---|---|---|---|---|---|---|"]
        for p in items:
            needs = "، ".join(NEEDS[n] for n in p.needs) or "—"
            lines.append(f"| {p.title} | `{p.key}` | {p.aspect} | {needs} | {risk_fa[p.risk]} | {p.exact or '—'} | {p.note} |")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args(argv)
    if args.json:
        print(json.dumps(menu(), ensure_ascii=False, indent=2))
    elif args.markdown:
        print(markdown())
    else:
        for group, items in by_group().items():
            print(f"\n{GROUPS[group]}")
            for p in items:
                needs = f"  [نیاز: {', '.join(p.needs)}]" if p.needs else ""
                print(f"  {p.key:22} {p.aspect:5} {p.risk:7} {p.title}{needs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
