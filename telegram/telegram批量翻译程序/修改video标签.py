import os
from bs4 import BeautifulSoup

# ===== 配置部分 =====
html_file = r"D:\hexoblog\source\telegram\telegram_1dayOnceUpdate35_2.html"   # 要读取并覆盖写回的 html 文件
video_folder = r"D:\hexoblog\source\telegram\1天30条的imgvideo"  # 视频所在目录
video_rel_path = "1天30条的imgvideo"   # HTML 中使用的相对路径


# ===== 读取 HTML =====
with open(html_file, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")


# ===== 查找所有 message-xxxx 的 div =====
message_divs = soup.find_all("div", id=lambda x: x and x.startswith("message-"))

print(f"共找到 {len(message_divs)} 个 message div")

inserted_count = 0
removed_telegram_video_count = 0

for message_div in message_divs:

    # 删除 telegram 视频标签
    all_videos = message_div.find_all("video")
    for v in all_videos:
        src = v.get("src", "")
        if "telegram" in src.lower():   # 检查是否包含 telegram
            v.decompose()
            removed_telegram_video_count += 1
            print(f"删除包含 telegram 的 video 标签: src={src}")

    # 获取 message id
    try:
        msg_id = message_div["id"].split("-")[1]
    except:
        continue

    # 判断本地视频文件是否存在
    local_video_path = os.path.join(video_folder, f"{msg_id}.mp4")
    if not os.path.exists(local_video_path):
        continue

    # 查找 media-inner
    media_inner = message_div.find("div", class_="media-inner")
    if not media_inner:
        continue

    # 创建本地 video 标签
    new_video = soup.new_tag("video")
    new_video["autoplay"] = ""
    new_video["src"] = f"{video_rel_path}/{msg_id}.mp4"
    new_video["class"] = "full-media"
    new_video["muted"] = ""
    new_video["loop"] = ""
    new_video["playsinline"] = ""
    new_video["disablepictureinpicture"] = ""
    new_video["draggable"] = "true"

    # 插入位置：canvas 后面优先，否则追加到 media-inner
    first_canvas = media_inner.find("canvas")
    if first_canvas:
        first_canvas.insert_after(new_video)
    else:
        media_inner.append(new_video)

    inserted_count += 1
    print(f"已插入本地视频 => message-{msg_id}")


# ===== 覆盖写回原 HTML 文件 =====
with open(html_file, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("\n====== 处理完成 ======")
print(f"删除包含 telegram 的 <video> 标签：{removed_telegram_video_count}")
print(f"插入本地视频标签：{inserted_count}")
print(f"已覆盖写回文件：{html_file}")
