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
        exe_dir = os.path.dirname(sys.executable)
    else:
        # running as script (for dev)
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    images_dir = os.path.join(exe_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    return images_dir

class AnimatedImage:
    def __init__(self, filepath, width, height):
        self.frames = []
        self.frame_count = 0
        self.current_frame = 0
        self.frame_duration = 100
        self.last_frame_time = time.time()

        try:
            img = Image.open(filepath)
            
            # check if it's an animated GIF
            if hasattr(img, 'n_frames') and img.n_frames > 1:
                # GIF
                for frame_num in range(img.n_frames):
                    img.seek(frame_num)
                    frame = img.copy()
                    frame = frame.resize((width, height), Image.Resampling.NEAREST)
                    
                    # Convert to RGBA if needed for transparency
                    if frame.mode != 'RGBA':
                        frame = frame.convert('RGBA')
                    
                    photo = ImageTk.PhotoImage(frame)
                    self.frames.append(photo)
                
                # try to get frame duration from GIF
                try:
                    img.seek(0)
                    self.frame_duration = img.info.get('duration', 100)
                except:
                    self.frame_duration = 100
                    
            else:
                # static image
                frame = img.resize((width, height), Image.Resampling.NEAREST)
                if frame.mode != 'RGBA':
                    frame = frame.convert('RGBA')
                photo = ImageTk.PhotoImage(frame)
                self.frames.append(photo)
                
            self.frame_count = len(self.frames)
            
        except Exception as e:
            print(f"Error loading image {filepath}: {e}")
            # create a fallback colored rectangle
            fallback = Image.new('RGBA', (width, height), (255, 0, 0, 255))
            photo = ImageTk.PhotoImage(fallback)
            self.frames.append(photo)
            self.frame_count = 1


    def get_current_frame(self):
        if self.frame_count <= 1:
            return self.frames[0]

        current_time = time.time()
        if (current_time - self.last_frame_time) * 1000 >= self.frame_duration:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.last_frame_time = current_time

        return self.frames[self.current_frame]
    
    def reset_animation(self):
        self.current_frame = 0
        self.last_frame_time = time.time()

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
    

class Fight:
                    
    def __init__(self):
        self.root = tk.Tk()

        self.setup_window()

        self.player1 = Dude(1, self.root)
        self.player2 = Dude(2, self.root)
        self.power_up = PowerUp(self.root)

        particle_path = resource_path('assets/particles.gif')
        self.particles = AnimatedImage(particle_path, self.player1.width, self.player1.height)

        self.high_score = 0

        self.animated_images = []
        self.images = []

        strawberry_path = resource_path('assets/strawberry.gif')
        self.power_up_gif = AnimatedImage(strawberry_path, self.power_up.width, self.power_up.height)

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
                animated_img = AnimatedImage(str(file), self.player1.width, self.player1.height)
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
                animated_img = AnimatedImage.__new__(AnimatedImage)
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
                p1.powered_up = False

            # player 2 has powerup, wins
            elif p2.powered_up and not p1.powered_up:
                self.change_p1_image()
                p1.score = 0
                p2.score += 1
                p2.powered_up = False

            # neither or both have powerup, coinflip
            else:
                if rand.randint(0, 1):
                    self.change_p1_image()
                    p1.score = 0
                    p2.score += 1
                    p2.powered_up = False
                else:
                    self.change_p2_image()
                    p2.score = 0
                    p1.score += 1
                    p1.powered_up = False

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

if __name__ == "__main__":
    screensaver = Fight()
    screensaver.run()