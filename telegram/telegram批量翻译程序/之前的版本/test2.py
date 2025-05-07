from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import By
import time
import re
from bs4 import BeautifulSoup
import os
import requests
import json

# 设置Chromium选项
do1 = ChromiumOptions().set_paths(local_port=9111, user_data_path=r'C:/Users/A/AppData/Local/Google/Chrome/User Data')
tab = ChromiumPage(addr_or_opts=do1)
tab.set.NoneElement_value('没找到')

import os
import time
import base64
from selenium.webdriver.common.by import By

def download_images(top_limit_message_divs, download_folder, max_retries=6):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)  # 创建下载目录

    total_blob_images = 0  # 统计所有 blob 图片总数

    for div in top_limit_message_divs:
        # 找到所有 img 标签
        img_tags = div.find_all('img')

        # 替换 ./ 为完整路径
        for img in img_tags:
            img_url = img.get('src')
            if img_url and img_url.startswith('./'):
                img['src'] = 'https://web.telegram.org/a/' + img_url.lstrip('./')

        # 只保留不与 video 标签并列且不以 ./ 开头的 img 标签
        filtered_img_tags = [
            img for img in img_tags
            if not (img.find_previous_sibling('video') or img.find_next_sibling('video'))
            and not img.get('src', '').startswith('./')
        ]

        blob_img_count = sum(1 for img in filtered_img_tags if img.get('src') and img.get('src').startswith('blob:'))
        total_blob_images += blob_img_count
        print(f"Found {blob_img_count} blob images in current div after filtering.")

        for i, img in enumerate(filtered_img_tags):
            img_url = img.get('src')
            if img_url and img_url.startswith('blob:') and 'full-media' in img.get('class', []):
                message_div_id = div['id']
                imgxpath = (By.XPATH, f'(//div[@id="{message_div_id}"]//img[contains(@class, "full-media") and starts-with(@src, "blob:")])')
                
                img_element = tab.ele(imgxpath)
                # 检查是否存在多个符合条件的 img 标签
                imgMorethan1xpath = (By.XPATH, f'(//div[@id="{message_div_id}"]//img[contains(@class, "full-media") and starts-with(@src, "blob:")])[2]')
                img_element2 = tab.ele(imgMorethan1xpath)

                if img_element2:  # 多个 blob 图片，使用 base64 下载
                    print(f"Preparing to download multi imgs")
                    file_name = img_url.split('/')[-1] + '.jpg'
                    img_path = os.path.join(download_folder, file_name)
                    
                    for attempt in range(max_retries):
                        result = tab.run_js(f"""
                            return fetch('{img_url}')
                                .then(response => response.blob())
                                .then(blob => {{
                                    return new Promise((resolve, reject) => {{
                                        const reader = new FileReader();
                                        reader.onloadend = () => resolve(reader.result.split(',')[1]);
                                        reader.onerror = reject;
                                        reader.readAsDataURL(blob);
                                    }});
                                }});
                        """)

                        img_data = base64.b64decode(result)  # 转换为二进制数据
                        with open(img_path, 'wb') as img_file:
                            img_file.write(img_data)

                        time.sleep(3)
                        if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
                            print(f"Saved image to: {img_path}")
                            break
                        else:
                            print(f"Retry {attempt + 1}/{max_retries} for image {img_url} failed.")
                            time.sleep(1)
                    else:
                        print(f"Failed to download image {img_url} after {max_retries} attempts.")

                else:  # 只有一张符合条件的图片，模拟右键下载
                    print(f"Preparing to download single img: {img_url}")
                    img_element.scroll.to_see()
                    time.sleep(1)
                    tab.actions.r_click(img_element)
                    # img_element.click.right()
                    time.sleep(1)

                    downloadxpath = (By.XPATH, f'//div[@id="{message_div_id}"]//div[@class="MenuItem compact" and normalize-space(.) = "Download"]')
                    download = tab.ele(downloadxpath)

                    # 设置下载路径和文件名
                    tab.set.download_path(download_folder)
                    tab.set.download_file_name(img_url.split('/')[-1].strip())
                    download.click()
                    time.sleep(1)

    print(f"Total blob images found: {total_blob_images}")


