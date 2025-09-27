import random as rand

class PowerUp:
    def __init__(self, root):
        self.width = 120
        self.height = 120

        self.screen_height = root.winfo_screenheight()
        self.screen_width = root.winfo_screenwidth()

        self.reposition()

        self.visible = True

    def reposition(self):
        # random power up spawn (with 120 pixel buffer from edges)
        buffer = 120
        self.x = rand.randint(buffer, self.screen_width - buffer)
        self.y = rand.randint(buffer, self.screen_height - buffer)