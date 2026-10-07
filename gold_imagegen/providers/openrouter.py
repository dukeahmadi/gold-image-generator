from __future__ import annotations

import asyncio
import base64
import time
from typing import Any

import httpx

from .base import EditRequest, EditResult, ProviderError

BASE_URL = "https://openrouter.ai/api/v1"
RETRY_STATUS = {429, 500, 502, 503, 504}


class OpenRouterProvider:
    """Image generation/editing through OpenRouter's `POST /api/v1/images`.

    Reference images go in `input_references` as base64. The target model must list
    "image" in its input modalities (see `python -m gold_imagegen.list_models`).
    Optional parameters (aspect_ratio, resolution, quality) are only sent when set,
    because not every model accepts every parameter.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        client: httpx.AsyncClient | None = None,
        timeout: float = 180.0,
        max_retries: int = 2,
        retry_delay: float = 2.0,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.model = model
        self._api_key = api_key
        self._client = client
        self._owns_client = client is None
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._extra = dict(extra or {})

    async def __aenter__(self) -> OpenRouterProvider:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._client is not None and self._owns_client:
            await self._client.aclose()
            self._client = None

    def _payload(self, req: EditRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {"model": self.model, "prompt": req.prompt, "n": 1}
        if req.images:
            payload["input_references"] = [
                {"data": base64.b64encode(img).decode("ascii")} for img in req.images
            ]
        for name in ("aspect_ratio", "resolution", "quality"):
            value = getattr(req, name)
            if value:
                payload[name] = value
        payload.update(self._extra)
        return payload

    async def edit(self, req: EditRequest) -> EditResult:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        payload = self._payload(req)
        headers = {"Authorization": f"Bearer {self._api_key}"}
        started = time.monotonic()

        last_error: ProviderError | None = None
        for attempt in range(self._max_retries + 1):
            if attempt:
                await asyncio.sleep(self._retry_delay * 2 ** (attempt - 1))
            try:
                resp = await self._client.post(
                    f"{BASE_URL}/images", json=payload, headers=headers
                )
            except httpx.TransportError as exc:
                last_error = ProviderError(f"{self.model}: network error: {exc!r}")
                continue
            if resp.status_code in RETRY_STATUS:
                last_error = ProviderError(
                    f"{self.model}: HTTP {resp.status_code}: {resp.text[:300]}",
                    resp.status_code,
                )
                continue
            if resp.status_code >= 400:
                raise ProviderError(
                    f"{self.model}: HTTP {resp.status_code}: {resp.text[:500]}",
                    resp.status_code,
                )
            return self._parse(resp, started)

        assert last_error is not None
        raise last_error

    def _parse(self, resp: httpx.Response, started: float) -> EditResult:
        try:
            body = resp.json()
            item = body["data"][0]
            image = base64.b64decode(item["b64_json"])
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            snippet = resp.text[:300]
            raise ProviderError(
                f"{self.model}: no image in response ({exc!r}): {snippet}"
            ) from exc
        cost = (body.get("usage") or {}).get("cost")
        return EditResult(
            image=image,
            media_type=item.get("media_type") or "image/png",
            model=self.model,
            elapsed_s=time.monotonic() - started,
            cost_usd=float(cost) if cost is not None else None,
        )

