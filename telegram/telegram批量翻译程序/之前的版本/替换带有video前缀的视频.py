import os

directory_path = r'E:\ai_analyze\telegram批量翻译程序\待压缩'

for filename in os.listdir(directory_path):
            # Check if filename starts with 'video'
            if filename.startswith("video"):
                # New filename without 'video' prefix
                new_filename = filename[len("video"):]
                # Full paths for renaming
                old_file = os.path.join(directory_path, filename)
                new_file = os.path.join(directory_path, new_filename)
                # Rename the file
                os.rename(old_file, new_file)