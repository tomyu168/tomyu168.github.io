from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import By
import time
import re
import os

# 设置Chromium选项
do1 = ChromiumOptions().set_paths(local_port=9111, user_data_path=r'C:/Users/A/AppData/Local/Google/Chrome/User Data')
tab = ChromiumPage(addr_or_opts=do1)

compress_tab = tab.get_tab(url='freeconvert.com')
folder_path = "D:/hexoblog/source/telegram"
size_limit_mb = 25
# 遍历文件夹并找到符合条件的文件
selected_files = []
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    # 检查是否为 MP4 文件且大于指定大小
    if filename.endswith(".mp4") and os.path.getsize(file_path) > size_limit_mb * 1024 * 1024:
        selected_files.append(file_path)

for file_path in selected_files:
    uploadbutton = compress_tab("#upload-file-button")
    uploadbutton.click.to_upload(file_path)  # 直接设置文件路径
    time.sleep(1)
    print(f"Selected and uploaded file: {file_path}")
else:
    print("No file found meeting the size criteria.")


AdvancedSettingsButton = compress_tab(".file-list-item__settings")
AdvancedSettingsButton.click()
time.sleep(1)
selectxpath = (By.XPATH, "//div[@class='dialog__content']//div[@class='col-md-9']//div[@class='form-control']//select[@name='compress_video']")
select = compress_tab.ele(selectxpath)
select.click()
time.sleep(1)
optionxpath = (By.XPATH, "//div[@class='form-control']//option[@value='602a9f6c86eb7a0023f187be']")
option = compress_tab.ele(optionxpath)
time.sleep(1)
option.click()


inputVideoSize = compress_tab('#602becb798c6e90023d064b3')
inputVideoSize.input('25')

applySettingsxpath = (By.XPATH, "//div[@class='dialog__content']//div[@id='Dropdown']//div[@data-automation-id='toggle_icon_preset_dropdown']")
applySettings = compress_tab.ele(applySettingsxpath)
applySettings.hover()
button_apply_to_allxpath = (By.XPATH, "//div[@class='dialog__content']//button[@data-automation-id='dropdown_apply_to_all']")
button_apply_to_all = compress_tab.ele(button_apply_to_allxpath)
print(button_apply_to_all)
button_apply_to_all.click()
time.sleep(1)
button_Compress_Nowxpath = (By.XPATH, "//button[@data-automation-id='FileInputDropdownFileConvert']")
button_Compress_Now = compress_tab.ele(button_Compress_Nowxpath)
button_Compress_Now.click()

download_button_Nowxpath = (By.XPATH, "//button[@data-automation-id='downloadAllDropdown']")
download_button = compress_tab.ele(download_button_Nowxpath)
compress_tab.wait.ele_displayed(download_button)

compress_tab.set.download_path(r'D:\hexoblog\source\telegram')
download_button.click()