def mute_autoplay_videos(message_divs):
    for div in message_divs:
        # 找到所有 video 标签
        video_tags = div.find_all('video')
        
        for video in video_tags:
            # 如果存在 autoplay 属性，替换为 autoplay muted
            if 'autoplay' in video.attrs:
                video['muted'] = ''  # 添加 muted 属性
                print(f"Updated video tag: {video}")  # 打印更新后的 video 标签


# 处理网页内容
def process_webpage(url_base, message_limit):
    # 指定输出文件路径
    output_file_path = r'D:\hexoblog\source\telegram\telegram_translated_messages.html'

    # 创建文件并写入 HTML 内容
    with open(output_file_path, 'w', encoding='utf-8') as file:
        # 写入 HTML 模板
        file.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Styled Message</title>
    <link rel="stylesheet" href="telegram2.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>

<script type="text/javascript">
    document.addEventListener("DOMContentLoaded", function() {
    const lazyElements = document.querySelectorAll('.lazy');

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const src = el.getAttribute('data-src');
                if (src) {
                    if (el.tagName === 'IMG' || el.tagName === 'VIDEO') {
                        el.src = src;
                        el.removeAttribute('data-src'); // 移除 data-src
                    }
                    observer.unobserve(el); // 停止观察已加载元素
                }
            }
        });
    }, { rootMargin: "0px 0px 200px 0px" }); // 提前 200px 加载

    lazyElements.forEach(el => observer.observe(el));
});

