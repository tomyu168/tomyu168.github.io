from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import By
import time
import re
from bs4 import BeautifulSoup

# 设置Chromium选项
do1 = ChromiumOptions().set_paths(local_port=9111, user_data_path=r'C:/Users/A/AppData/Local/Google/Chrome/User Data')
tab = ChromiumPage(addr_or_opts=do1)
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

    time.sleep(3)
    print("translated_text为：" + translated_text.text)
    return translated_text.text

# 处理网页内容
def process_webpage(url):
    tab.get(url)
    time.sleep(3)  # 等待页面加载
    menu1 = (By.XPATH, '//a[@href="#-1001000219802"]')
    menu_list = tab.ele(menu1)
    time.sleep(1)
    menu_list.click()
    container1 = (By.XPATH, '//div[@class="messages-container"]')
    messages_container = tab.ele(container1)
    time.sleep(2)

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(messages_container.html, 'html.parser')

    # 删除所有span class="MessageMeta"
    for meta_span in soup.find_all('span', class_='MessageMeta'):
        meta_span.decompose()  # 删除元素

    for message_title in soup.find_all('span', class_='message-title-name'):
        message_title.decompose()  # 删除元素

    for video_duration in soup.find_all('div', class_='message-media-duration'):
        video_duration.decompose()  # 删除元素

    for button_react in soup.find_all('button', class_='message-reaction'):
        button_react.decompose()  # 删除元素

    for reply in soup.find_all('div', class_='CommentButton'):
        reply.decompose()  # 删除元素

    for reply2 in soup.find_all('div', class_='recent-repliers'):
        reply2.decompose()  # 删除元素


    # 遍历每条消息内容并进行翻译
    for div in soup.find_all('div', class_='message-content-wrapper can-select-text'):
        for text_content in div.find_all(text=True):
            stripped_text = text_content.strip()  # 去除两端空格
            if is_non_chinese_and_non_link(stripped_text):
                parent_element = text_content.parent
                print("stripped_text为：" + stripped_text)
                translated_text = translate_text(stripped_text)
                

                # 在 parent_element 后插入翻译内容
                # 获取 text_content_div 和 text_content_div2
                # 获取当前处理的原文元素
                text_content_div = tab.ele((By.XPATH, f"//div[contains(@class, 'text-content') and contains(@class, 'clearfix') and contains(., '{stripped_text}')][not(@data-translated)]"))
                text_content_div2 = tab.ele((By.XPATH, f"//div[contains(@class, 'WebPage-text') and contains(., '{stripped_text}')][not(@data-translated)]"))

                # 如果任一元素存在，就插入翻译内容
                target_div = text_content_div or text_content_div2

                if target_div:
                    # 标记已翻译的元素，以避免重复
                    target_div.run_js("this.setAttribute('data-translated', 'true');")
                    
                    # 运行 JavaScript 以在最后一个翻译段落之后插入新翻译
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
                        transDiv.innerHTML = '<p style="color: purple;">{translated_text}</p>';
                        
                        // 将新翻译插入到目标原文元素之后
                        insertAfter(transDiv, this);
                    """)
                else:
                    print("未能找到任何元素")


    # 返回处理后的HTML内容
    return str(soup)

# 测试
url = 'https://web.telegram.org/a/#-1001000219802'
processed_html = process_webpage(url)


