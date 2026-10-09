import asyncio
import json

import pytest
from PIL import Image

from gold_imagegen import cutout, prompts
from gold_imagegen.providers import EditResult, ProviderError
from gold_imagegen.suite import run_suite, write_index


class FakeProvider:
    def __init__(self, model, cost=0.1, reject_aspect=False, fail=False):
        self.model, self.cost, self.reject_aspect, self.fail = model, cost, reject_aspect, fail
        self.requests = []

    async def edit(self, req):
        self.requests.append(req)
        if self.fail:
            raise ProviderError("boom", 500)
        if self.reject_aspect and req.aspect_ratio:
            raise ProviderError("unsupported aspect_ratio", 400)
        return EditResult(b"img-" + self.model.encode(), "image/png", self.model, 1.0, self.cost)

    async def aclose(self):
        return None


def _run(tmp_path, models, names=("a", "b"), max_cost=10.0, **provider_kw):
    made = {}

    def make(model):
        made[model] = FakeProvider(model, **provider_kw)
        return made[model]

    texts = {n: f"prompt {n}" for n in names}
    runs = asyncio.run(run_suite(models, texts, (b"i1", b"i2"), tmp_path, make, max_cost=max_cost, concurrency=2))
    return runs, made


def test_suite_prompt_carries_brief_roles_and_the_keep_exactly_block():
    text = prompts.suite_prompt(
        "hero_3d", item="ring", brief="Square black stone.", roles="Image 1 is the front."
    )
    assert "ring" in text and "Square black stone." in text and "Image 1 is the front." in text
    assert "never replace a motif with a different one" in text
    assert "{" not in text


@pytest.mark.parametrize("name", prompts.SUITE_NAMES)
def test_every_suite_prompt_formats(name):
    assert "{" not in prompts.suite_prompt(name, item="ring", brief="b", roles="r")


def test_suite_prompt_rejects_unknown_names():
    with pytest.raises(ValueError):
        prompts.suite_prompt("nope")


def test_suite_writes_one_file_per_prompt_and_model(tmp_path):
    runs, _ = _run(tmp_path, ["v/x", "w/y"])
    assert len(runs) == 4 and all(r.ok for r in runs)
    assert (tmp_path / "a" / "v__x.png").read_bytes() == b"img-v/x"
    assert {r.prompt_name for r in runs} == {"a", "b"}
    assert all(r.prompt == f"prompt {r.prompt_name}" and r.cost_usd == 0.1 for r in runs)


def test_every_call_gets_all_reference_images(tmp_path):
    _, made = _run(tmp_path, ["v/x"])
    assert all(req.images == (b"i1", b"i2") for req in made["v/x"].requests)


def test_budget_guard_skips_calls_once_spent(tmp_path):
    runs, _ = _run(tmp_path, ["v/x"], names=("a", "b", "c", "d"), max_cost=0.15)
    ok = [r for r in runs if r.ok]
    skipped = [r for r in runs if not r.ok]
    assert len(ok) == 2 and len(skipped) == 2  # two calls ($0.10 each) reach the limit; concurrency is 2
    assert all("budget" in r.error for r in skipped)


def test_rejected_aspect_ratio_is_retried_without_it(tmp_path):
    runs, made = _run(tmp_path, ["v/x"], names=("a",), reject_aspect=True)
    assert runs[0].ok and "retried without" in runs[0].note
    assert [r.aspect_ratio for r in made["v/x"].requests] == ["1:1", None]


def test_quality_is_sent_and_dropped_together_with_the_aspect_on_a_400(tmp_path):
    made = {}

    def make(model):
        made[model] = FakeProvider(model, reject_aspect=True)
        return made[model]

    runs = asyncio.run(
        run_suite(["v/x"], {"a": "p"}, (b"i",), tmp_path, make, max_cost=10, aspect_ratio="1:1", quality="high")
    )
    assert runs[0].ok and "retried without" in runs[0].note
    assert [(r.aspect_ratio, r.quality) for r in made["v/x"].requests] == [("1:1", "high"), (None, None)]


def test_failures_are_recorded_not_raised(tmp_path):
    runs, _ = _run(tmp_path, ["v/x"], names=("a",), fail=True)
    assert not runs[0].ok and "boom" in runs[0].error


def test_index_lists_prompt_model_and_cost(tmp_path):
    runs, _ = _run(tmp_path, ["v/<x>"], names=("a",))
    write_index(tmp_path, ["input_1.png"], runs)
    page = (tmp_path / "index.html").read_text()
    assert "prompt a" in page and "$0.1000" in page and "&lt;x&gt;" in page
    json.dumps([r.__dict__ for r in runs])


def test_crop_around_product_is_square_exact_and_inside_the_photo():
    photo = Image.new("RGB", (100, 200), (10, 10, 10))
    photo.paste(Image.new("RGB", (20, 30), (200, 150, 40)), (60, 40))  # product at x 60-80, y 40-70
    cut = Image.new("RGBA", photo.size, (0, 0, 0, 0))
    cut.paste(Image.new("RGBA", (20, 30), (200, 150, 40, 255)), (60, 40))
    crop = cutout.crop_around_product(photo, cut, margin=0.5)
    assert crop.width == crop.height == 60  # 30 * (1 + 2 * 0.5)
    assert crop.getpixel((30, 30)) == (200, 150, 40)  # the product is in the middle, unchanged
    edge = Image.new("RGBA", photo.size, (0, 0, 0, 0))
    edge.paste(Image.new("RGBA", (20, 20), (1, 2, 3, 255)), (80, 180))  # product in the corner
    assert cutout.crop_around_product(photo, edge, margin=2).size == (100, 100)  # clamped to the photo


HAND_PROMPTS = [n for n in prompts.SUITE_NAMES if n.startswith("hand_")]


def test_there_are_four_hand_poses():
    assert HAND_PROMPTS == ["hand_flat", "hand_fist", "hand_resting", "hand_raised"]


@pytest.mark.parametrize("name", HAND_PROMPTS)
def test_hand_prompts_pin_down_anatomy_scale_and_the_design(name):
    text = prompts.suite_prompt(name, item="ring", brief="B.", roles="R.")
    assert "a man's hand" in text and "natural medium (wheat)" in text
    assert "exactly five fingers" in text and "realistic scale" in text
    assert "no other jewelry" in text and "no face is visible" in text
    assert "never replace a motif with a different one" in text
    assert "{" not in text


def test_hand_prompts_follow_wearer_and_skin():
    text = prompts.suite_prompt("hand_flat", item="ring", wearer="a woman's", skin="light")
    assert "a woman's hand" in text and "Skin tone: light" in text
