import random as rand
import tkinter as tk

class Dude:
    def __init__(self, player):
        self.width = 240
        self.height = 240

        self.speed = rand.choice(4, 6)

        self.score = 0

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
            self.x = self.root.winfo_screenwidth()/4 - self.width/2
            self.y = self.root.winfo_screenheight()/2 - self.width/2
        # right side start
        else:
            self.x2 = self.root.winfo_screenwidth()*.75 - self.width/2
            self.y2 = self.root.winfo_screenheight()/2 - self.width/2

            