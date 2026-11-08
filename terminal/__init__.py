from time import sleep, perf_counter
from terminal.Renderer import Renderer
from terminal.InputHandler import InputHandler
from terminal.colors import *
from terminal.tui.Drawable import Drawable
from terminal.tui.TextInput import TextInput
from terminal.tui.TextLabel import TextLabel
from terminal.tui.Menu import Menu, MenuItem
from terminal.tui.Pagination import Pagination, Page
from terminal.tui.AbsoluteLayout import AbsoluteLayout
from terminal.tui.StackLayout import StackLayout

class Scheduler:
    TARGET_FPS = 30
    INPUT = InputHandler(capture_signals=True)
    RENDERER = Renderer()
    running: bool = False
    _roots: list[Drawable] = []

    def __new__(cls, *args, **kwargs):
        raise TypeError("Scheduler is static; use Scheduler.run(), not Scheduler()")

    @classmethod
    def populate(cls, root: Drawable) -> None:
        cls._roots.append(root)

    @classmethod
    def stop(cls) -> None:
        cls.running = False

    @classmethod
    def run(cls) -> None:
        cls.running = True
        cls.RENDERER.start()
        cls.INPUT.start()

        frame_budget = 1.0 / cls.TARGET_FPS
        last_time = perf_counter()

        try:
            while cls.running:
                frame_start = perf_counter()
                cls.dt = frame_start - last_time
                last_time = frame_start

                cls.INPUT.flush_events()
                for root in cls._roots:
                    root.poll(cls.INPUT)

                cls.RENDERER.begin_frame()
                for root in cls._roots:
                    root.arrange((0, 0), (cls.RENDERER.width, cls.RENDERER.height))
                for root in cls._roots:
                    root.draw(cls.RENDERER)
                cls.RENDERER.render()

                sleep_time = frame_budget - (perf_counter() - frame_start)
                if sleep_time > 0:
                    sleep(sleep_time)
        except KeyboardInterrupt:
            pass
        finally:
            cls.INPUT.stop()
            cls.RENDERER.close()
            cls.running = False

colors_list = [name for name in dir() if name.isupper()] + ["Style"]
__all__ = ["Scheduler", "TextInput", "TextLabel", "Menu", "MenuItem", "Pagination", "Page", "AbsoluteLayout", "StackLayout"] + colors_list