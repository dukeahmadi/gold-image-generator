import asyncio
import io
import json

import pytest
from PIL import Image

from gold_imagegen import cutout
from gold_imagegen.compare import main, slug
from gold_imagegen.providers import EditRequest, ProviderError
from gold_imagegen.providers.local_cutout import LocalCutoutProvider


def _fake_cut_out(image, model):
    rgba = image.convert("RGBA")
    rgba.putalpha(Image.new("L", image.size, 255))
    return rgba


def _jpeg(size=(64, 48)):
    buffer = io.BytesIO()
    Image.new("RGB", size, (200, 160, 40)).save(buffer, format="JPEG")
    return buffer.getvalue()


def test_slug_is_filename_safe():
    assert slug("local/cutout:birefnet-dis") == "local__cutout_birefnet-dis"


def test_provider_returns_white_png_at_zero_cost(monkeypatch):
    monkeypatch.setattr(cutout, "cut_out", _fake_cut_out)
    result = asyncio.run(LocalCutoutProvider("m").edit(EditRequest(prompt="x", images=(_jpeg(),))))
    image = Image.open(io.BytesIO(result.image))
    assert result.cost_usd == 0.0
    assert result.model == "local/cutout:m"
    assert image.format == "PNG" and image.width == image.height


def test_provider_needs_a_product_photo():
    with pytest.raises(ProviderError, match="product photo"):
        asyncio.run(LocalCutoutProvider().edit(EditRequest(prompt="x")))


def test_provider_wraps_model_errors(monkeypatch):
    def boom(image, model):
        raise RuntimeError("weights missing")

    monkeypatch.setattr(cutout, "cut_out", boom)
    with pytest.raises(ProviderError, match="weights missing"):
        asyncio.run(LocalCutoutProvider().edit(EditRequest(prompt="x", images=(_jpeg(),))))


def test_compare_runs_local_cutout_without_api_key(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(cutout, "cut_out", _fake_cut_out)
    product = tmp_path / "ring.jpg"
    product.write_bytes(_jpeg())
    code = main([
        "--task", "white_background", "--product", str(product),
        "--models", "local/cutout", "--out", str(tmp_path / "out"),
    ])
    assert code == 0
    (run_dir,) = (tmp_path / "out").iterdir()
    (result,) = json.loads((run_dir / "results.json").read_text())
    assert result["ok"] and result["cost_usd"] == 0.0
    assert (run_dir / "index.html").exists()


def test_local_cutout_is_rejected_for_on_model(tmp_path):
    photo = tmp_path / "p.jpg"
    photo.write_bytes(_jpeg())
    with pytest.raises(SystemExit):
        main([
            "--task", "on_model", "--product", str(photo), "--model-photo", str(photo),
            "--models", "local/cutout",
        ])
