import pytest

from gold_imagegen import prompts


def test_white_background_preserves_product():
    text = prompts.white_background("gold ring")
    assert "#FFFFFF" in text
    assert prompts.KEEP_REST in text


@pytest.mark.parametrize("jewelry,where", sorted(prompts.PLACEMENT.items()))
def test_on_model_mentions_placement(jewelry, where):
    text = prompts.on_model(jewelry)
    assert jewelry in text and where in text
    assert "image 1" in text and "image 2" in text


def test_on_model_rejects_unknown_jewelry():
    with pytest.raises(ValueError):
        prompts.on_model("crown")
