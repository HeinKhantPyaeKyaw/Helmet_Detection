import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog

# Global Variables for Video Capture
cap = None
playing_video = False
video_fps = 30

# Function to start live video capture
def start_live_video(video_canvas):
  global cap, playing_video
  if cap:
    stop_video()
  cap = cv2.VideoCapture(0)
  playing_video = True
  show_video(video_canvas)
  
  
# Function to upload a video file
def upload_video(video_canvas):
  global cap, playing_video
  file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4")])
  if cap:
    stop_video()

  if file_path:
    cap = cv2.VideoCapture(file_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_fps = fps if fps > 0 else 30
    playing_video = True
  
  show_video(video_canvas)


# Show Video
def show_video(video_canvas, fps=None):
  global cap, playing_video, video_fps
  ret, frame = cap.read()
  if not ret:
    print("Error: Cannot read the frame")
    return
  
  video_canvas.delete("all")
  
  # Resize the frame to fit the canvas
  canvas_width = video_canvas.winfo_width()
  canvas_height = video_canvas.winfo_height()
  
  frame_height, frame_width,= frame.shape[:2]
  aspect_ratio = frame_width/frame_height
  new_width = canvas_width
  new_height = int(new_width/aspect_ratio)
  
  if new_height > canvas_height:
    new_height = canvas_height
    new_width = int(new_height * aspect_ratio)
    
  resized_frame = cv2.resize(frame, (new_width, new_height))
  
  # Convert the frame to RGB to display in tkinter canvas
  frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
  img = Image.fromarray(frame_rgb)
  img_tk = ImageTk.PhotoImage(image=img)
  
  x_pos = (canvas_width - new_width)//2
  y_pos = (canvas_height - new_height)//2
  
  # Display the video feed
  video_canvas.create_image(x_pos, y_pos, image=img_tk, anchor="nw")
  video_canvas.img = img_tk
  
  
  
  if fps is not None:
    video_fps = fps  
  frame_delay=int(1000/video_fps)
  
  # Continuously display the video feed
  video_canvas.after(frame_delay, lambda: show_video(video_canvas, video_fps))
  
  
# Function to stop video capture
def stop_video():
  global cap, playing_video
  if cap:
    cap.release()
  cap = None
  playing_video = False