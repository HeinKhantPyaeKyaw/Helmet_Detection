import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
from ultralytics import YOLO

# Global Variables for Video Capture
cap = None
playing_video = False
video_fps = 30

model = YOLO('best.pt')

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
  
# Function to check if two classes are overlapping or not
def is_intersecting(box1, box2):
  x1_min, y1_min, x1_max, y1_max = box1
  x2_min, y2_min, x2_max, y2_max = box2
  
  if x1_min > x2_max or x2_min > x1_max or y1_min > y2_max or y2_min > y1_max:
    return False
  return True


# Show Video
def show_video(video_canvas, fps=None):
  cnt = 0
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
  # video_canvas.create_image(x_pos, y_pos, image=img_tk, anchor="nw")
  # video_canvas.img = img_tk
  
  results = model(frame_rgb)
  frm = results[0].plot()
  frm_img = Image.fromarray(frm)
  frm_img_tk = ImageTk.PhotoImage(image=frm_img)
  
  # for class_id, class_name in model.names.items():
  #   print(f"Class ID: {class_id}, Class Name: {class_name}")
  
  # Boxes for classes
  no_helmet_boxes = []
  helmet_boxes = []
  motorcycle_boxes = []
  
  for detection in results[0].boxes:
    class_id = int (detection.cls)
    box = detection.xyxy[0].tolist()
    
    # Check if teh class is no_helmet or "motorcycle"
    if class_id == 2:
      no_helmet_boxes.append(box)
    elif class_id == 1:
      helmet_boxes.append(box)
    elif class_id == 0:
      motorcycle_boxes.append(box)
      
  # Check if the helmet and motorcycle boxes are overlapping
  # for helmet_box in helmet_boxes:
  #   for motorcycle_box in motorcycle_boxes:
      
  # Check if the no_helmet and motorcycle boxes are overlapping
  violation_img = None
  for no_helmet_box in no_helmet_boxes:
    for motorcycle_box in motorcycle_boxes:
      if is_intersecting(no_helmet_box, motorcycle_box):
        violation_img = Image.fromarray(frm)
        # sliced_violated_img = violation_img.crop(int(motorcycle_box[0]), int(motorcycle_box[1]), int(motorcycle_box[2]), int(motorcycle_box[3]))
        violation_img_tk = ImageTk.PhotoImage(image=sliced_violated_img)
        cv2.imwrite(f"violation{violation_img_tk}.jpg", frm)
        print("Violation Detected!")
        
  # cv2.imwrite(f"test{violation_img_tk}.jpg", frm)
  
  video_canvas.create_image(x_pos, y_pos, image=frm_img_tk, anchor="nw")
  video_canvas.img = frm_img_tk 
  
  # cv2.imwrite('output_{cnt}.jpg', frm)
  
  # video_canvas.img = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
  
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
