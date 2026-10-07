import asyncio
import json

from gold_imagegen.compare import ModelRun, run_comparison, write_index
from gold_imagegen.providers import EditRequest, EditResult, ProviderError


class FakeProvider:
    def __init__(self, model, cost, fail=False):
        self.model, self.cost, self.fail, self.closed = model, cost, fail, False

    async def edit(self, req):
        if self.fail:
            raise ProviderError(f"{self.model}: boom")
        return EditResult(b"img-" + self.model.encode(), "image/png", self.model, 1.0, self.cost)

    async def aclose(self):
        self.closed = True


def _run(models, tmp_path, max_cost, fail=()):
    made = {}

    def make(model):
        made[model] = FakeProvider(model, 0.6, fail=model in fail)
        return made[model]

    runs = asyncio.run(run_comparison(models, EditRequest(prompt="p"), tmp_path, make, max_cost))
    return runs, made


def test_writes_one_file_per_model_and_closes_providers(tmp_path):
    runs, made = _run(["a/x", "b/y"], tmp_path, max_cost=10)
    assert [r.ok for r in runs] == [True, True]
    assert (tmp_path / "a__x.png").read_bytes() == b"img-a/x"
    assert all(p.closed for p in made.values())


def test_budget_guard_skips_remaining_models(tmp_path):
    runs, made = _run(["a/x", "b/y", "c/z"], tmp_path, max_cost=1.0)
    assert [r.ok for r in runs] == [True, True, False]
    assert "budget" in runs[2].error
    assert "c/z" not in made


def test_failure_is_recorded_and_run_continues(tmp_path):
    runs, made = _run(["a/x", "b/y"], tmp_path, max_cost=10, fail={"a/x"})
    assert [r.ok for r in runs] == [False, True]
    assert made["a/x"].closed


def test_index_escapes_html(tmp_path):
    runs = [ModelRun("m/<script>", False, error="<b>bad</b>")]
    write_index(tmp_path, "task", "prompt <x>", ["input_1.jpg"], runs)
    page = (tmp_path / "index.html").read_text()
    assert "<script>" not in page and "&lt;script&gt;" in page
    json.dumps([r.__dict__ for r in runs])
