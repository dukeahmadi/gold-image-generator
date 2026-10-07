"""List OpenRouter image models. Public endpoint; no API key needed.

    python -m gold_imagegen.list_models            # editable models only
    python -m gold_imagegen.list_models --all
"""
from __future__ import annotations

import argparse

import httpx

URL = "https://openrouter.ai/api/v1/models"


def _per_million(value: str | None) -> str:
    try:
        return f"${float(value) * 1_000_000:.2f}" if value not in (None, "") else "-"
    except ValueError:
        return "-"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--all", action="store_true", help="include text-to-image-only models")
    args = parser.parse_args()

    resp = httpx.get(URL, params={"output_modalities": "image"}, timeout=30)
    resp.raise_for_status()
    rows = []
    for m in resp.json().get("data", []):
        inputs = m.get("architecture", {}).get("input_modalities") or []
        editable = "image" in inputs
        if not (editable or args.all):
            continue
        pricing = m.get("pricing") or {}
        out_price = pricing.get("image_output") or pricing.get("image_token")
        rows.append((m["id"], "edit" if editable else "t2i", _per_million(out_price)))

    rows.sort()
    width = max((len(r[0]) for r in rows), default=10)
    print(f"{'model':<{width}}  mode  $/M image-output tokens")
    for model_id, mode, out_price in rows:
        print(f"{model_id:<{width}}  {mode:<4}  {out_price:>10}")
    print(
        "\nPer-image cost depends on resolution/quality (token-based); the compare tool "
        "records the real cost OpenRouter reports for each call."
    )


if __name__ == "__main__":
    main()
