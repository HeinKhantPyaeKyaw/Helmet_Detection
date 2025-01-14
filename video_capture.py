import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
from ultralytics import YOLO
from datetime import datetime
import sqlite3
import os
import threading
import playsound
import time

# Global Variables for Video Capture
cap = None
playing_video = False
video_fps = 30
# saved_violation_ids = set()
active_violations_dict = {}
last_seen_frame_dict = {}



model = YOLO('it30_best.pt')

db_path = "helmet_detection.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the table if it does not exist
cursor.execute(''' 
               CREATE TABLE IF NOT EXISTS helmet_detection(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 filename TEXT NOT NULL,
                 image_path TEXT NOT NULL,
                 violation_type TEXT NOT NULL,
                 violation_timestamp TEXT NOT NULL
                  )
                 ''')

conn.commit()

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

def play_alarm_sound():
  try:
    playsound.playsound(os.path.abspath("alarm.wav"))
    print("Alarm sound played")
  except:
    print("Error: Cannot play alarm sound")

def save_violation(violation_id, img, violation_type):
  global active_violations_dict
  global filtered_violations_dict
  
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  img_folder = "violation_images"
  file_name = f"violation_{violation_id}.jpg"
  os.makedirs(img_folder, exist_ok=True)
  img_path = os.path.join(img_folder, f"violation_{violation_id}.jpg")
  img.save(img_path)
  # threading.Thread(target=play_alarm_sound).start()
  cursor.execute("INSERT INTO helmet_detection(filename, image_path, violation_type, violation_timestamp) VALUES (?, ?, ?, ?)", (file_name, img_path, violation_type, timestamp))
  conn.commit()
  
  print(f"Violation ID {violation_id} saved to the database")
  

# Show Video
def show_video(video_canvas, fps=None):
  global cap, playing_video, video_fps, active_violations_dict, last_seen_frame_dict
  ret, frame = cap.read()
  if not ret:
    print("Error: Cannot read the frame")
    return
  
  # video_canvas.delete("all")
  
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
  
  results = model.track(frame_rgb, persist=True)
  frm = results[0].plot()
  frm_img = Image.fromarray(frm)
  frm_img_tk = ImageTk.PhotoImage(image=frm_img)
  
  # Boxes for classes
  no_helmet_boxes = []
  helmet_boxes = []
  motorcycle_boxes = []
  current_ids = set()
  
  for detection in results[0].boxes:
    class_id = int (detection.cls)
    box = detection.xyxy[0].tolist()
    # track_id = detection.id
    track_id = int(detection.id.item()) if detection.id is not None else None

    
    if track_id is None:
      continue
    current_ids.add(track_id)
    
    # Check if teh class is no_helmet or "motorcycle"
    if class_id == 2:
      no_helmet_boxes.append((box, track_id))
    # elif class_id == 1:
    #   helmet_boxes.append(box)
    elif class_id == 0:
      motorcycle_boxes.append((box, track_id))
      
  # Check if the no_helmet and motorcycle boxes are overlapping
  violation_img = None
  for motorcycle_box, motorcycle_id in motorcycle_boxes:
    for no_helmet_box, no_helmet_id in no_helmet_boxes: 
      if is_intersecting(no_helmet_box, motorcycle_box):
        if motorcycle_id not in active_violations_dict:
          # Mark the ID as active and alarm not played
          active_violations_dict[motorcycle_id] = {"alarm_played": False}

        if not active_violations_dict[motorcycle_id]["alarm_played"]:
          # Play alarm only once
          threading.Thread(target=play_alarm_sound).start()
          active_violations_dict[motorcycle_id]["alarm_played"] = True
        x1, y1, x2, y2 = map(int, motorcycle_box)
        cropped_img = cv2.cvtColor(frame_rgb[y1:y2, x1:x2], cv2.COLOR_RGB2BGR)
        violation_img = Image.fromarray(cv2.cvtColor(cropped_img, cv2.COLOR_RGB2BGR))
        violation_img_tk = ImageTk.PhotoImage(image=violation_img)
        # threading.Thread(target=play_alarm_sound).start()
          
        # Store the last frame where the violation was detected
        last_seen_frame_dict[motorcycle_id] = (violation_img, "No Helmet Violation")
  
  # Handle objects that are no longer in the frame
  inactive_ids = set(active_violations_dict.keys()) - current_ids
  for inactive_id in inactive_ids:
    if inactive_id in last_seen_frame_dict:
      violation_img, violation_type = last_seen_frame_dict.pop(inactive_id)
      # threading.Thread(target=save_violation, args=(inactive_id, violation_img, violation_type)).start()
      save_violation(inactive_id, violation_img, violation_type)
    active_violations_dict.pop(inactive_id)
    
  # Update active violations
  active_violations_dict.update({track_id : {"alarm_played": True} for track_id in current_ids})
          
  
  print (active_violations_dict)
  video_canvas.create_image(x_pos, y_pos, image=frm_img_tk, anchor="nw")
  video_canvas.img = frm_img_tk 
  
  if fps is not None:
    video_fps = fps  
  frame_delay=int(1000/video_fps)
  
  # Continuously display the video feed
  video_canvas.after(frame_delay, lambda: show_video(video_canvas, video_fps))
  
  
# Function to stop video capture
def stop_video(video_canvas):
  global cap, playing_video
  if cap:
    cap.release()
  cap = None
  playing_video = False
  video_canvas.delete("all")