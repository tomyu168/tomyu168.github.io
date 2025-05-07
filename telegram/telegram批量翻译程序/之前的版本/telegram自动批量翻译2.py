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
    return text and not re.search(r'[\u4e00-\u9fff]', text) and 'http' not in text

# 执行翻译并返回结果
def translate_text(text):
    tab.get('https://translate.volcengine.com/?category=&home_language=zh&source_language=detect&target_language=zh&text=')
    time.sleep(2)  
    language1 = (By.XPATH, "//div[@class='sc-ipEyDJ dqurTv']/div[@class='lang' and text()='英语']")
    language_list = tab.ele(language1)
    language_list.click()
    time.sleep(1) 
    language2 = (By.XPATH, "//div[@class='lang-search-recently']/div[@data-lang='zh']")
    language_option = tab.ele(language2)
    language_option.click()
    time.sleep(1) 
    input1 = (By.XPATH, '//div[@role="textbox" and @aria-multiline="true" and contains(@class, "slate-editor")]')
    input_box = tab.ele(input1)
    input_box.input(text)
    time.sleep(2)
    result1 = (By.XPATH, "//div[@class='slate-editor' and @contenteditable='false']")
    translated_text = tab.ele(result1).text
    time.sleep(2)
    return translated_text

# 处理网页内容
def process_webpage(url):
    tab.get(url)
    time.sleep(3)  # 等待页面加载
    menu1 = (By.XPATH, '//a[@href="#-1002463734187"]')
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

    # 遍历每条消息内容并进行翻译
    for div in soup.find_all('div', class_='message-content-wrapper can-select-text'):
        for text_content in div.find_all(text=True):
            stripped_text = text_content.strip()  # 去除两端空格
            if is_non_chinese_and_non_link(stripped_text):
                parent_element = text_content.parent

                translated_text = translate_text(stripped_text)

                # 重新获取网页
                tab.get(url)
                time.sleep(3)  # 等待页面加载完成
                menu_list = tab.ele(menu1)  # 重新获取元素
                menu_list.click()
                time.sleep(2)

                save_script = f"""
                var originalText = "{stripped_text}";
                var translatedText = "<p style='color: purple;'>{translated_text}</p>";
                localStorage.setItem(originalText, translatedText);
                """
                tab.run_js(save_script)

                # 在 parent_element 后插入翻译内容
                # 获取 text_content_div 和 text_content_div2
                text_content_div = tab.ele((By.XPATH, f"//div[contains(@class, 'text-content') and contains(@class, 'clearfix') and contains(., '{stripped_text}')]"))
                text_content_div2 = tab.ele((By.XPATH, f"//div[contains(@class, 'WebPage-text') and contains(., '{stripped_text}')]"))
                print("translated_text为" + translated_text)
                # 如果任一元素存在，就插入翻译内容
                if text_content_div or text_content_div2:
                    target_div = text_content_div if text_content_div else text_content_div2  # 选择存在的元素
                    # 运行 JavaScript 以在目标元素后插入翻译内容
                    target_div.run_js(f"""
                        var transDiv = document.createElement('div');
                        transDiv.className = 'translated_text';
                        transDiv.innerHTML = '<p style="color: purple;">{translated_text}</p>';
                        this.parentNode.insertBefore(transDiv, this.nextSibling);
                    """)
                else:
                    print("未能找到任何元素")

                time.sleep(1)

    load_script = """
    Object.keys(localStorage).forEach(function(key) {
        var originalText = key;
        var translatedText = localStorage.getItem(key);
        
        // 查找 class 为 'text-content' 的元素
        var element1 = document.evaluate("//div[contains(@class, 'text-content') and contains(., '" + originalText + "')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (element1) {
            var transDiv = document.createElement('div');
            transDiv.className = 'translated_text';
            transDiv.innerHTML = translatedText;
            element1.parentNode.insertBefore(transDiv, element1.nextSibling);
        }

        // 查找 class 为 'WebPage-text' 的元素
        var element2 = document.evaluate("//div[contains(@class, 'WebPage-text') and contains(., '" + originalText + "')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (element2) {
            var transDiv2 = document.createElement('div');
            transDiv2.className = 'translated_text';
            transDiv2.innerHTML = translatedText;
            element2.parentNode.insertBefore(transDiv2, element2.nextSibling);
        }
    });
    """
    tab.run_js(load_script)


    # 返回处理后的HTML内容
    return str(soup)

# 测试
url = 'https://web.telegram.org/a/#-1002463734187'
processed_html = process_webpage(url)
