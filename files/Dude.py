import random as rand


class Dude:
    def __init__(self, player, root):

        self.width = 240
        self.height = 240

        self.screen_height = root.winfo_screenheight()
        self.screen_width = root.winfo_screenwidth()

        self.speed = rand.choice([100, 150, 200])

        self.score = 0

        self.powered_up = False

        self._initial_pos(player)

        #small variance in starting pos
        self.x += rand.randint(-200, 200)
        self.y += rand.randint(-200, 200)

        # random direction
        dir = [self.speed, -self.speed]
        self.dx = rand.choice(dir)
        self.dy = rand.choice(dir)

    def _initial_pos(self, player):
        # left side start
        if player == 1:
            self.x = self.screen_width/4 - self.width/2
            self.y = self.screen_height/2 - self.height/2
        # right side start
        else:
            self.x = self.screen_width*.75 - self.width/2
            self.y = self.screen_height/2 - self.width/2

    def update_pos(self, delta_time):

        # update pos
        self.x += self.dx * delta_time
        self.y += self.dy * delta_time

        # collision = False
        corner = False

        top = bool(self.y + self.height >= self.screen_height)
        right = bool(self.x + self.width >= self.screen_width)
        bottom = bool(self.y <= 0)
        left = bool(self.x <= 0)

        # bounce on collision
        if right:
            # flips sign of dx, randomizes speed
            self.dx = rand.choice([-180, -150, -120])
            if top or bottom:
                corner = True
        if top:
            self.dy = rand.choice([-180, -150, -120])
            if left or right:
                corner = True
        if left:
            self.dx = rand.choice([120, 150, 180])
            if top or bottom:
                corner = True
        if bottom:
            self.dy = rand.choice([120, 150, 180])
            if left or right:
                corner = True

        return corner
    
