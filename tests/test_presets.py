import re

import pytest

from gold_imagegen import presets, prompts
from gold_imagegen.suite import main


def test_every_preset_is_a_scene_and_keys_are_unique():
    keys = [p.key for p in presets.PRESETS]
    assert len(keys) == len(set(keys)) == 29
    assert set(keys) <= set(prompts.SUITE_NAMES)


def test_groups_needs_and_risks_are_valid():
    for p in presets.PRESETS:
        assert p.group in presets.GROUPS and p.risk in presets.RISKS
        assert set(p.needs) <= set(presets.NEEDS)
        assert re.fullmatch(r"\d+:\d+", p.aspect) and p.title
    assert all(presets.by_group()[g] for g in presets.GROUPS)


@pytest.mark.parametrize("preset", presets.PRESETS, ids=lambda p: p.key)
def test_every_preset_prompt_formats_with_defaults(preset):
    text = prompts.suite_prompt(preset.key, item="ring", brief="B.", roles="R.")
    assert "{" not in text and "B." in text
    assert ("TWO real rings" in text) == (preset.key in prompts.PAIR_SCENES)


def test_the_user_selected_catalog_is_complete():
    wanted = {"white_catalog", "macro_stone", "macro_ornament", "coin_scale", "ruler_scale", "hand_flat", "hand_fist",
              "hand_resting", "woman_hand_flowers", "couple_rings_set", "display_box", "proposal_box",
              "studio_marble", "persian_tile", "persian_rug", "copper_tray", "hafez_book", "tea_nabat",
              "pomegranate_saffron", "nowruz", "yalda", "sepandarmazgan", "mothers_day", "fathers_day"}
    assert wanted <= {p.key for p in presets.PRESETS}


def test_scale_note_states_a_true_size_only_when_given():
    assert "times as wide" in prompts.suite_prompt("coin_scale", item="ring", head_width_mm=12)
    assert "24 mm" in prompts.suite_prompt("coin_scale", item="ring", head_width_mm=12)
    assert "true size" in prompts.suite_prompt("coin_scale", item="ring")  # asks for it, states no number
    assert "ruler's ticks" in prompts.suite_prompt("ruler_scale", item="ring", head_width_mm=14)
    assert "about twice" in prompts.suite_prompt("coin_scale", item="ring")


def test_woman_scene_forces_a_woman_s_manicured_hand():
    text = prompts.suite_prompt("woman_hand_flowers", item="ring", wearer="a man's")
    assert "a woman's hand" in text and "nude manicure" in text and "exactly five fingers" in text
    assert "natural short clean nails" not in text


def test_proposal_scene_holds_the_box_and_does_not_wear_the_ring():
    text = prompts.suite_prompt("proposal_box", item="ring", wearer="a woman's")
    assert "marriage-proposal" in text and "a man's hand" in text
    assert "no face is visible" in text and "fits the finger" not in text


def test_the_menu_is_json_ready_and_persian():
    menu = presets.menu()
    assert len(menu) == 29 and all(m["title"] and m["group_title"] for m in menu)
    assert next(m for m in menu if m["key"] == "hand_fist")["needs"] == ["gender", "skin_tone"]
    assert "|" in presets.markdown()


def test_suite_group_selects_the_presets_of_that_group(tmp_path, capsys):
    photo = tmp_path / "p.jpg"
    photo.write_bytes(b"x")
    assert main(["--images", str(photo), "--group", "persian", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert out.count("\n[") == 6 and "[tea_nabat]" in out and "[nowruz]" not in out
    with pytest.raises(SystemExit):
        main(["--images", str(photo), "--group", "persian", "--prompts", "nowruz", "--dry-run"])
