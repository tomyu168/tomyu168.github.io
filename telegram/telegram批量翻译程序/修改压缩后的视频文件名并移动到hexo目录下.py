import os
import shutil

# 指定源目录和目标目录
source_folder = r'E:\ai_analyze\telegram批量翻译程序\待压缩\已转换'  # 替换为你的源目录路径
target_folder = r'D:\hexoblog\source\telegram\1天30条的imgvideo'  # 替换为你的目标目录路径
del_folder = r'E:\ai_analyze\telegram批量翻译程序\待压缩'
# 确保目标文件夹存在
os.makedirs(target_folder, exist_ok=True)

# 遍历源文件夹中的所有文件
for filename in os.listdir(source_folder):
    file_path = os.path.join(source_folder, filename)
    
    # 检查文件是否为文件而不是目录
    if os.path.isfile(file_path):
        # 去掉文件名中的 .mpeg4.aac
        new_filename = filename.replace('.x264.aac', '')
        new_file_path = os.path.join(source_folder, new_filename)
        
        # 重命名文件
        os.rename(file_path, new_file_path)
        
        # 如果文件是 MP4 文件，则移动到目标目录
        if new_filename.endswith('.mp4'):
            shutil.move(new_file_path, os.path.join(target_folder, new_filename))
            print(f"已移动文件: {new_filename} 到 {target_folder}")

for filename in os.listdir(del_folder):
    if filename.endswith('.mp4'):
        os.remove(os.path.join(del_folder, filename))
        print(f"已删除文件: {filename} 从 {del_folder}")

size_limit = 25 * 1024 * 1024  # 转换为字节

# 遍历文件夹中的所有文件
for filename in os.listdir(target_folder):
    file_path = os.path.join(target_folder, filename)
    
    # 检查是否为文件
    if os.path.isfile(file_path):
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 如果文件大小超过限制，删除文件
        if file_size > size_limit:
            os.remove(file_path)
            print(f"已删除文件：{file_path}，大小为 {file_size / (1024 * 1024):.2f} MB")

print("处理完成！")