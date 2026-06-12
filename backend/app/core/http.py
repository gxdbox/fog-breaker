from __future__ import annotations

import httpx
from app.core.config import settings

_proxy = settings.HTTP_PROXY.strip() if settings.HTTP_PROXY else None


def get_client(timeout: int = 30, extra_headers: dict | None = None) -> httpx.Client:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; FogBreaker/1.0)"}
    if extra_headers:
        headers.update(extra_headers)
    return httpx.Client(proxy=_proxy, timeout=timeout, headers=headers, follow_redirects=True)


def get_async_client(timeout: int = 30, extra_headers: dict | None = None) -> httpx.AsyncClient:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; FogBreaker/1.0)"}
    if extra_headers:
        headers.update(extra_headers)
    return httpx.AsyncClient(proxy=_proxy, timeout=timeout, headers=headers, follow_redirects=True)
