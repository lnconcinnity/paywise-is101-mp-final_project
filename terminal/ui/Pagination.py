class Page:
    def __init__(self, name, *widgets, onEnter=None, onExit=None):
        self.name = name
        self.widgets = list(widgets)
        self.onEnter = onEnter
        self.onExit = onExit

    def enter(self):
        if self.onEnter:
            self.onEnter()

    def exit(self):
        if self.onExit:
            self.onExit()

    def poll(self):
        for w in self.widgets:
            w.poll()

    def draw(self):
        for w in self.widgets:
            w.draw()


class Pagination:
    def __init__(self, *pages, wrap=False):
        assert pages, "Pagination needs at least one Page"
        for p in pages:
            assert isinstance(p, Page), f"expected Page, got {type(p).__name__}"

        names = [p.name for p in pages]
        assert len(set(names)) == len(names), f"duplicate page names: {names}"

        self.pages = list(pages)
        self.wrap = wrap
        self.index = 0
        self._by_name = {p.name: i for i, p in enumerate(self.pages)}

        self.pages[0].enter()

    @property
    def current(self):
        return self.pages[self.index]

    def goto(self, target):
        if isinstance(target, str):
            if target not in self._by_name:
                raise KeyError(
                    f"unknown page {target!r}; known pages: {list(self._by_name)}"
                )
            i = self._by_name[target]
        else:
            if not 0 <= target < len(self.pages):
                raise IndexError(
                    f"page index {target} out of range (0..{len(self.pages) - 1})"
                )
            i = target

        if i == self.index:
            return False

        self.current.exit()
        self.index = i
        self.current.enter()
        return True

    def next(self):
        return self._step(1)

    def back(self):
        return self._step(-1)

    def _step(self, delta):
        n = len(self.pages)
        i = self.index + delta
        if self.wrap:
            i %= n
        elif not 0 <= i < n:
            return False
        return self.goto(i)

    def poll(self):
        self.current.poll()

    def draw(self):
        self.current.draw()