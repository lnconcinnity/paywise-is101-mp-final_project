from typing import Callable

class Selection:
    def __init__(
        self,
        count: Callable[[], int],
        wrap: bool = False,
        skip: Callable[[int], bool] | None = None,
        on_change: Callable[[int, int], None] | None = None,
    ):
        self.count = count
        self.wrap = wrap
        self.skip = skip
        self.on_change = on_change
        first = self.first()
        self.index = first if first is not None else 0

    def can_select(self, i: int) -> bool:
        return 0 <= i < self.count() and not (self.skip and self.skip(i))

    def first(self) -> int | None:
        return next((i for i in range(self.count()) if self.can_select(i)), None)

    def last(self) -> int | None:
        return next((i for i in range(self.count() - 1, -1, -1) if self.can_select(i)), None)

    def _next(self, i: int, step: int) -> int:
        n = self.count()
        start = i
        for _ in range(n):
            j = i + step
            if self.wrap:
                j %= n
            elif not 0 <= j < n:
                return start
            i = j
            if self.can_select(i):
                return i
        return start

    def set(self, i: int) -> bool:
        if i == self.index or not self.can_select(i):
            return False
        old, self.index = self.index, i
        if self.on_change:
            self.on_change(old, i)
        return True

    def step(self, delta: int) -> bool:
        direction = 1 if delta > 0 else -1
        i = self.index
        for _ in range(abs(delta)):
            i = self._next(i, direction)
        return self.set(i)