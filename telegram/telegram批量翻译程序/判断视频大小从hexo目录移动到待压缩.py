import os
import shutil

folder_path = r'D:\hexoblog\source\telegram\1天30条的imgvideo'
size_limit_mb = 25
target_path = r'E:\ai_analyze\telegram批量翻译程序\待压缩'

# 确保目标文件夹存在
os.makedirs(target_path, exist_ok=True)

# 遍历文件夹并找到符合条件的文件
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    # 检查是否为 MP4 文件且大于指定大小
    if filename.endswith(".mp4") and os.path.getsize(file_path) > size_limit_mb * 1024 * 1024:
        # 移动文件到目标路径
        shutil.move(file_path, os.path.join(target_path, filename))
        print(f"移动文件: {filename} 到 {target_path}")
