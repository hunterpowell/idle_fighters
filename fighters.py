import tkinter as tk
import random as rand
from PIL import Image, ImageTk
import sys
import os
import time
from pathlib import Path
from playsound3 import playsound

# needed to add pngs to exe
def resource_path(relative_path):
    try:
        # for exe
        base_path = sys._MEIPASS
    except Exception:
        # for dev
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_images_folder():
    # always use the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # running as exe
        exe_dir = os.path.dirname(sys.executable)  # ← This uses where the EXE is located
    else:
        # running as script (for dev)
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    images_dir = os.path.join(exe_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    return images_dir

class Dude:
    def __init__(self, player, root):
        self.width = 240
        self.height = 240

        self.screen_height = root.winfo_screenheight()
        self.screen_width = root.winfo_screenwidth()

        self.speed = rand.choice([100, 150, 200])

        self.score = 0

        self._initial_pos(player, root)

        #small variance in starting pos
        self.x += rand.randint(-200, 200)
        self.y += rand.randint(-200, 200)

        # random direction
        dir = [self.speed, -self.speed]
        self.dx = rand.choice(dir)
        self.dy = rand.choice(dir)

    def _initial_pos(self, player, root):
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
    

class Fight:
                    
    def __init__(self):
        self.root = tk.Tk()

        self.setup_window()

        self.player1 = Dude(1, self.root)
        self.player2 = Dude(2, self.root)

        self.high_score = 0

        self.images = []
        self.load_images(self.player1)
        self.load_images(self.player2)
        self.current_image_index = 0
        self.current_image_index2 = (int(len(self.images)/2))

        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='#261313')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.bind('<Escape>', self.quit_app)

        self.running = True

        self.last_time = time.time()

    def load_images(self, player):

        images_folder = get_images_folder()
        suffixes = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
        print(f"looking for images in: {images_folder}")

        for file in Path(images_folder).iterdir():
            # filters for only images
            if file.suffix.lower() in suffixes:
                img = Image.open(file)
                img = img.resize((player.width, player.height), Image.Resampling.NEAREST)
                photo = ImageTk.PhotoImage(img)
                self.images.append(photo)
                print(f"loaded image: {file.name}")
        # random order :)
        rand.shuffle(self.images)

        # if no images found, use some rectangles
        if not self.images:
            print("no images found, creating default")
            colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']
            for color in colors:
                img = Image.new('RGB', (240, 240), color)
                photo = ImageTk.PhotoImage(img)
                self.images.append(photo)

    def setup_window(self):
        #remove window decorations
        self.root.overrideredirect(True)
        # always on top
        self.root.wm_attributes('-topmost', True)
        # make #000001 transparent
        self.root.wm_attributes('-transparentcolor', '#261313')

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # set window to fullscreen
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

    def combat_collision(self):

        p1 = self.player1
        p2 = self.player2

        if (p1.x < p2.x + p2.width and 
            p1.x + p1.width > p2.x and
            p1.y < p2.y + p2.height and
            p1.y + p1.height > p2.y):


            p1.dx, p2.dx = p2.dx, p1.dx
            p1.dy, p2.dy = p2.dy, p1.dy
            return True
        
        return False

    def change_p1_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.images)

    def change_p2_image(self):
        self.current_image_index2 = (self.current_image_index2 + 1) % len(self.images)

    def draw(self):
        self.canvas.delete("all")

        # force a redraw of the background with the transparent color, prevents weird trails
        self.canvas.create_rectangle(
            0, 0, 
            self.screen_width, self.screen_height, 
            fill = "#261313", 
            outline = ''
        )

        self.canvas.create_image(
            self.player1.x, self.player1.y,
            image = self.images[self.current_image_index],
            anchor = "nw"
        )
        self.canvas.create_text(
            self.player1.x + 110, self.player1.y-30,
            text = self.player1.score,
            fill = "#ffffff",
            font = "Arial 32 bold",
            anchor = "nw"
        )

        self.canvas.create_image(
            self.player2.x, self.player2.y,
            image = self.images[self.current_image_index2],
            anchor = "nw"
        )

        self.canvas.create_text(
            self.player2.x + 110, self.player2.y-30,
            text = self.player2.score,
            fill = "#ffffff",
            font = "Arial 32 bold",
            anchor = "nw"
        )

        self.canvas.create_text(
            0, 0,
            text = (f"High Score : {self.high_score}"),
            fill = "#ffffff",
            font = "Arial 48 bold",
            anchor = "nw"
        )

    def animate(self):

        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time

        # main animation loop
        if self.player1.update_pos(delta_time):           # returns corner hit T/F
            playsound(resource_path('taco_baco.mp3'), block = False)
            self.player1.score += 5

        if self.player2.update_pos(delta_time):           # returns corner hit T/F
            playsound(resource_path('taco_baco.mp3'), block = False)
            self.player2.score += 5

        if self.combat_collision():
            if rand.randint(0, 1):
                self.change_p1_image()
                self.player1.score = 0
                self.player2.score += 1
            else:
                self.change_p2_image()
                self.player2.score = 0
                self.player1.score += 1

        self.high_score = max(self.high_score, self.player1.score, self.player2.score)

        self.draw()

    def quit_app(self, event = None):
        self.running = False
        self.root.destroy()

    def run(self):
        while self.running:
            self.animate()
            self.root.update_idletasks()
            self.root.update()

if __name__ == "__main__":
    screensaver = Fight()
    screensaver.run()