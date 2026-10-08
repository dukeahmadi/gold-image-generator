import io

import pytest
from PIL import Image

from gold_imagegen import cutout, plates
from gold_imagegen.render import main, render_all


def _cutout(w=60, h=40):
    img = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    img.paste(Image.new("RGBA", (w, h), (200, 160, 40, 255)), (10, 10))
    return img


def _plate_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (200, 200), (220, 220, 215)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_pixel_only_types_produce_one_image_per_photo_and_color():
    out = render_all(
        {"a": _cutout(), "b": _cutout(50, 50)}, ["white", "solid", "set"], colors=["navy", "#112233"]
    )
    assert sorted(out) == [
        "a_solid-112233.png", "a_solid-navy.png", "a_white.png",
        "b_solid-112233.png", "b_solid-navy.png", "b_white.png",
        "set_112233.png", "set_navy.png",
    ]
    for image in out.values():
        assert image.mode == "RGB" and image.width == image.height


def test_plate_types_need_plates(tmp_path):
    empty = tmp_path
    with pytest.raises(ValueError, match="--plates is required"):
        render_all({"a": _cutout()}, ["scene"], colors=[])
    with pytest.raises(ValueError, match="no plates"):
        render_all({"a": _cutout()}, ["scene"], colors=[], plate_dir=empty)


def test_plate_types_use_matching_plates_only(tmp_path):
    plates.write_plate(tmp_path, "scene_silk_01", _plate_bytes(), "scene")
    plates.write_plate(tmp_path, "accessories_silk_roses_01", _plate_bytes(), "accessories")
    plates.write_plate(tmp_path, "display_ring_01", _plate_bytes(), "display_ring")
    out = render_all({"a": _cutout()}, ["scene", "display"], colors=[], plate_dir=tmp_path)
    assert sorted(out) == ["a_display_ring_01.png", "a_scene_silk_01.png"]


def _fake_cut_out(image, model):
    rgba = image.convert("RGBA")
    rgba.putalpha(Image.new("L", image.size, 255))
    return rgba


def _photo(tmp_path, name="ring.jpg"):
    path = tmp_path / name
    Image.new("RGB", (64, 48), (200, 160, 40)).save(path)
    return path


def test_cli_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setattr(cutout, "cut_out", _fake_cut_out)
    out = tmp_path / "out"
    code = main([str(_photo(tmp_path)), "--types", "white", "solid", "--colors", "navy", "--out", str(out)])
    assert code == 0
    assert sorted(p.name for p in out.iterdir()) == ["ring_solid-navy.png", "ring_white.png"]


def test_cli_rejects_a_bad_color_before_doing_any_work(tmp_path, monkeypatch):
    monkeypatch.setattr(cutout, "cut_out", lambda *a: pytest.fail("should not run"))
    assert main([str(_photo(tmp_path)), "--types", "solid", "--colors", "nope"]) == 1
