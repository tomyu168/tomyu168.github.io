import os

directory_path = "D:/hexoblog/source/telegram/aa"

directory_path = "D:/hexoblog/source/telegram/aa"
for filename in os.listdir(directory_path):
    # 检查文件是否以 '_1' 结尾并且紧接着文件扩展名
    if filename.endswith('_1.mp4') or filename.endswith('_1.MOV'):
        # 移除文件名中的 '_1'
        new_filename = filename.replace('_1', '', 1)
        
        # 构建旧文件和新文件的完整路径
        old_file = os.path.join(directory_path, filename)
        new_file = os.path.join(directory_path, new_filename)
        
        # 重命名文件
        os.rename(old_file, new_file)
        print(f"Renamed {filename} to {new_filename}")
    else:
        print(f"Skipping {filename}, does not match pattern.")
