import asyncio
import io
import json

import pytest
from PIL import Image, ImageChops

from gold_imagegen import plates, prompts
from gold_imagegen.make_plates import generate_plates
from gold_imagegen.providers import EditResult, ProviderError

PLATE_COLOR = (220, 220, 215)
RED = (255, 0, 0, 255)


def _png(size=(200, 200), color=PLATE_COLOR):
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    return buffer.getvalue()


def _plate(**kw):
    return plates.Plate(Image.new("RGB", (200, 200), PLATE_COLOR), **kw)


def _red(w, h, pad=10):
    img = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    img.paste(Image.new("RGBA", (w, h), RED), (pad, pad))
    return img


def _diff_box(out, plate):
    return ImageChops.difference(out, plate.image).getbbox()


def test_write_and_load_plate_roundtrip(tmp_path):
    path = plates.write_plate(tmp_path, "scene_silk_01", _png(), "scene")
    plate = plates.load_plate(path)
    assert plate.kind == "scene" and plate.name == "scene_silk_01"
    assert plate.slot == plates.DEFAULT_SLOTS["scene"] and plate.image.size == (200, 200)


@pytest.mark.parametrize(
    "meta",
    [{"kind": "nope"}, {"slot": [0.5, 0.5, 0.9, 0.9]}, {"light": [0, 0]}, {"occlude_below": 1.5}],
)
def test_load_plate_rejects_invalid_metadata(tmp_path, meta):
    path = plates.write_plate(tmp_path, "p", _png(), "scene")
    data = json.loads(path.read_text())
    data.update(meta)
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        plates.load_plate(path)


def test_iter_plates_filters_by_kind(tmp_path):
    plates.write_plate(tmp_path, "a", _png(), "scene")
    plates.write_plate(tmp_path, "b", _png(), "display_ring")
    assert [p.name for p in plates.iter_plates(tmp_path, ("display_ring",))] == ["b"]
    assert len(plates.iter_plates(tmp_path)) == 2


def test_product_is_centered_in_the_slot_unscaled():
    plate = _plate(slot=(0.2, 0.2, 0.6, 0.6))  # slot 40..160
    out = plates.place_on_plate(_red(60, 40), plate, shadow=False)
    assert _diff_box(out, plate) == (70, 80, 130, 120)
    assert out.getpixel((0, 0)) == PLATE_COLOR


def test_product_larger_than_the_slot_is_shrunk_to_fit():
    plate = _plate(slot=(0.2, 0.2, 0.6, 0.6))
    out = plates.place_on_plate(_red(400, 100), plate, shadow=False)
    assert _diff_box(out, plate) == (40, 85, 160, 115)  # 400x100 -> 120x30


def test_product_is_never_upscaled():
    plate = _plate(slot=(0.2, 0.2, 0.6, 0.6))
    out = plates.place_on_plate(_red(20, 10), plate, shadow=False)
    assert _diff_box(out, plate) == (90, 95, 110, 105)


def test_anchor_places_the_product_at_the_bottom_or_top_of_the_slot():
    kw = dict(slot=(0.2, 0.2, 0.6, 0.6))  # slot 40..160
    bottom = plates.place_on_plate(_red(60, 40), _plate(anchor="bottom", **kw), shadow=False)
    top = plates.place_on_plate(_red(60, 40), _plate(anchor="top", **kw), shadow=False)
    assert _diff_box(bottom, _plate()) == (70, 120, 130, 160)
    assert _diff_box(top, _plate()) == (70, 40, 130, 80)


def test_anchor_is_validated_and_defaults_follow_the_kind(tmp_path):
    path = plates.write_plate(tmp_path, "ring", _png(), "display_ring")
    assert plates.load_plate(path).anchor == "bottom"
    assert plates.load_plate(plates.write_plate(tmp_path, "card", _png(), "display_earrings")).anchor == "top"
    assert plates.load_plate(plates.write_plate(tmp_path, "m", _png(), "scene")).anchor == "center"
    data = json.loads(path.read_text())
    data["anchor"] = "left"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="anchor"):
        plates.load_plate(path)


def test_occlude_below_hides_the_lower_part_of_the_product():
    plate = _plate(slot=(0.3, 0.3, 0.4, 0.4), occlude_below=0.5)  # product 80..120, line at y=100
    out = plates.place_on_plate(_red(40, 40), plate, shadow=False)
    assert out.getpixel((100, 90))[:3] == RED[:3]
    assert out.getpixel((100, 110)) == PLATE_COLOR


def test_occlude_line_above_the_product_is_rejected():
    plate = _plate(slot=(0.3, 0.3, 0.4, 0.4), occlude_below=0.2)
    with pytest.raises(ValueError, match="hides the whole product"):
        plates.place_on_plate(_red(40, 40), plate)


def test_shadow_falls_away_from_the_light():
    plate = _plate(slot=(0.3, 0.3, 0.4, 0.4), light=(1, 1))  # product 80..120
    out = plates.place_on_plate(_red(40, 40), plate, shadow=True)
    assert out.getpixel((121, 121))[0] < out.getpixel((78, 78))[0]


# --- plate prompts and generation -------------------------------------------------------------
def test_plate_prompts_ban_jewelry_and_keep_the_center_free():
    for kind in prompts.PLATE_KINDS:
        text = prompts.plate_prompt(kind, "silk", "roses")
        assert "No jewelry" in text
    assert "center of the frame is completely empty" in prompts.plate_prompt("scene")
    assert "never in the center" in prompts.plate_prompt("accessories", "silk", "roses")


def test_plate_prompt_rejects_unknown_values():
    for args in (("nope",), ("scene", "nope"), ("accessories", "silk", "nope")):
        with pytest.raises(ValueError):
            prompts.plate_prompt(*args)


class FakeProvider:
    def __init__(self, cost=0.04, fail=False):
        self.cost, self.fail = cost, fail

    async def edit(self, req):
        if self.fail:
            raise ProviderError("boom")
        return EditResult(_png(), "image/png", "fake", 0.1, self.cost)

    async def aclose(self):
        return None


def _generate(tmp_path, provider, count=3, max_cost=1.0, style="silk"):
    return asyncio.run(
        generate_plates(
            lambda: provider, kind="scene", style=style, props=None, count=count,
            out_dir=tmp_path, max_cost=max_cost,
        )
    )


def test_generate_plates_writes_loadable_plates(tmp_path):
    written, spent, errors = _generate(tmp_path, FakeProvider())
    assert [p.stem for p in written] == ["scene_silk_01", "scene_silk_02", "scene_silk_03"]
    assert not errors and spent == pytest.approx(0.12)
    assert all(plates.load_plate(p).kind == "scene" for p in written)
    generation = json.loads(written[0].read_text())["generation"]
    assert generation["cost_usd"] == 0.04 and generation["model"] == "fake"
    assert generation["prompt"] == prompts.plate_prompt("scene", "silk")


def test_generate_plates_stops_at_the_budget(tmp_path):
    written, _, errors = _generate(tmp_path, FakeProvider(cost=0.6), count=4)
    assert len(written) == 2 and "budget" in errors[-1]


def test_generate_plates_records_provider_errors(tmp_path):
    written, _, errors = _generate(tmp_path, FakeProvider(fail=True), count=2)
    assert not written and errors == ["boom", "boom"]


def test_generate_plates_numbering_continues(tmp_path):
    _generate(tmp_path, FakeProvider(), count=2)
    written, _, _ = _generate(tmp_path, FakeProvider(), count=1)
    assert [p.stem for p in written] == ["scene_silk_03"]
