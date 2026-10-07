from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ProviderError(RuntimeError):
    """An image provider call failed. `status` is the HTTP status if there was one."""

    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class EditRequest:
    prompt: str
    # Reference images in the order the prompt refers to them ("image 1", "image 2").
    images: tuple[bytes, ...] = ()
    aspect_ratio: str | None = None
    resolution: str | None = None
    quality: str | None = None


@dataclass(frozen=True)
class EditResult:
    image: bytes
    media_type: str
    model: str
    elapsed_s: float
    cost_usd: float | None = None


class ImageEditProvider(Protocol):
    async def edit(self, req: EditRequest) -> EditResult: ...

    async def aclose(self) -> None: ...
