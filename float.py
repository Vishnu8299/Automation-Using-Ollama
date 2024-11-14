import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import cv2

class FloatingIcon:
    def __init__(self, video_path):
        # Initialize main Tkinter window
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.wm_attributes("-topmost", True)  # Keep window on top
        self.root.wm_attributes("-transparentcolor", "white")  # Set transparency color
        
        # Set up canvas with transparent background
        self.canvas_size = 100  # New smaller size
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size, bg='white', highlightthickness=0)
        self.canvas.pack()
        
        # Load video
        self.video = cv2.VideoCapture(video_path)

        # Start video animation
        self.update_frame()

        # Make the icon draggable
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.move_icon)

        # Set initial position of the window
        self.root.geometry(f"{self.canvas_size}x{self.canvas_size}+100+100")
        self.root.mainloop()

    def update_frame(self):
        # Read the next frame from the video
        ret, frame = self.video.read()
        if ret:
            # Resize the frame to fit in the smaller circular window
            frame = cv2.resize(frame, (self.canvas_size, self.canvas_size))
            
            # Convert frame to RGB and then to PIL format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)

            # Create a circular mask for the new size
            mask = Image.new("L", (self.canvas_size, self.canvas_size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, self.canvas_size, self.canvas_size), fill=255)
            pil_image.putalpha(mask)

            # Convert PIL image to ImageTk format and update the label
            self.photo = ImageTk.PhotoImage(pil_image)
            self.canvas.create_image(self.canvas_size // 2, self.canvas_size // 2, image=self.photo)
        
        else:
            # Restart video if it reaches the end
            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        # Schedule the next frame update
        self.root.after(33, self.update_frame)  # 33 ms for ~30 FPS

    def start_move(self, event):
        self.x_offset = event.x
        self.y_offset = event.y

    def move_icon(self, event):
        x = self.root.winfo_x() + event.x - self.x_offset
        y = self.root.winfo_y() + event.y - self.y_offset
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    icon = FloatingIcon("JARVIS.mp4")
