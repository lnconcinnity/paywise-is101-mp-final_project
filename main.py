from terminal.Renderer import Renderer
from terminal.InputHandler import InputHandler
from terminal.ui.Pagination import Pagination
from pages.SplashPage import page as SplashPage
from pages.LoginPage import page as LoginPage
import time

def run():
    running = True
    input = InputHandler(capture_signals=True)
    renderer = Renderer()
    input.start()

    pagination = None
    pagination = Pagination(
        SplashPage(renderer, input, lambda: pagination),
        LoginPage(renderer, input, lambda: pagination)
    )

    try:
        while running:
            input.flush_events()
            if not running:
                break
            # poll
            pagination.poll()
            # update
            renderer.update_dimensions()
            # draw
            pagination.draw()
            # render
            renderer.render()
            time.sleep(0.033)
    except KeyboardInterrupt:
        pass
    finally:
        input.stop()
        renderer.close()

if __name__ == "__main__":
    run()