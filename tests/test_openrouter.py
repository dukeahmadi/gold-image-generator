import asyncio
import base64
import json

import httpx
import pytest

from gold_imagegen.providers import EditRequest, OpenRouterProvider, ProviderError

IMG = b"\x89PNG-fake-bytes"


def _ok(cost=0.04):
    return httpx.Response(
        200,
        json={
            "data": [{"b64_json": base64.b64encode(IMG).decode(), "media_type": "image/png"}],
            "usage": {"cost": cost},
        },
    )


def _provider(handler, **kw):
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return OpenRouterProvider("sk-test-secret", "vendor/model", client=client, retry_delay=0, **kw)


def test_edit_success_builds_payload_and_parses_result():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["authorization"]
        seen["body"] = json.loads(request.content)
        return _ok(0.077)

    req = EditRequest(prompt="p", images=(b"one", b"two"), quality="high")
    result = asyncio.run(_provider(handler).edit(req))

    assert seen["url"] == "https://openrouter.ai/api/v1/images"
    assert seen["auth"] == "Bearer sk-test-secret"
    assert seen["body"]["model"] == "vendor/model"
    assert seen["body"]["quality"] == "high"
    assert "aspect_ratio" not in seen["body"]
    assert seen["body"]["input_references"] == [
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(b"one").decode()}},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(b"two").decode()}},
    ]
    assert result.image == IMG
    assert result.media_type == "image/png"
    assert result.cost_usd == 0.077


def test_retries_on_429_then_succeeds():
    calls = []

    def handler(request):
        calls.append(1)
        return httpx.Response(429, text="slow down") if len(calls) == 1 else _ok()

    result = asyncio.run(_provider(handler, max_retries=1).edit(EditRequest(prompt="p")))
    assert len(calls) == 2
    assert result.image == IMG


def test_client_error_is_not_retried_and_hides_key():
    calls = []

    def handler(request):
        calls.append(1)
        return httpx.Response(402, text="insufficient credits")

    with pytest.raises(ProviderError) as info:
        asyncio.run(_provider(handler, max_retries=3).edit(EditRequest(prompt="p")))
    assert len(calls) == 1
    assert info.value.status == 402
    assert "sk-test-secret" not in str(info.value)


def test_gives_up_after_retries():
    def handler(request):
        return httpx.Response(503, text="down")

    with pytest.raises(ProviderError) as info:
        asyncio.run(_provider(handler, max_retries=1).edit(EditRequest(prompt="p")))
    assert info.value.status == 503


def test_missing_image_in_response():
    def handler(request):
        return httpx.Response(200, json={"data": []})

    with pytest.raises(ProviderError, match="no image"):
        asyncio.run(_provider(handler).edit(EditRequest(prompt="p")))


def test_reference_images_keep_their_real_mime_type():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["urls"] = [r["image_url"]["url"] for r in json.loads(request.content)["input_references"]]
        return _ok()

    jpeg, webp = b"\xff\xd8\xff\xe0rest", b"RIFF\x00\x00\x00\x00WEBPrest"
    asyncio.run(_provider(handler).edit(EditRequest(prompt="p", images=(jpeg, webp))))
    assert [u.split(";")[0] for u in seen["urls"]] == ["data:image/jpeg", "data:image/webp"]
