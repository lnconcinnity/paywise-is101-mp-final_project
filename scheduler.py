from terminal.Renderer import Renderer
from terminal.InputHandler import InputHandler
from time import sleep

INPUT = InputHandler(capture_signals=True)
RENDERER = Renderer()

started = False
layouts = []

def start():
    # assert started, "scheduler is already running"
    started = True
    INPUT.start()

def stop():
    # assert not started, "scheduler hasn't started yet"
    INPUT.stop()
    RENDERER.close()
    started = False

def populate(layout):
    layouts.append(layout)

def run():
    running = True
    start()
    try:
        while running:
            INPUT.flush_events()
            if not running:
                break
            # poll
            for layout in layouts:
                if hasattr(layout, "poll"):
                    layout.poll()
            RENDERER.update_dimensions()
            # poll
            for layout in layouts:
                if hasattr(layout, "draw"):
                    layout.draw()
            RENDERER.render()
            sleep(0.033)
    except KeyboardInterrupt:
        pass
    finally:
        stop()