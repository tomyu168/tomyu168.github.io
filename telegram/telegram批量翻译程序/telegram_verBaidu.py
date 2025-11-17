from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import By
import time
import re
from bs4 import BeautifulSoup
import os
import requests
import json
import base64
from telethon.sync import TelegramClient

# 设置Chromium选项
# do1 = ChromiumOptions().set_paths(local_port=9111, user_data_path=r'C:/Users/A/AppData/Local/Google/Chrome/User Data')
do1 = ChromiumOptions().set_paths(local_port=9111, user_data_path=r'E:/chrometmp/User Data')
tab = ChromiumPage(addr_or_opts=do1)
chat_ids = []
url_base = 'https://web.telegram.org/a/#'
message_limit = 30

api_id = '24053889'
api_hash = '8e1a8794cf3c36a56097cd8d3f3775b2'

# 代理设置
proxy = ('socks5', '127.0.0.1', 7890)  # 代理地址和端口需要根据实际情况调整

# 登录并创建客户端



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

                        time.sleep(1)
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

                    # downloadxpath = (By.XPATH, f'//div[@id="{message_div_id}"]//div[@class="MenuItem compact" and (normalize-space(.) = "Download" or normalize-space(.) = "Cancel Download")]')
                    downloadxpath = (By.XPATH, f'//div[@class="MenuItem compact" and (normalize-space(.) = "Download" or normalize-space(.) = "Cancel Download")]')
                    download = tab.ele(downloadxpath)

                    # 设置下载路径和文件名
                    tab.set.download_path(download_folder)
                    tab.set.download_file_name(img_url.split('/')[-1].strip())
                    download.click()
                    time.sleep(3)

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


def rename_file_extensions(directory):
    for filename in os.listdir(directory):
        # 分离文件名和扩展名
        base, ext = os.path.splitext(filename)

        # 检查扩展名是否为 .MP4
        if ext == '.MP4':
            # 构造旧文件路径和新文件路径
            old_file = os.path.join(directory, filename)
            new_file = os.path.join(directory, base + '.mp4')

            # 如果文件已存在，则在文件名后添加序号
            count = 1
            while os.path.exists(new_file):
                new_file = os.path.join(directory, f"{base}_{count}.mp4")
                count += 1

            # 重命名文件
            os.rename(old_file, new_file)
            print(f"Renamed {filename} to {new_file}")

# 判断是否为非中文且非链接文本
def is_non_chinese_and_non_link(text):
    # 检查文本是否不包含中文、链接，且不包含30个字符以内的英文字母和以@开头的英文字母
    return (
        text and
        not re.search(r'[\u4e00-\u9fff]', text) and
        'http' not in text and
        'www' not in text and
        not re.search(r'^[a-zA-Z]{1,30}$', text) and  # 检查文本是否为1到30个字符的英文字母
        not re.search(r'^@[a-zA-Z]{1,30}$', text)    # 检查文本是否以@开头并且为1到30个字符的英文字母
    )

# 执行翻译并返回结果
def translate_text(text):
    translate_tab = tab.get_tab(url='fanyi.baidu.com/')
    time.sleep(3)
    translate_tab.refresh()
    time.sleep(3)
    # while translate_tab.ele('t:iframe'):
    #     print("检测到 iframe，刷新页面...")
    #     translate_tab.refresh()
    #     time.sleep(6)  # 等待页面加载
    # languageEn = (By.XPATH, "//div[@class='reverse']/following-sibling::div[@class='sc-ipEyDJ dqurTv']/div[@class='lang' and text()='英语']")
    # if translate_tab.ele(languageEn):
    #     print("由于不明原因改成翻译为英文")
    #     translate_tab.ele(languageEn).click()
    #     time.sleep(2)
    #     language2 = (By.XPATH, "//div[@class='lang-search-recently']/div[@data-lang='zh']")
    #     language_option = translate_tab.ele(language2)
    #     language_option.click()
    #     print("强制改为翻译成中文")

    result1 = (By.XPATH, "//div[@class='aytrOJav' and @id='machineResContent']")  
    translated_text = translate_tab.ele(result1)
    input1 = (By.XPATH, "//div[contains(@class, 'ioHXHxf9') and @contenteditable='true' and @role='textbox']")
    input_box = translate_tab.ele(input1)
    input_box.clear()
    input_box.input(text)

    time.sleep(15)
    # print("translated_text为：" + translated_text.text)
    return translated_text.text

