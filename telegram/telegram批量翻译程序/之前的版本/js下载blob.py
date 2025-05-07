import time
import json
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import By
import requests

do1 = ChromiumOptions().set_paths(local_port=9111, user_data_path=r'C:/Users/A/AppData/Local/Google/Chrome/User Data')
tab = ChromiumPage(addr_or_opts=do1)
tab.get('https://web.telegram.org/a/#-1001036240821')
time.sleep(5)


# 你要下载的 Blob URL
blob_url = "blob:https://web.telegram.org/de4e101c-4dde-4eb4-a161-cea8970e79e1"

# 使用 JavaScript 获取 Blob 数据并转换为可下载的 URL
result = tab.run_js(f"""
    return fetch('{blob_url}')
        .then(response => response.blob())
        .then(blob => {{
            return {{
                url: URL.createObjectURL(blob),
                type: blob.type  // 获取 Blob 的 MIME 类型
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
file_name = blob_url.split('/')[-1] + file_extension  # 使用适当的扩展名

# 打印下载链接
print("Download URL:", download_url)


# 注意：由于 Blob URL 只在浏览器中有效，这里使用 requests 直接请求 Blob URL 是行不通的
# 我们需要使用 JavaScript 进行转换并在浏览器中下载
# 这里我们直接执行 JavaScript 进行下载
tab.run_js(f"""
    var link = document.createElement('a');
    link.href = '{download_url}';
    link.download = '{file_name}';  // 使用提取的文件名
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
""")

# 等待下载完成
time.sleep(5)


