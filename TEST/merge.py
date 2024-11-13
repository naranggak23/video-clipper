import os
import subprocess
from pathlib import Path

folder_name = "./VIDEO_03"  # Atau '..\\VIDEO_02' jika benar-benar dibutuhkan
print("Current Working Directory:", os.getcwd())  # Menampilkan direktori kerja
print("Folder Exists:", os.path.exists(folder_name))  # Mengecek apakah folder_name ada


# 2. Ambil semua file di dalam folder dan filter hanya file dengan ekstensi .mp4
file_list = [f for f in os.listdir(folder_name) if f.endswith('.mkv')]

print(f"\033[1;92m{file_list}\033[0m")

# 3. Urutkan file secara alfabet
sorted_files = sorted(file_list)

# 4. Buat file_list.txt untuk ffmpeg
with open("file_list.txt", "w") as f:
    for file_name in sorted_files:
        # Cantumkan path lengkap untuk memastikan ffmpeg dapat menemukannya
        f.write(f"file '{os.path.join(folder_name, file_name)}'\n")

# 5. Tentukan nama output berdasarkan nama folder
output_name = f"{folder_name}.mkv"

# 6. Jalankan ffmpeg untuk menggabungkan video
subprocess.run([
    "ffmpeg", "-f", "concat", "-safe", "0", "-i", "file_list.txt", "-c",  "copy", "-loglevel", "verbose", "-y", output_name
])

file_path = Path(output_name)
file_size = file_path.stat().st_size
file_size_mb = file_size / (1024*1024)
print(f"Video berhasil digabung menjadi {output_name}; size : {file_size_mb}")
