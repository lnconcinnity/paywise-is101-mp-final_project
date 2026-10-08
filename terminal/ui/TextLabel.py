class TextLabel:
    def __init__(self, position=(0, 0), anchor_point=(0, 0), text="", renderer=None):
        self.position = position
        self.anchor_point = anchor_point
        self.text = text
        self.renderer = renderer

    def set_text(self, new_text):
        self.text = str(new_text)

    def render(self):
        return self.text

    def draw(self):
        box_width = len(self.text)
        box_height = 1

        target_x, target_y = self.position
        anchor_x, anchor_y = self.anchor_point

        screen_x = int(self.renderer.width * target_x)
        screen_y = int(self.renderer.height * target_y)

        abs_x = screen_x - int(box_width * anchor_x)
        abs_y = screen_y - int(box_height * anchor_y)

        self.renderer.draw(abs_x, abs_y, self.text)

        return abs_x, abs_y