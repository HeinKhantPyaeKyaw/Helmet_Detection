import tkinter as tk
from tkinter import ttk, filedialog
import alarm_functions
import video_capture
import sqlite3

db_path = "helmet_detection.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the main window
window = tk.Tk()
window.title("QuadLink Helmet Detection System")
window.geometry("1400x800")
# window.pack_propagate(False)

# Create two tabs for Monitor and Records
tabs = ttk.Notebook(window)
tabs.pack(fill='both', expand=True)

# Two Tabs for Monitor and Records
monitor_tab = ttk.Frame(tabs, width=700, height=600,)
tabs.add(monitor_tab, text="Monitor")
records_tab = ttk.Frame(tabs, width=700, height=600)
tabs.add(records_tab, text="Records")

#------------------Monitor Tab------------------
# Video Capture Frame
video_frame = tk.Frame(monitor_tab, background="#545454", width=400)
video_frame.pack(side="left", fill="both", expand=True)
video_frame.grid_rowconfigure(1, weight=1)   # Allow row 1 to expand vertically
video_frame.grid_columnconfigure(0, weight=1)
frame_label1 = tk.Label(video_frame, text="Video Capture Frame", font=("Arial", 20), fg="white", background="#545454")
frame_label1.grid(row=0, column=0, pady=10)
alarmNoti_label = tk.Label(video_frame, text="Alarm: ", font=("Arial", 20), fg="white", background="#545454")
alarmNoti_label.grid(row=0, column=1, pady=10)
# ------------------Video Capture Frame------------------
video_canvas = tk.Canvas(video_frame, width=640, height=480, background="black")
video_canvas.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=10)

# Capture Date and Time Label
capture_datetime_label = tk.Label(video_frame, text="Capture Date and Time", font=("Arial", 15), fg="white", background="#545454")
capture_datetime_label.grid(row=2, column=0, columnspan=3, pady=10)



# Indicator Light
my_canvas = tk.Canvas(video_frame, width=50, height=50, background="#545454", bd=0, highlightthickness=0)
my_canvas.grid(row=0, column=2, pady=10)
indicator = my_canvas.create_oval(10, 10, 40, 40, fill="green", tags="indicator")


# Button to start live video
live_video_btn = tk.Button(video_frame, text="Start Live Video", command=lambda: video_capture.start_live_video(video_canvas,))
live_video_btn.grid(row=3, column=0, pady=10)

# Button to upload video
upload_video_btn = tk.Button(video_frame, text="Upload Video", command=lambda: video_capture.upload_video(video_canvas,))
upload_video_btn.grid(row=3, column=1, pady=10)

# Button to stop video
upload_video_btn = tk.Button(video_frame, text="Stop", command=lambda: video_capture.stop_video(video_canvas,))
upload_video_btn.grid(row=3, column=2, pady=10)



# Violation Information Frame
violation_frame = tk.Frame(monitor_tab, background="#545454")
violation_frame.pack(side="right", fill="both", expand=True)
violation_frame.grid_rowconfigure(1, weight=1)   # Allow row 1 to expand vertically
violation_frame.grid_columnconfigure(0, weight=1)
# Saved Capture Label
frame_label2 = tk.Label(violation_frame, text="Saved Captures", font=("Arial", 20), fg="white", background="#545454")
frame_label2.grid(row=0, column=0, pady=10)
# Helmet violation capture frame
helmet_violation_frame = tk.Frame(violation_frame, background="#a6a6a6")
helmet_violation_frame.place(relx=0, rely=0.1, relwidth=1.0, relheight=0.4, anchor="nw")
helmet_violation_label = tk.Label(helmet_violation_frame, text="Helmet Violation", font=("Arial", 12), background="#a6a6a6")
helmet_violation_label.grid(row=0, column=0)

# Passenger violation capture frame
passenger_violation_frame = tk.Frame(violation_frame, background="#a6a6a6")
passenger_violation_frame.place(relx=0, rely=0.52, relwidth=1.0, relheight=0.4, anchor="nw")
passenger_violation_label = tk.Label(passenger_violation_frame, text="Passenger Violation", font=("Arial", 12), background="#a6a6a6")
passenger_violation_label.grid(row=0, column=0)
# Alarm Label
# alarm_label = tk.Label(violation_frame, text="Alarm", font=("Arial", 15), background="#545454", fg="white")
# alarm_label.grid(row=3, column=0, pady=10)



#------------------Record Tab------------------

# root = tk.Tk()
# root.geometry("800x600")

my_tree = ttk.Treeview(records_tab)

# Define Columns
my_tree['columns'] = ("ID", "File Name", "Image",  "Timestamp", "Violation")

# Format Columns
my_tree.column("#0", width=0, minwidth=50, stretch=tk.NO)
my_tree.column("ID", anchor="center", width=50)
my_tree.column("File Name", anchor="w", width=140)
my_tree.column("Image", anchor="w", width=180)
my_tree.column("Timestamp", anchor="w", width=140)
my_tree.column("Violation", anchor="w", width=140)

# Create Headings
my_tree.heading("#0", text="", anchor="w")
my_tree.heading("ID", text="ID", anchor="center")
my_tree.heading("File Name", text="File Name", anchor="w")
my_tree.heading("Image", text="Image", anchor="w")
my_tree.heading("Timestamp", text="Timestamp", anchor="w")
my_tree.heading("Violation", text="Violation", anchor="w")

# Add Data


# Function to fetch data from database
def fetch_violation_data():
    query = "SELECT id, filename, image_path, violation_timestamp, violation_type FROM helmet_detection"
    cursor.execute(query)
    return cursor.fetchall()

# Populate the Treeview
def populate_treeview(my_tree):
    for record in my_tree.get_children():
        my_tree.delete(record)
        
    data = fetch_violation_data()
    
    for record in data:
        my_tree.insert(parent='', index='end', iid=record[0], text="", values=(record[0],  record[1], record[2], record[3], record[4]))



my_tree.pack(pady=20)
populate_treeview(my_tree)


window.mainloop()

# data = [
#     ["F1", "Image1", "2021-09-01 12:00:00", "Helmet Violation"],
#     ["F2", "Image2", "2021-09-01 12:00:00", "Helmet Violation"],
#     ["F3", "Image3", "2021-09-01 12:00:00", "Passenger Violation"],
   
# ]

# count = 0