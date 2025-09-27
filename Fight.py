import Dude
import PowerUp
import AnimatedImage as Anim
from helpers import resource_path, get_images_folder
import time
import tkinter as tk
from playsound3 import playsound
import random as rand
from PIL import Image, ImageTk
from pathlib import Path

class Fight:
                    
    def __init__(self):
        self.root = tk.Tk()

        self.setup_window()

        self.player1 = Dude.Dude(1, self.root)
        self.player2 = Dude.Dude(2, self.root)
        self.power_up = PowerUp.PowerUp(self.root)

        particle_path = resource_path('assets/particles.gif')
        self.particles = Anim.AnimatedImage(particle_path, self.player1.width, self.player1.height)

        self.high_score = 0

        self.animated_images = []
        self.images = []

        strawberry_path = resource_path('assets/strawberry.gif')
        self.power_up_gif = Anim.AnimatedImage(strawberry_path, self.power_up.width, self.power_up.height)

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
                animated_img = Anim.AnimatedImage(str(file), self.player1.width, self.player1.height)
                self.animated_images.append(animated_img)
                print(f"loaded image: {file.name}")
        # random order :)
        rand.shuffle(self.animated_images)

        # if no images found, use some rectangles
        if not self.animated_images:
            print("no images found, creating default")
            colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']
            for color in colors:
                # Create a simple colored rectangle as fallback
                img = Image.new('RGBA', (240, 240), color)
                photo = ImageTk.PhotoImage(img)
                # Create a simple AnimatedImage wrapper
                animated_img = Anim.__new__(Anim)
                animated_img.frames = [photo]
                animated_img.frame_count = 1
                animated_img.current_frame = 0
                self.animated_images.append(animated_img)

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
    
    def power_up_collision(self):
        
        p1 = self.player1
        p2 = self.player2
        item = self.power_up

        if (item.visible):

            # check player 1 power up collision
            if (p1.x < item.x + item.width and 
                p1.x + p1.width > item.x and
                p1.y < item.y + item.height and
                p1.y + p1.height > item.y):

                p1.powered_up = True
                item.visible = False

                self.root.after(15000, self.respawn_power_up)

            # check player 2 power up collision
            elif (p2.x < item.x + item.width and 
                p2.x + p2.width > item.x and
                p2.y < item.y + item.height and
                p2.y + p2.height > item.y):

                p2.powered_up = True
                item.visible = False

                self.root.after(15000, self.respawn_power_up)

    def respawn_power_up(self):
        self.power_up.reposition()
        self.power_up.visible = True

    def change_p1_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.animated_images)
        self.animated_images[self.current_image_index].reset_animation()

    def change_p2_image(self):
        self.current_image_index2 = (self.current_image_index2 + 1) % len(self.animated_images)
        self.animated_images[self.current_image_index].reset_animation()

    def draw(self):
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
        
        if self.player1.powered_up:
            particle_frame = self.particles.get_current_frame()
            self.canvas.create_image(
                self.player1.x, self.player1.y,
                image = particle_frame,
                anchor = "nw"
            )
        
        self.canvas.create_text(
            self.player1.x + 110, self.player1.y-30,
            text = self.player1.score,
            fill = "#ffffff",
            font = "Arial 32 bold",
            anchor = "nw"
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
            self.player2.x + 110, self.player2.y-30,
            text = self.player2.score,
            fill = "#ffffff",
            font = "Arial 32 bold",
            anchor = "nw"
        )

        if self.player2.powered_up:
            particle_frame = self.particles.get_current_frame()
            self.canvas.create_image(
                self.player2.x, self.player2.y,
                image = particle_frame,
                anchor = "nw"
            )

        self.canvas.create_text(
            0, 0,
            text = (f"High Score : {self.high_score}"),
            fill = "#ffffff",
            font = "Arial 48 bold",
            anchor = "nw"
        )

        # draw power up if visible
        if self.power_up.visible:
            power_up_frame = self.power_up_gif.get_current_frame()
            self.canvas.create_image(
                self.power_up.x, self.power_up.y,
                image = power_up_frame,
                anchor = "nw"
            )



    def animate(self):

        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time

        p1 = self.player1
        p2 = self.player2

        # main animation loop
        if p1.update_pos(delta_time):           # returns corner hit T/F
            playsound(resource_path('assets/taco_baco.mp3'), block = False)
            p1.score += 5

        if p2.update_pos(delta_time):           # returns corner hit T/F
            playsound(resource_path('assets/taco_baco.mp3'), block = False)
            p2.score += 5

        if self.combat_collision():
            # player 1 has powerup, wins
            if p1.powered_up and not p2.powered_up:
                self.change_p2_image()
                p2.score = 0
                p1.score += 1
                # clear all powerups
                p1.powered_up = False
                p2.powered_up = False

            # player 2 has powerup, wins
            elif p2.powered_up and not p1.powered_up:
                self.change_p1_image()
                p1.score = 0
                p2.score += 1
                p2.powered_up = False
                p1.powered_up = False

            # neither or both have powerup, coinflip
            else:
                if rand.randint(0, 1):
                    self.change_p1_image()
                    p1.score = 0
                    p2.score += 1
                    p2.powered_up = False
                    p1.powered_up = False
                else:
                    self.change_p2_image()
                    p2.score = 0
                    p1.score += 1
                    p1.powered_up = False
                    p2.powered_up = False

        self.high_score = max(self.high_score, p1.score, p2.score)

        self.power_up_collision()

        self.draw()

    def quit_app(self, event = None):
        self.running = False
        self.root.destroy()

    def run(self):
        while self.running:
            self.animate()
            self.root.update_idletasks()
            self.root.update()