</script>
<body>
""")  # 开始写入 HTML 模板

    # 遍历编号数组
    for chat_id in chat_ids:
        # 拼接URL和menu XPATH
        url = url_base + chat_id
        tab.get(url)
        time.sleep(3)  # 等待页面加载
        menu1 = (By.XPATH, f'//a[@href="#-{chat_id}"]')
        menu_list = tab.ele(menu1)
        time.sleep(1)
        menu_list.click()

        button1 = (By.XPATH, '//div[@class="Y2NKrpKj u62x81QI"]/button')
        buttondown = tab.ele(button1)
        buttondown.click()
        time.sleep(3)
        container1 = (By.XPATH, '//div[@class="messages-container"]')
        messages_container = tab.ele(container1)
        time.sleep(2)

        
        total_videos = 0
        total_imgs = 0

        
        soup = BeautifulSoup(messages_container.html, 'html.parser')

        # 删除不需要的元素
        for meta_span in soup.find_all('span', class_='MessageMeta'):
            meta_span.decompose()
        for message_title in soup.find_all('span', class_='message-title-name'):
            message_title.decompose()
        for video_duration in soup.find_all('div', class_='message-media-duration'):
            video_duration.decompose()
        for button_react in soup.find_all('button', class_='message-reaction'):
            button_react.decompose()
        for reply in soup.find_all('div', class_='CommentButton'):
            reply.decompose()
        for reply2 in soup.find_all('div', class_='recent-repliers'):
            reply2.decompose()

        # 提取 message-list-item 中的消息
        message_divs = soup.find_all('div', class_='message-list-item', id=lambda x: x and x.startswith('message-'))

        # 提取 id 中的数字部分并排序
        message_divs_sorted = sorted(
            message_divs,
            key=lambda div: int(div['id'].split('-')[1]),
            reverse=True
        )

        # 根据指定的消息数量保留消息
        top_limit_message_divs = message_divs_sorted[:message_limit]
        
        download_folder = r'D:\hexoblog\source\telegram'
        # 调用下载函数

        # download_images(top_limit_message_divs, download_folder)

        # for div in top_limit_message_divs:
        #     # 找到所有 img 标签
        #     img_tags = div.find_all('img')

        #     for img in img_tags:
        #         img_url = img.get('src')
        #         if img_url and img_url.startswith('blob:'):
        #             # 获取图片的文件名并添加后缀
        #             new_img_url = img_url.split('/')[-1] + ".jpg"
        #             # 修改 img 的 src 属性为 data-src
        #             img['data-src'] = new_img_url
        #             # 删除原有的 src 属性
        #             del img['src']
        #             if 'full-media' in img['class']:
        #                 # 如果 'lazy' 不在 class 列表中，则添加
        #                 if 'lazy' not in img['class']:
        #                     img['class'].append('lazy')

        #         if img_url and img_url.startswith('./'):
        #             # 将 './' 替换为完整路径
        #             img_url = 'https://web.telegram.org/a/' + img_url.lstrip('./')
        #             img['src'] = img_url


        # for message_div in top_limit_message_divs:
        #     element = tab.ele(f'@id={message_div['id']}')
        #     element.scroll.to_see()
        #     time.sleep(7)

        for message_div in top_limit_message_divs:
            # 将滚动条移动到当前 message_div 的位置
            element = tab.ele(f'@id={message_div["id"]}')
            element.scroll.to_see()
            time.sleep(7)
            # 检查当前 message_div 是否包含 video 标签
            message_div_id = message_div['id']
            videoxpath = (By.XPATH, f'//div[@id="{message_div_id}"]//video')
            
            if videoxpath:
                print(f"Video tag found in div with ID: {message_div['id']}")
                # 这里可以继续对 video_tag 进行操作，比如下载视频等
                video_element = tab.ele(videoxpath)
                video_src = video.get('src')
                if video_src and video_src.startswith('./progressive/document'):
                    # 提取文件名
                    file_name = video_src.replace('./progressive/document', '')
                    print(f"Preparing to download video with filename: {file_name.strip()}")

                    # 定义视频标签的 XPath
                    message_div_id = message_div['id']
                    videoxpath = (By.XPATH, f'//div[@id="{message_div_id}"]//video')
                    video_element = tab.ele(videoxpath)  # 获取视频元素
                    tab.actions.r_click(video_element)

                    # 等待菜单出现
                    time.sleep(2)  # 可根据需要调整等待时间

                    # 定义下载选项的 XPath
                    downloadxpath = (By.XPATH, f'//div[@id="{message_div_id}"]//div[@class="MenuItem compact" and normalize-space(.) = "Download"]')
                    download = tab.ele(downloadxpath)  # 获取下载按钮

                    # 设置下载路径和文件名
                    tab.set.download_path(r'D:\hexoblog\source\telegram')  # 设置文件保存路径
                    tab.set.download_file_name(file_name.strip())  # 设置重命名文件名
                    time.sleep(2)
                    # 点击下载按钮
                    download.click()
                    video_src = file_name + ".mp4"
                    video['data-src'] = video_src
                    del video['src'] 
                    video['class'] = 'full-media lazy'
                    # 可选：等待下载完成
                    time.sleep(8)  # 根据下载时间进行调整
            else:
                print(f"No video tag found in div with ID: {message_div['id']}")

        mute_autoplay_videos(top_limit_message_divs)

        directory_path = "D:/hexoblog/source/telegram"

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

        translated_text_divs = ''.join(str(div) for div in top_limit_message_divs)

        for div in translated_text_divs:
            with open(output_file_path, 'a', encoding='utf-8') as file:
                file.write(str(div))  # 将每个 div 的 HTML 内容写入文件
            
    with open(output_file_path, 'a', encoding='utf-8') as file:
            file.write("\n</body>\n</html>")

    print(f"Translated messages saved to {output_file_path}")


chat_ids = ['1001036240821']
url_base = 'https://web.telegram.org/a/#-'
message_limit = 25

process_webpage(url_base, message_limit)