# 处理网页内容
def process_webpage(client, url_base, message_limit, chat_ids):
    # 指定输出文件路径
    output_file_path = r'D:\hexoblog\source\telegram\telegram_1dayOnceUpdate35.html'

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
        menu1 = (By.XPATH, f'//a[@href="#{chat_id}"]')
        menu_list = tab.ele(menu1)
        time.sleep(1)
        menu_list.click()

        # prev = 0
        # while True:
        #     current_html = tab.html
        #     msgs = current_html.count('message-list-item')
        #     if msgs == prev:
        #         break
        #     prev = msgs
        #     tab.scroll.down(2000)
        #     time.sleep(1)

        button1 = (By.XPATH, '//div[@class="Y2NKrpKj u62x81QI"]/button')
        buttondown = tab.ele(button1)
        buttondown.click()
        time.sleep(3)
        container1 = (By.XPATH, '//div[@class="messages-container"]')
        messages_container = tab.ele(container1)
        time.sleep(2)

        try:
            entity = client.get_entity(int(chat_id))  # 将 chat_id 转成 int
            messagesvideo = client.get_messages(entity, limit=message_limit)
        except ValueError as e:
            print(f"无法找到 chat_id 对应实体: {chat_id}, 跳过。错误: {e}")
            continue

        download_folder = r"D:\hexoblog\source\telegram\1天30条的imgvideo"
        os.makedirs(download_folder, exist_ok=True)

        video_count = 0
        for msg in messagesvideo:
            if msg.video or (msg.document and msg.document.mime_type and "video" in msg.document.mime_type):
                video_count += 1
                # 自动选择扩展名：优先从 mime_type，回退到 mp4
                ext = "mp4"
                try:
                    if msg.document and msg.document.mime_type:
                        mime = msg.document.mime_type  # 比如 "video/mp4"
                        ext_from_mime = mime.split('/')[-1]
                        if ext_from_mime:
                            ext = ext_from_mime.split('+')[0]  # 避免带 + 的情况
                except Exception:
                    pass

                file_path = os.path.join(download_folder, f"{msg.id}.{ext}")
                print(f"Downloading video => {msg.id} -> {file_path}")
                try:
                    client.download_media(msg, file=file_path)
                except Exception as e:
                    print(f"下载失败 msg.id={msg.id}: {e}")

        print(f"chat_id {chat_id} 在前 {message_limit} 条消息中有 {video_count} 个视频")

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(messages_container.html, 'html.parser')

        # 删除不需要的元素
        for videotags in soup.find_all('video', class_='full-media with-blurred-bg'):
            videotags.decompose()
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

        total_videos = 0
        total_imgs = 0


        for message_div in top_limit_message_divs:

            # 先处理 text-content
            print("处理text-content")
            text_content_divs = message_div.find_all('div', class_='text-content')
            print(f"当前的message_div的id为{message_div['id']}")

            for div in text_content_divs:
                text_content_list = []
                for text_content in div.find_all(text=True):
                    stripped_text = text_content.strip()  # 去除两端空格
                    if is_non_chinese_and_non_link(stripped_text):
                        text_content_list.append(stripped_text)

                combined_text = '\n'.join(text_content_list)
                if combined_text:
                    # print(f"Processing text-content combined_text: {combined_text}")
                    translated_text = translate_text(combined_text)

                    # 将 translated_text 转义成 JavaScript 字符串
                    safe_translated_text = json.dumps(f'<p style="color: purple;">{translated_text}</p>')

                    # 使用原文内容匹配的 XPath 查询，找到浏览器中的目标元素
                    # 检查文本中是否包含单引号
                    content_to_use = text_content_list[0]  # 默认使用第一个内容

                    if chat_id == '-1001443119244':
                        content_to_use = text_content_list[1]

                    # 构建 XPath 表达式
                    safe_xpath = ""
                    if "'" in content_to_use:
                        # 使用双引号包装并构建 XPath
                        safe_xpath = f'//div[contains(@class, "text-content") and contains(., "{content_to_use}")][not(@data-translated)]'
                    else:
                        # 直接使用单引号包装
                        safe_xpath = f"//div[contains(@class, 'text-content') and contains(., '{content_to_use}')][not(@data-translated)]"

                    if "'" in text_content_list[0] and '"' in text_content_list[0]:
                        original_content = text_content_list[0]
                        # 使用正则表达式去除所有引号
                        print("既包含了单引号又有双引号")
                        truncated_content = re.split(r'"', original_content)[0]
                        # 构建 XPath 表达式，使用 processed_content 进行匹配
                        safe_xpath = f"//div[contains(@class, 'text-content') and contains(., '{truncated_content}')][not(@data-translated)]"
                    # 定位元素
                    target_div = tab.ele((By.XPATH, safe_xpath))

                    if target_div:
                        target_div.run_js("this.setAttribute('data-translated', 'true');")
                        target_div.run_js(f"""
                            function insertAfter(newElement, targetElement) {{
                                var parentElement = targetElement.parentNode;
                                if (parentElement.lastChild === targetElement) {{
                                    parentElement.appendChild(newElement);
                                }} else {{
                                    parentElement.insertBefore(newElement, targetElement.nextSibling);
                                }}
                            }}
                            
                            var transDiv = document.createElement('div');
                            transDiv.className = 'translated_text';
                            transDiv.innerHTML = {safe_translated_text};
                            
                            insertAfter(transDiv, this);
                        """)
                    else:
                        print("未能找到任何元素 for text-content")

            # 处理 WebPage-text
            print("处理WebPage-text")
            webpage_text_divs = message_div.find_all('div', class_='WebPage-text')
            print(f"当前的message_div的id为{message_div['id']}")

            for div in webpage_text_divs:
                text_content_list = []
                for text_content in div.find_all(text=True):
                    stripped_text = text_content.strip()  # 去除两端空格
                    if is_non_chinese_and_non_link(stripped_text):
                        text_content_list.append(stripped_text)

                combined_text = '\n'.join(text_content_list)
                if combined_text:
                    # print(f"Processing WebPage-text combined_text: {combined_text}")
                    translated_text = translate_text(combined_text)

                    # 将 translated_text 转义成 JavaScript 字符串
                    safe_translated_text = json.dumps(f'<p style="color: purple;">{translated_text}</p>')

                    # 使用原文内容匹配的 XPath 查询，找到浏览器中的目标元素
                    # 检查文本中是否包含单引号
                    if len(text_content_list) > 1:
                        # 检查 text_content_list[1] 是否包含单引号
                        if "'" in text_content_list[1]:
                            # 使用双引号包装并构建 XPath
                            safe_xpath = f'//div[contains(@class, "WebPage-text") and contains(., "{text_content_list[1]}")][not(@data-translated)]'
                        else:
                            # 使用单引号包装
                            safe_xpath = f"//div[contains(@class, 'WebPage-text') and contains(., '{text_content_list[1]}')][not(@data-translated)]"
                        
                        # 定位元素

                        if "'" in text_content_list[1] and '"' in text_content_list[1]:
                            original_content = text_content_list[1]
                            # 使用正则表达式去除所有引号
                            print("既包含了单引号又有双引号")
                            truncated_content = re.split(r'"', original_content)[0]
                            # 构建 XPath 表达式，使用 processed_content 进行匹配
                            safe_xpath = f"//div[contains(@class, 'WebPage-text') and contains(., '{truncated_content}')][not(@data-translated)]"

                        target_div = tab.ele((By.XPATH, safe_xpath))

                    else:
                        # 如果 text_content_list[1] 不存在，使用 text_content_list[0]
                        target_div = tab.ele((By.XPATH, f"//div[contains(@class, 'WebPage-text') and contains(., '{text_content_list[0]}')][not(@data-translated)]"))



                    if target_div:
                        target_div.run_js("this.setAttribute('data-translated', 'true');")
                        target_div.run_js(f"""
                            function insertAfter(newElement, targetElement) {{
                                var parentElement = targetElement.parentNode;
                                if (parentElement.lastChild === targetElement) {{
                                    parentElement.appendChild(newElement);
                                }} else {{
                                    parentElement.insertBefore(newElement, targetElement.nextSibling);
                                }}
                            }}
                            
                            var transDiv = document.createElement('div');
                            transDiv.className = 'translated_text';
                            transDiv.innerHTML = {safe_translated_text};
                            
                            insertAfter(transDiv, this);
                        """)
                    else:
                        print("未能找到任何元素 for WebPage-text")


        for message_div in top_limit_message_divs[:]:  # 使用切片复制一份列表，以便在循环中修改原列表
            element = tab.ele(f"@id={message_div['id']}")
            if element is None:
                # 如果找不到元素，从列表中移除该元素
                print('scroll阶段发生找不到div异常！')
                top_limit_message_divs.remove(message_div)
                continue  # 跳过该元素

            # 如果找到元素，进行滚动操作
            element.scroll.to_see()
            time.sleep(5)


        container1 = (By.XPATH, '//div[@class="messages-container"]')
        messages_container = tab.ele(container1)
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
        message_divs = [
            div for div in soup.find_all('div', class_='message-list-item', id=lambda x: x and x.startswith('message-'))
            if div.find('div', class_='translated_text')
        ]


        # 提取 id 中的数字部分并排序
        message_divs_sorted = sorted(
            message_divs,
            key=lambda div: int(div['id'].split('-')[1]),
            reverse=True
        )
        
        top_limit_message_divs = message_divs_sorted[:message_limit]

        output_message_divs_path = r"D:\hexoblog\source\telegram\debug_divs.txt"

        with open(output_message_divs_path, "w", encoding="utf-8") as f:
            for div in top_limit_message_divs:
                f.write(f"===== {div['id']} =====\n")
                f.write(div.prettify())       # 输出格式化 HTML
                f.write("\n\n")
        print(f"[DEBUG] 已把 top_limit_message_divs 输出到 {output_message_divs_path}")


        directory_path = "D:/hexoblog/source/telegram/1天30条的imgvideo"
        download_folder = r'D:\hexoblog\source\telegram\1天30条的imgvideo'
        download_images(top_limit_message_divs, download_folder)

        for div in top_limit_message_divs:
            # 找到所有 img 标签
            img_tags = div.find_all('img')

            for img in img_tags:
                img_url = img.get('src')
                if img_url and img_url.startswith('blob:'):
                    # 获取图片的文件名并添加后缀
                    new_img_url = '1天30条的imgvideo/' + img_url.split('/')[-1] + ".jpg"
                    # 修改 img 的 src 属性为 data-src
                    img['data-src'] = new_img_url
                    # 删除原有的 src 属性
                    del img['src']
                    if 'full-media' in img['class']:
                        # 如果 'lazy' 不在 class 列表中，则添加
                        if 'lazy' not in img['class']:
                            img['class'].append('lazy')

                if img_url and img_url.startswith('./'):
                    # 将 './' 替换为完整路径
                    img_url = 'https://web.telegram.org/a/' + img_url.lstrip('./')
                    img['src'] = img_url


        

        translated_text_divs = ''.join(str(div) for div in top_limit_message_divs)

        for div in translated_text_divs:
            with open(output_file_path, 'a', encoding='utf-8') as file:
                file.write(str(div))  # 将每个 div 的 HTML 内容写入文件
            
    with open(output_file_path, 'a', encoding='utf-8') as file:
            file.write("\n</body>\n</html>")

    print(f"Translated messages saved to {output_file_path}")


