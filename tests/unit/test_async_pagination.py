from __future__ import annotations

from clockify._pagination import Page  # ruff: ignore[import-private-name]
from clockify._pagination import apaginate  # ruff: ignore[import-private-name]


class _Fetcher:
    def __init__(self, pages):
        self._pages = pages
        self.calls = []

    async def __call__(self, page):
        self.calls.append(page)
        return self._pages[page]


async def test_full_page_then_short_page_yields_everything():
    # Arrange
    fetch = _Fetcher({1: Page(items=[1, 2], page=1, page_size=2), 2: Page(items=[3], page=2, page_size=2)})
    # Act
    items = [item async for item in apaginate(fetch)]
    # Assert
    assert items == [1, 2, 3]
    assert fetch.calls == [1, 2]


async def test_empty_first_page_yields_nothing():
    # Arrange
    fetch = _Fetcher({1: Page(items=[], page=1, page_size=2)})
    # Act
    items = [item async for item in apaginate(fetch)]
    # Assert
    assert items == []
    assert fetch.calls == [1]


async def test_start_page_is_honoured():
    # Arrange
    fetch = _Fetcher({3: Page(items=[9], page=3, page_size=2)})
    # Act
    items = [item async for item in apaginate(fetch, start_page=3)]
    # Assert
    assert items == [9]
