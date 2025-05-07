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

def download_images(top_10_message_divs, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)  # 创建下载目录

    total_blob_images = 0  # 统计所有blob图片总数

    for div in top_10_message_divs:
        # 找到所有 img 标签
        img_tags = div.find_all('img')
        
        # 统计当前div中的blob图片数
        blob_img_count = sum(1 for img in img_tags if img.get('src') and img.get('src').startswith('blob:'))
        total_blob_images += blob_img_count
        print(f"Found {blob_img_count} blob images in current div.")

        for img in img_tags:
            img_url = img.get('src')
            if img_url and img_url.startswith('blob:'):
                # 使用 JavaScript 获取 Blob 数据并转换为可下载的 URL
                result = tab.run_js(f"""
                    return fetch('{img_url}')
                        .then(response => response.blob())
                        .then(blob => {{
                            return {{
                                url: URL.createObjectURL(blob),
                                type: blob.type
                            }};
                        }}); 
                """)

                download_url = result['url']
                mime_type = result['type']

                # 根据 MIME 类型确定文件扩展名
                if mime_type == 'image/png':
                    file_extension = '.png'
                elif mime_type == 'image/jpeg':
                    file_extension = '.jpg'
                elif mime_type == 'image/gif':
                    file_extension = '.gif'
                else:
                    file_extension = '.bin'  # 默认扩展名

                # 提取 Blob URL 中的 ID 作为文件名
                file_name = img_url.split('/')[-1] + file_extension  # 使用适当的扩展名
                img_path = os.path.join(download_folder, file_name)

                # 使用 JavaScript 下载图像
                tab.run_js(f"""
                    var link = document.createElement('a');
                    link.href = '{download_url}';
                    link.download = '{file_name}';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                """)

                print(f"Initiated download for: {img_path}")
                time.sleep(1)  # 确保下载请求之间有间隔，以避免过快

    print(f"Total blob images found: {total_blob_images}")



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
    translate_tab = tab.get_tab(url='volcengine.com')

    languageEn = (By.XPATH, "//div[@class='reverse']/following-sibling::div[@class='sc-ipEyDJ dqurTv']/div[@class='lang' and text()='英语']")
    if translate_tab.ele(languageEn):
        print("由于不明原因改成翻译为英文")
        translate_tab.ele(languageEn).click()
        time.sleep(2)
        language2 = (By.XPATH, "//div[@class='lang-search-recently']/div[@data-lang='zh']")
        language_option = translate_tab.ele(language2)
        language_option.click()
        print("强制改为翻译成中文")

    result1 = (By.XPATH, "//div[@class='slate-editor' and @contenteditable='false']")
    translated_text = translate_tab.ele(result1)
    input1 = (By.XPATH, '//div[@role="textbox" and @aria-multiline="true" and contains(@class, "slate-editor")]')
    input_box = translate_tab.ele(input1)
    input_box.clear()
    input_box.input(text)

    time.sleep(5)
    print("translated_text为：" + translated_text.text)
    return translated_text.text

# 处理网页内容
def process_webpage(url):
    tab.get(url)
    time.sleep(3)  # 等待页面加载
    menu1 = (By.XPATH, '//a[@href="#-1001036240821"]')
    menu_list = tab.ele(menu1)
    time.sleep(1)
    menu_list.click()
    container1 = (By.XPATH, '//div[@class="messages-container"]')
    messages_container = tab.ele(container1)
    time.sleep(2)

    # 使用BeautifulSoup解析HTML
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

    # 保留最大的10个
    top_10_message_divs = message_divs_sorted[:10]

    download_folder = r'D:\hexoblog\source\telegram'
    # 调用下载函数
    time.sleep(10) 

    download_images(top_10_message_divs, download_folder)

    # 遍历每条消息内容并进行翻译
    for message_div in top_10_message_divs:
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
                print(f"Processing text-content combined_text: {combined_text}")
                translated_text = translate_text(combined_text)

                # 将 translated_text 转义成 JavaScript 字符串
                safe_translated_text = json.dumps(f'<p style="color: purple;">{translated_text}</p>')

                # 使用原文内容匹配的 XPath 查询，找到浏览器中的目标元素
                target_div = tab.ele((By.XPATH, f"//div[contains(@class, 'text-content') and contains(., '{text_content_list[0]}')][not(@data-translated)]"))

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
                print(f"Processing WebPage-text combined_text: {combined_text}")
                translated_text = translate_text(combined_text)

                # 将 translated_text 转义成 JavaScript 字符串
                safe_translated_text = json.dumps(f'<p style="color: purple;">{translated_text}</p>')

                # 使用原文内容匹配的 XPath 查询，找到浏览器中的目标元素

                if len(text_content_list) > 1:
                    # 尝试使用 text_content_list[1]
                    target_div = tab.ele((By.XPATH, f"//div[contains(@class, 'WebPage-text') and contains(., '{text_content_list[1]}')][not(@data-translated)]"))
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

    # 保留最大的10个
    top_10_message_divs = message_divs_sorted[:10]
    
    

    translated_text_divs = ''.join(str(div) for div in top_10_message_divs)

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
    <link rel="stylesheet" href="telegram.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
""")  # 开始写入 HTML 模板

        for div in translated_text_divs:
            file.write(str(div))  # 将每个 div 的 HTML 内容写入文件
            
        file.write("""\n</body>
</html>""")  # 结束 <body> 和 </html> 标签

    print(f"Translated messages saved to {output_file_path}")

# 测试
url = 'https://web.telegram.org/a/#-1001036240821'
processed_html = process_webpage(url)
# 定义下载目录




