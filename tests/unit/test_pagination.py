from __future__ import annotations

import pytest

from clockify._pagination import Page  # ruff: ignore[import-private-name]
from clockify._pagination import paginate  # ruff: ignore[import-private-name]


class _Fetcher:
    def __init__(self, pages):
        self._pages = pages
        self.calls = []

    def __call__(self, page):
        self.calls.append(page)
        return self._pages[page]


def test_full_page_then_short_page_yields_everything():
    # Arrange
    fetch = _Fetcher({1: Page(items=[1, 2], page=1, page_size=2), 2: Page(items=[3], page=2, page_size=2)})
    # Act
    items = list(paginate(fetch))
    # Assert
    assert items == [1, 2, 3]
    assert fetch.calls == [1, 2]


def test_empty_first_page_yields_nothing():
    # Arrange
    fetch = _Fetcher({1: Page(items=[], page=1, page_size=50)})
    # Act
    items = list(paginate(fetch))
    # Assert
    assert not items
    assert fetch.calls == [1]


def test_exact_multiple_requests_one_more_page_then_stops():
    # Arrange
    fetch = _Fetcher({
        1: Page(items=[1, 2], page=1, page_size=2),
        2: Page(items=[3, 4], page=2, page_size=2),
        3: Page(items=[], page=3, page_size=2),
    })
    # Act
    items = list(paginate(fetch))
    # Assert
    assert items == [1, 2, 3, 4]
    assert fetch.calls == [1, 2, 3]


def test_start_page_is_honored():
    # Arrange
    fetch = _Fetcher({4: Page(items=["a"], page=4, page_size=10)})
    # Act
    items = list(paginate(fetch, start_page=4))
    # Assert
    assert items == ["a"]
    assert fetch.calls == [4]


def test_iteration_is_lazy():
    # Arrange
    fetch = _Fetcher({1: Page(items=[1, 2], page=1, page_size=2), 2: Page(items=[3], page=2, page_size=2)})
    iterator = paginate(fetch)
    # Act
    before = list(fetch.calls)
    first = next(iterator)
    # Assert
    assert not before
    assert first == 1
    assert fetch.calls == [1]


def test_page_is_frozen():
    # Arrange
    page = Page(items=[1], page=1, page_size=1)
    # Act
    with pytest.raises(AttributeError) as excinfo:
        page.page = 2
    # Assert
    assert isinstance(excinfo.value, AttributeError)
    assert (page.items, page.page, page.page_size) == ([1], 1, 1)