with TelegramClient('session_name', api_id, api_hash, proxy=proxy) as client:
    # 检查是否已登录

    # 获取当前登录用户的聊天列表
    dialogs = client.get_dialogs()
    
    # 用于存储未读消息数大于等于35条的频道的 chat_id
    
    for dialog in dialogs:
        # 只获取频道或群组
        if dialog.is_channel:
            # 获取该频道的未读消息数
            unread_messages = dialog.unread_count
            # 如果未读消息数大于等于30条，将其 chat_id 添加到 chat_ids 列表中
            if unread_messages >= message_limit:
                chat_ids.append(str(dialog.id))  # 将 chat_id 转为字符串并添加到列表

    # 输出满足条件的频道 chat_ids
    print(f"未读消息数大于等于30条的频道 chat_ids: {chat_ids}")
    target_chat_id = '-1001224883656'
    if target_chat_id in chat_ids:
        chat_ids.remove(target_chat_id)  # 从列表中移除该 chat_id
    time.sleep(3)

    process_webpage(client, url_base, message_limit, chat_ids)


target_directory = r'D:\hexoblog\source\telegram\1天30条的imgvideo'
add_extensions_by_size(target_directory)

# ===== 配置部分 =====
html_file = r"D:\hexoblog\source\telegram\telegram_1dayOnceUpdate35.html"   # 要读取并覆盖写回的 html 文件
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


