from __future__ import annotations

import asyncio
import time

from .. import cutout
from .base import EditRequest, EditResult, ProviderError


class LocalCutoutProvider:
    """White-background "edit" done locally: cut the product out, place it on white.

    Implements the same interface as the API providers so it can be compared side by side
    with generative models. Costs nothing per call; only the first image is used.
    """

    def __init__(self, model: str | None = None, shadow: bool = True) -> None:
        self.model = model or cutout.DEFAULT_MODEL
        self._shadow = shadow

    async def edit(self, req: EditRequest) -> EditResult:
        if not req.images:
            raise ProviderError("local cutout needs the product photo as the first image")
        started = time.monotonic()
        try:
            result = await asyncio.to_thread(
                cutout.process, req.images[0], model=self.model, shadow=self._shadow
            )
        except Exception as exc:  # model download, onnx runtime and decode errors differ widely
            raise ProviderError(f"local/cutout:{self.model}: {type(exc).__name__}: {exc}") from exc
        return EditResult(
            image=cutout.to_png(result.white),
            media_type="image/png",
            model=f"local/cutout:{self.model}",
            elapsed_s=time.monotonic() - started,
            cost_usd=0.0,
        )

    async def aclose(self) -> None:
        return None
