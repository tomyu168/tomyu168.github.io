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
import ddddocr

# 设置Chromium选项
do1 = ChromiumOptions().set_paths(local_port=9111, user_data_path=r'C:/Users/A/AppData/Local/Google/Chrome/User Data')
tab = ChromiumPage(addr_or_opts=do1)

translate_tab = tab.get_tab(url='volcengine.com')
iframe = translate_tab('t:iframe')

# 获取滑块的移动轨迹
def get_tracks(distance):
    """
    根据偏移量获取移动轨迹
    :param distance: 偏移量
    :return: 移动轨迹
    """
    # 移动轨迹
    tracks = []
    # 减速阈值
    mid = distance * 4 / 5

    for i in range(5):
        tracks.append(mid / 5)
    for j in range(2):
        tracks.append(distance / 5 / 2)

    return tracks

def move_to_gap(tab, slider, tracks):
    """
    拖动滑块
    :param slider: 滑块
    :param tracks: 轨迹
    :return:
    """
    # 模拟滑动滑块
    translate_tab.actions.hold(slider)
    for i in tracks:
        translate_tab.actions.move(offset_x=i, offset_y=0)
    time.sleep(0.5)
    translate_tab.actions.release()

# 如果验证码容器存在
verifyContainer = translate_tab.ele('#captcha_container')
if verifyContainer:
    # 下载背景图和滑块图

    background_url = iframe.ele('.captcha-verify-image').attr('src')
    slider_url = iframe.ele('.captcha-verify-image-slide').attr('src')

    background_response = requests.get(background_url)
    slider_response = requests.get(slider_url)

    # 获取图像字节数据
    background_bytes = background_response.content
    slider_bytes = slider_response.content

    # 初始化 DdddOcr
    det = ddddocr.DdddOcr(det=False, ocr=False)

    # 使用滑块和背景图进行匹配
    res = det.slide_match(slider_bytes, background_bytes)

    # 输出结果
    distance = res["target"][0] - 10
    tracks = get_tracks(distance)
    print(tracks)
    time.sleep(2)
    
    slider_button = translate_tab.ele('.dragger-item')
    
    # 移动滑块
    move_to_gap(translate_tab, slider_button, tracks)
    time.sleep(2)
