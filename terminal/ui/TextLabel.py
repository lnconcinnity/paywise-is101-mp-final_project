from scheduler import RENDERER

class TextLabel:
    def __init__(self, position: tuple[int, int] | None=None, anchor_point: tuple[int, int] | None=None, text: str=""):
        self.position = position
        self.anchor_point = anchor_point
        self.text = text

    def set_text(self, new_text: str) -> None:
        self.text = str(new_text)

    def render(self) -> str:
        return self.text

    def draw(self) -> None:
        box_width = len(self.text)
        box_height = 1

        target_x, target_y = self.position
        anchor_x, anchor_y = self.anchor_point

        screen_x = int(RENDERER.width * target_x)
        screen_y = int(RENDERER.height * target_y)

        abs_x = screen_x - int(box_width * anchor_x)
        abs_y = screen_y - int(box_height * anchor_y)

        RENDERER.draw(abs_x, abs_y, self.text)