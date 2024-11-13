import os
import random
import subprocess
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def gen_folder_name():
    base_name = 'VIDEO'
    suffix = 1
    while True: 
        folder_name = f"{base_name}_{suffix:02d}"
        if not os.path.exists(folder_name):
            return folder_name
        suffix += 1

# Helper function to generate unique filenames
def generate_filename(folder, ext):
    timestamp = time.time()  # Get current timestamp
    truncated_timestamp = str(timestamp).split('.')[1][:6]
    filename = f"{folder}/video_{truncated_timestamp}.{ext}"  # Format timestamp with microsecond precision
    return filename

# Function to get video duration using ffprobe
def get_video_duration(url):
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'format=duration',
            '-of', 'json', url
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"Error with ffprobe: {result.stderr.decode()}")
            return None
        metadata = json.loads(result.stdout)
        print(f"ffprobe output: {json.dumps(metadata, indent=2)}")  # Print raw output for debugging
        duration = float(metadata['format']['duration'])  # Ensure the duration is a float
        print(f"DURATION: {duration} seconds")
        return duration
    except Exception as e:
        print(f"Failed to get video info: {e}")
        return None


# Function to execute ffmpeg clipping
def clip_video(start_time, duration, output_path, url):
    cmd = [
        'ffmpeg',
        '-headers',
        'Referer: sextb.net',
        '-hwaccel', 'cuda',
        '-ss', str(start_time),          # Start time for the segment
        '-i', url,                       # Input stream URL
        '-t', str(duration),             # Duration of the segment
        '-reconnect', '1',               # Enable reconnect
        '-reconnect_at_eof', '1',        # Reconnect at EOF
        '-timeout', '300000',            # Set timeout (in milliseconds)
        '-c', 'copy',
        '-y',                            # Overwrite output file without asking
        output_path                      # Output file path
    ]

    print(f"Clipping from {start_time}s to {start_time + duration}s -> {output_path}")
    subprocess.run(cmd)

# Function to rename files based on their creation time
def rename_files_based_on_creation_time(folder, ext):
    files = [f for f in os.listdir(folder) if f.endswith(ext)]
    files.sort(key=lambda f: os.path.getctime(os.path.join(folder, f)))
    
    for index, file in enumerate(files, 1):
        new_name = f"{folder}/video{index:03d}.{ext}"  # Rename to ordered format
        old_file = os.path.join(folder, file)
        os.rename(old_file, new_name)  # Rename the file
        print(f"Renamed: {old_file} -> {new_name}")

# Function to merge video files into one
def merge_videos(folder_name, ext):
    file_list = [f for f in os.listdir(folder_name) if f.endswith(ext)]
    print(f"Files to merge: {file_list}")

    file_list.sort()
    
    # Write the file list to a text file for ffmpeg
    with open("file_list.txt", "w") as f:
        for file_name in file_list:
            f.write(f"file '{os.path.join(folder_name, file_name)}'\n")

    output_name = f"{folder_name}.mkv"
    # Run ffmpeg to merge the videos
    subprocess.run([
        "ffmpeg", "-hwaccel", 'cuda', "-f", "concat", "-safe", "0", "-i", "file_list.txt", "-c",  "copy", "-y", output_name
    ])

    file_path = Path(output_name)
    file_size = file_path.stat().st_size
    file_size_mb = file_size / (1024*1024)
    print(f"Videos successfully merged into {output_name}; size: {file_size_mb:.2f} MB")

# Main function to perform video clipping and merging
def start_clipping_and_merging():
    judul = gen_folder_name()  # Generate folder name dynamically
    duration = 2                #@param
    clips_per_minute = 4        #@param
    url = "https://vdownload-36.sb-cd.com/8/2/8294542-1080p.mp4?secure=SrC6XCz5DCoGmGxNgnByYA,1731465650&m=36&d=1&_tid=8294542" #@param{type:"string"}
    ext = "mkv"                 # Output video extension (fixed to MKV)
    interval_minutes = 5        #@param

    # Create output directory
    output_dir = f"./{judul}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get video duration using ffprobe
    video_duration = get_video_duration(url)
    if video_duration is None:
        return
    
    # Process video clipping in batches
    with ThreadPoolExecutor(max_workers=120) as executor:
        # Process each batch of clips
        for minute in range(0, int(video_duration) // 60, interval_minutes):  # 'video_duration' is now a float
            # Create tasks for this batch
            tasks = []
            for _ in range(clips_per_minute):
                random_start = minute * 60 + random.randint(0, 60 - duration)
                output_path = generate_filename(output_dir, ext)
                tasks.append((random_start, duration, output_path, url))

            # Submit the tasks in batches
            futures = [executor.submit(clip_video, *task) for task in tasks]
            # Wait for all tasks in the current batch to finish
            for future in futures:
                future.result()

    # Rename files after all clips are done
    rename_files_based_on_creation_time(output_dir, ext)
    
    # Merge clips into a single file
    merge_videos(output_dir, ext)
    
    print("Video clipping and merging completed successfully!")

if __name__ == "__main__":
    start_clipping_and_merging()
