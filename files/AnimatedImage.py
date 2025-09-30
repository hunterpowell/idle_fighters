from PIL import Image, ImageTk
import time

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