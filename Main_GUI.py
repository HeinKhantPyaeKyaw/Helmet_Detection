import tkinter as tk
from tkinter import ttk, filedialog
import alarm_functions
import video_capture
import sqlite3
from PIL import Image, ImageTk

db_path = "helmet_detection.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the main window
window = tk.Tk()
window.title("QuadLink Helmet Detection System")
window.geometry("720x600")
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
frame_label1.grid(row=0, column=0, columnspan=3, pady=10)
# alarmNoti_label = tk.Label(video_frame, text="Alarm: ", font=("Arial", 20), fg="white", background="#545454")
# alarmNoti_label.grid(row=0, column=1, pady=10)
# ------------------Video Capture Frame------------------
video_canvas = tk.Canvas(video_frame, width=640, height=480, background="black")
video_canvas.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=10)

# Capture Date and Time Label
capture_datetime_label = tk.Label(video_frame, text="Capture Date and Time", font=("Arial", 15), fg="white", background="#545454")
capture_datetime_label.grid(row=2, column=0, columnspan=3, pady=10)



# Indicator Light
# my_canvas = tk.Canvas(video_frame, width=50, height=50, background="#545454", bd=0, highlightthickness=0)
# my_canvas.grid(row=0, column=2, pady=10)
# indicator = my_canvas.create_oval(10, 10, 40, 40, fill="green", tags="indicator")


# Button to start live video
live_video_btn = tk.Button(video_frame, text="Start Live Video", command=lambda: video_capture.start_live_video(video_canvas,))
live_video_btn.grid(row=3, column=0, pady=10)

# Button to upload video
upload_video_btn = tk.Button(video_frame, text="Upload Video", command=lambda: video_capture.upload_video(video_canvas,))
upload_video_btn.grid(row=3, column=1, pady=10)

# Button to stop video
stop_video_btn = tk.Button(video_frame, text="Stop", command=lambda: video_capture.stop_video(video_canvas))
stop_video_btn.grid(row=3, column=2, pady=10)

#------------------Record Tab------------------

my_tree = ttk.Treeview(records_tab)

# Create a frame for the Treeview header (for the refresh button)
header_frame = tk.Frame(records_tab)
header_frame.pack(fill="x", pady=10)

# Add the Refresh Button to the header frame
refresh_button = tk.Button(
    header_frame,
    text="Refresh Records",
    command=lambda: populate_treeview(my_tree),
    bg="gray",
    fg="black",
    font=("Arial", 12)
)
refresh_button.pack(side="right", padx=10)

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

# Frame for displaying selected record details
record_detail_frame = tk.Frame(records_tab, background="black")
record_detail_frame.pack(fill="x", pady=10)

# Add widgets for displaying image and details
selected_image_label = tk.Label(record_detail_frame, text="Selected Image", background="#f0f0f0")
selected_image_label.grid(row=0, column=0, padx=10, pady=10)

selected_image_canvas = tk.Canvas(record_detail_frame, width=200, height=150, background="black", highlightthickness=0)
selected_image_canvas.grid(row=0, column=0, padx=10, pady=10)

record_info_label = tk.Label(
    record_detail_frame,
    text="",
    background="black",
    foreground="white",
    font=("Arial", 12),
    justify="left"
)
record_info_label.grid(row=0, column=1, padx=10, pady=10, sticky="nw")

# Function to handle selection
def display_selected_record(event):
    selected_item = my_tree.selection()
    if selected_item:
        record = my_tree.item(selected_item)["values"]
        record_id, file_name, image_path, timestamp, violation_type = record

        # Display the image
        try:
            img = Image.open(image_path).resize((200, 150))
            img_tk = ImageTk.PhotoImage(img)
            selected_image_canvas.image = img_tk  # Keep reference to avoid garbage collection
            selected_image_canvas.create_image(0, 0, anchor="nw", image=img_tk)
        except Exception as e:
            selected_image_canvas.delete("all")
            selected_image_canvas.create_text(
                100, 75, text="Image not found", fill="white", font=("Arial", 10)
            )

        # Update the info label
        record_info_label.config(
            text=(
                f"ID: {record_id}\n"
                f"File Name: {file_name}\n"
                f"Timestamp: {timestamp}\n"
                f"Violation: {violation_type}"
            )
        )

# Bind selection event
my_tree.bind("<<TreeviewSelect>>", display_selected_record)


populate_treeview(my_tree)


window.mainloop()