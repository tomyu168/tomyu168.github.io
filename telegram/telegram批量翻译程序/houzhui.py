
import os



def add_extensions_by_size(directory):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        # 跳过文件夹
        if not os.path.isfile(filepath):
            continue

        # 判断是否已有后缀
        if '.' in filename:
            continue

        # 获取文件大小（单位：字节）
        file_size_bytes = os.path.getsize(filepath)
        file_size_mb = file_size_bytes / (1024 * 1024)

        # 判断大小并添加后缀
        if file_size_mb < 0.4:
            new_filename = filename + '.jpg'
        else:
            new_filename = filename + '.mp4'

        new_filepath = os.path.join(directory, new_filename)
        
        # 重命名文件
        os.rename(filepath, new_filepath)
        print(f"Renamed '{filename}' -> '{new_filename}'")

target_directory = r'D:\hexoblog\source\telegram\1天30条的imgvideo'
add_extensions_by_size(target_directory)


