from terminal.Renderer import Renderer
from terminal.InputHandler import InputHandler
from terminal.ui.ComponentTypes import Drawable
from time import sleep, perf_counter

INPUT = InputHandler(capture_signals=True)
RENDERER = Renderer()

is_running: bool = False
layouts: list[Drawable] = []

def populate(layout: Drawable) -> None:
    layouts.append(layout)

def stop() -> None:
    global is_running
    is_running = False

def run() -> None:
    global is_running
    is_running = True
    INPUT.start()
    
    TARGET_FRAME_TIME = 1.0 / 30.0
    last_time = perf_counter()
    
    try:
        while is_running:
            frame_start = perf_counter()
            dt = frame_start - last_time
            last_time = frame_start
            
            INPUT.flush_events()
            for layout in layouts:
                layout.poll()

            RENDERER.update_dimensions()
            for layout in layouts:
                layout.draw()
                
            RENDERER.render()
            
            frame_duration = perf_counter() - frame_start
            sleep_time = TARGET_FRAME_TIME - frame_duration
            if sleep_time > 0:
                sleep(sleep_time)
                
    except KeyboardInterrupt:
        pass
    finally:
        INPUT.stop()
        RENDERER.close()
        is_running = False