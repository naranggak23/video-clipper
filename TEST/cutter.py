import tkinter as tk
from tkinter import messagebox
import os
import subprocess

def generate_output_filename(base_path='output', base_name='video', ext='mp4'):
    """Generate the next available output filename."""
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    counter = 1
    while True:
        filename = os.path.join(base_path, f"{base_name}{counter:03d}.{ext}")
        if not os.path.exists(filename):
            return filename
        counter += 1

def extract_video():
    start_time = entry_start_time.get()
    video_url = entry_video_url.get()

    if not start_time or not video_url:
        messagebox.showerror("Input Error", "Please enter both start time and video URL.")
        return

    output_file = generate_output_filename()

    # FFmpeg command
    command = f"ffmpeg -ss {start_time} -i {video_url} -t 10 -c copy {output_file}"

    try:
        subprocess.run(command, shell=True, check=True)
        messagebox.showinfo("Success", f"Video extracted successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("FFmpeg Error", str(e))

# Create the main application window
root = tk.Tk()
root.title("Video Extractor")

# Create and place labels and entry widgets
tk.Label(root, text="Start Time (HH:MM:SS):").grid(row=0, column=0, padx=10, pady=10)
entry_start_time = tk.Entry(root)
entry_start_time.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Video URL:").grid(row=1, column=0, padx=10, pady=10)
entry_video_url = tk.Entry(root)
entry_video_url.grid(row=1, column=1, padx=10, pady=10)

# Create and place the extract button
btn_extract = tk.Button(root, text="Extract Video", command=extract_video)
btn_extract.grid(row=2, columnspan=2, pady=20)

# Run the application
root.mainloop()
