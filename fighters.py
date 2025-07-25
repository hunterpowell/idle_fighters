import tkinter as tk
import random as rand
from PIL import Image, ImageTk
import sys
import os
from pathlib import Path
from playsound3 import playsound
import math

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

class Fight:
    def __init__(self):
        self.root = tk.Tk()

        self.setup_window()

        self.width = 240
        self.height = 240

        self.speed = 5
        # SPEED DEBUGGING
        # self.speed = 30

        self.score1 = 0
        self.score2 = 0

        self.high_score = 0

        # comment out this, uncomment below to force a corner hit
        # initial pos, center of screen
        self.x = self.root.winfo_screenwidth()/4 - self.width/2
        self.y = self.root.winfo_screenheight()/2 - self.width/2

        self.x2 = self.root.winfo_screenwidth()*.75 - self.width/2
        self.y2 = self.root.winfo_screenheight()/2 - self.width/2

        #small variance in starting pos
        self.x += rand.randint(-200, 200)
        self.y += rand.randint(-200, 200)

        self.x2 += rand.randint(-200, 200)
        self.y2 += rand.randint(-200, 200)

        # speed, random direction
        dir = [self.speed, -self.speed]
        self.dx = rand.choice(dir)
        self.dy = rand.choice(dir)

        self.dx2 = -self.dx
        self.dy2 = -self.dy

        # # comment out the above, uncomment this to force a corner hit
        # self.x = 100
        # self.y = 100
        # self.dx = -3
        # self.dy = -3

        self.images = []
        self.load_images()
        self.current_image_index = 0
        self.current_image_index2 = (int(len(self.images)/2))

        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='#000001')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.bind('<Escape>', self.quit_app)

    def load_images(self):

        images_folder = get_images_folder()
        suffixes = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
        print(f"looking for images in: {images_folder}")

        for file in Path(images_folder).iterdir():
            # filters for only images
            if file.suffix.lower() in suffixes:
                img = Image.open(file)
                img = img.resize((self.width, self.height), Image.Resampling.NEAREST)
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
                img = Image.new('RGB', (self.width, self.height), color)
                photo = ImageTk.PhotoImage(img)
                self.images.append(photo)

    def setup_window(self):
        #remove window decorations
        self.root.overrideredirect(True)
        # always on top
        self.root.wm_attributes('-topmost', True)
        # make #000001 transparent
        self.root.wm_attributes('-transparentcolor', '#000001')

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # set window to fullscreen
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

    def update_pos(self):

        # update pos
        self.x += self.dx
        self.y += self.dy

        # collision = False
        corner = False

        top = bool(self.y + self.height >= self.screen_height)
        right = bool(self.x + self.width >= self.screen_width)
        bottom = bool(self.y <= 0)
        left = bool(self.x <= 0)

        # bounce on collision
        if right:
            # flips sign of dx, randomizes speed between 4-6
            self.dx = rand.randint(-6, -4)
            if top or bottom:
                corner = True
        if top:
            self.dy = rand.randint(-6, -4)
            if left or right:
                corner = True
        if left:
            self.dx = rand.randint(4, 6)
            if top or bottom:
                corner = True
        if bottom:
            self.dy = rand.randint(4, 6)
            if left or right:
                corner = True

        if self.combat_collision():
            if rand.randint(0,1):
                self.change_image()
                self.score1 = 0
                self.score2 += 1
                if self.score2 > self.high_score:
                    self.high_score = self.score2
            else:
                self.change_image2()
                self.score2 = 0
                self.score1 += 1
                if self.score1 > self.high_score:
                    self.high_score = self.score1
                
        if corner:
            sound_path = resource_path('taco_baco.mp3')
            playsound(sound_path)
            self.score1 += 5

    def update_pos2(self):

        # update pos
        self.x2 += self.dx2
        self.y2 += self.dy2

        # collision = False
        corner = False

        top = bool(self.y2 + self.height >= self.screen_height)
        right = bool(self.x2 + self.width >= self.screen_width)
        bottom = bool(self.y2 <= 0)
        left = bool(self.x2 <= 0)

        # bounce on collision
        if right:
            self.dx2 = rand.randint(-6, -4)
            if top or bottom:
                corner = True
        if top:
            self.dy2 = rand.randint(-6, -4)
            if left or right:
                corner = True
        if left:
            self.dx2 = rand.randint(4, 6)
            if top or bottom:
                corner = True
        if bottom:
            self.dy2 = rand.randint(4, 6)
            if left or right:
                corner = True
        if corner:
            sound_path = resource_path('taco_baco.mp3')
            playsound(sound_path)
            self.score2 += 5
            if self.score2 > self.high_score:
                self.high_score = self.score2

    def combat_collision(self):
        # check if rectangles are colliding
        if (self.x < self.x2 + self.width and 
            self.x + self.width > self.x2 and
            self.y < self.y2 + self.height and 
            self.y + self.height > self.y2):
            
            # calc overlap amounts
            overlap_x = min(self.x + self.width - self.x2, self.x2 + self.width - self.x)
            overlap_y = min(self.y + self.height - self.y2, self.y2 + self.height - self.y)
            
            # determine collision direction and exchange velocities
            if overlap_x < overlap_y:  # horizontal collision
                self.dx, self.dx2 = self.dx2, self.dx
            else:  # vertical collision
                self.dy, self.dy2 = self.dy2, self.dy
                
            return True
        return False

    def change_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.images)

    def change_image2(self):
        self.current_image_index2 = (self.current_image_index2 + 1) % len(self.images)

    def draw(self):
        self.canvas.delete("all")

        # force a redraw of the background with the transparent color, prevents weird trails
        self.canvas.create_rectangle(
            0, 0, 
            self.screen_width, self.screen_height, 
            fill = '#000001', 
            outline = ''
        )

        self.canvas.create_image(
            self.x, self.y,
            image = self.images[self.current_image_index],
            anchor = "nw"
        )
        self.canvas.create_text(
            self.x+110, self.y-30,
            text = self.score1,
            fill = "#ffffff",
            font = "Arial 32 bold",
            anchor = "nw"
        )

        self.canvas.create_image(
            self.x2, self.y2,
            image = self.images[self.current_image_index2],
            anchor = "nw"
        )

        self.canvas.create_text(
            self.x2+110, self.y2-30,
            text = self.score2,
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
        # main animation loop
        self.update_pos()
        self.update_pos2()
        self.draw()

        # schedule next frame (roughly 60 FPS)
        self.root.after(17, self.animate)

    def quit_app(self, event = None):
        self.root.destroy()

    def run(self):
        self.animate()
        self.root.mainloop()

if __name__ == "__main__":
    screensaver = Fight()
    screensaver.run()