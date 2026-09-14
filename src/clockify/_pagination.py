from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterator


@dataclass(frozen=True, slots=True)
class Page[T]:
    items: list[T]
    page: int
    page_size: int


def paginate[T](fetch: Callable[[int], Page[T]], *, start_page: int = 1) -> Iterator[T]:
    number = start_page
    while True:
        page = fetch(number)
        yield from page.items
        if len(page.items) < page.page_size:
            return
        number += 1
