import time
import Dude
import AnimatedImage as Animated
from PIL import Image, ImageTk
import tkinter as tk
from pathlib import Path
from playsound3 import playsound
import random as rand
from helpers import get_images_folder, resource_path

class Fight:
                    
    def __init__(self):
        self.root = tk.Tk()

        self.setup_window()

        self.player1 = Dude.Dude(1, self.root)
        self.player2 = Dude.Dude(2, self.root)

        self.high_score = 0

        self.animated_images = []
        self.images = []
        self.load_images()
        self.current_image_index = 0
        self.current_image_index2 = (int(len(self.animated_images)/2))

        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='#261313')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.bind('<Escape>', self.quit_app)

        self.running = True

        self.last_time = time.time()

    def load_images(self):

        images_folder = get_images_folder()
        suffixes = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
        print(f"looking for images in: {images_folder}")

        for file in Path(images_folder).iterdir():
            # filters for only images
            if file.suffix.lower() in suffixes:
                animated_img = Animated.AnimatedImage(str(file), self.player1.width, self.player1.height)
                self.animated_images.append(animated_img)
                print(f"loaded image: {file.name}")
        # random order :)
        rand.shuffle(self.animated_images)

        # if no images found, use some rectangles
        if not self.animated_images:
            print("no images found, creating default")
            colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']
            for color in colors:
                # create a simple colored rectangle as fallback
                img = Image.new('RGBA', (240, 240), color)
                photo = ImageTk.PhotoImage(img)
                # simple AnimatedImage wrapper
                animated_img = Animated.AnimatedImage.__new__(Animated.AnimatedImage)
                animated_img.frames = [photo]
                animated_img.frame_count = 1
                animated_img.current_frame = 0
                self.animated_images.append(animated_img)
    
        # TODO
        # resources_folder = Path(resource_path('.')).parent if resource_path('.') else Path('.')
        # mp3_files = list(resources_folder.glob('*.mp3'))
        # if mp3_files:
        #     return str(mp3_files[0])  # Return the first (and presumably only) MP3 file
        # else:
        #     print("No MP3 files found")
        #     return None

    def setup_window(self):
        #remove window decorations
        self.root.overrideredirect(True)
        # always on top
        self.root.wm_attributes('-topmost', True)
        # make #261313 transparent
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
        self.current_image_index = (self.current_image_index + 1) % len(self.animated_images)
        self.animated_images[self.current_image_index].reset_animation()

    def change_p2_image(self):
        self.current_image_index2 = (self.current_image_index2 + 1) % len(self.animated_images)
        self.animated_images[self.current_image_index].reset_animation()

    def draw(self):
        x_offset = 110
        y_offset = -30

        self.canvas.delete("all")

        # force a redraw of the background with the transparent color, prevents weird trails
        self.canvas.create_rectangle(
            0, 0, 
            self.screen_width, self.screen_height, 
            fill = "#261313", 
            outline = ''
        )

        # draw player 1 with current animation frame
        if self.animated_images:
            current_frame1 = self.animated_images[self.current_image_index].get_current_frame()
            self.canvas.create_image(
                self.player1.x, self.player1.y,
                image = current_frame1,
                anchor = "nw"
            )
        
        self.canvas.create_text(
            self.player1.x + x_offset, self.player1.y + y_offset,
            text = self.player1.score,
            fill = "#ffffff",
            font = "Arial 32 bold",
        )

        # draw player 2 with current animation frame
        if self.animated_images:
            current_frame2 = self.animated_images[self.current_image_index2].get_current_frame()
            self.canvas.create_image(
                self.player2.x, self.player2.y,
                image = current_frame2,
                anchor = "nw"
            )

        self.canvas.create_text(
            self.player2.x + x_offset, self.player2.y + y_offset,
            text = self.player2.score,
            fill = "#ffffff",
            font = "Arial 32 bold",
        )

        self.canvas.create_text(
            0, 0,
            text = (f"High Score : {self.high_score}"),
            fill = "#ffffff",
            font = "Arial 48 bold",
            anchor = 'nw'
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