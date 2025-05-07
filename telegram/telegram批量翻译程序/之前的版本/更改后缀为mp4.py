import os

def rename_file_extensions(directory):
    # 检查目录是否存在
    if not os.path.isdir(directory):
        print(f"The directory {directory} does not exist.")
        return

    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        # 分离文件名和扩展名
        base, ext = os.path.splitext(filename)
        
        # 检查扩展名是否为 .MP4
        if ext == '.MP4':
            # 构造旧文件路径和新文件路径
            old_file = os.path.join(directory, filename)
            new_file = os.path.join(directory, base + '.mp4')

            # 重命名文件
            os.rename(old_file, new_file)
            print(f"Renamed {filename} to {base + '.mp4'}")

# 使用示例
directory_path = r'D:\hexoblog\source\telegram'  # 替换为你要操作的文件夹路径
rename_file_extensions(directory_path)