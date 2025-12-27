
# 🎄 Grand Luxury Tree

[![Contributors](https://img.shields.io/github/contributors/electronicminer/gesture-Christmas_tree-3d_with_photo?color=dark-green)](https://github.com/electronicminer/gesture-Christmas_tree-3d_with_photo/graphs/contributors)

哈喽！这是一个为了庆祝圣诞节写的小项目。✨

原本只是想画一棵普通的 3D 圣诞树，但觉得不够酷，于是加上了 **手势识别** 和 **粒子特效**。现在你可以通过摄像头“隔空”控制这棵树，还能把自己喜欢的照片挂上去。

虽然只有几百行代码，但视觉效果拉满了（特别是在大屏幕上）。

点击下面的链接可以直接访问：支持全平台
https://electronicminer.github.io/gesture-Christmas_tree-3d_with_photo/christmas_tree_touch&gesture.html

<img width="2559" height="1439" alt="image" src="https://github.com/user-attachments/assets/45f3ec57-00b5-4989-b3b2-484772ad95cf" />


## 🤔 这是啥？(Intro)

这不是那种静态的网页贺卡。这是一棵由 **几千个粒子** 组成的动态树。
我接入了 Google 的 MediaPipe，所以它能看懂你的手势。

* **粒子特效**：树会呼吸、旋转，还能炸裂成满天星。
* **隔空控物**：不需要鼠标，对着摄像头挥挥手就能控制它（感觉像奇异博士）。
* **挂载回忆**：点右上角的按钮上传照片，它们会变成带金框的拍立得，飘在树周围。
* **极简审美**：只有黑金配色，没有花里胡哨的装饰，主打一个“高级感”。
<img width="2557" height="1291" alt="image" src="https://github.com/user-attachments/assets/d7d31b4c-bf4d-49b2-b922-79813bbddba5" />

<img width="2559" height="1294" alt="image" src="https://github.com/user-attachments/assets/d7e4e982-3042-449d-8898-105048aeac1d" />


## 🛠️ 用了什么 (Tech)

纯纯的前端魔法，没用复杂的框架：
* **Three.js** - 搞定 3D 渲染和粒子系统。
* **MediaPipe** - 搞定手势识别（这东西太强了）。
* **原生 JS (ES Modules)** - 手搓核心逻辑。

## 🎮 怎么玩？(Controls)

第一次玩建议把音响打开（虽然还没加背景音乐，但你可以自己放首 Jingle Bells 🎵）。

### 🖐️ 手势模式 (重点！)
确保浏览器允许使用摄像头，然后：
1.  **张开手掌 (🖐️)**：这就是“炸裂模式”！树会散开变成星云，你可以转动视角。
2.  **握紧拳头 (✊)**：收！粒子会重新聚合成圣诞树。
3.  **捏合手指 (🤏)**：就像在捏东西一样，它会随机抓取一张照片放大给你看。

### 🖱️ 鼠标党
* 左键拖拽旋转，滚轮缩放。
* **H 键**：按下可以隐藏所有 UI，用来截图或录屏当壁纸很棒。

## 🚀 跑起来 (How to Run)

⚠️ **注意：** 因为用到了 ES Modules 和摄像头权限，**千万不要直接双击 `index.html` 打开**，浏览器会报错（CORS 策略限制）。你得起一个本地服务器。

**如果你有 VS Code (推荐):**
装个 `Live Server` 插件，右键 `index.html` -> "Open with Live Server"。搞定。

**如果你是 Python 大佬:**
在目录下打开终端：
```bash
python -m http.server 8000
````

然后浏览器访问 `localhost:8000`。

**如果你习惯 Node.js:**

```bash
npx http-server .
```



**Merry Christmas\! 🎅**
如果你觉得这项目有点意思，欢迎 Star，或者 Fork 改成你喜欢的颜色！

新增移动端网页支持
## Contributors ✨

感谢所有为本项目做出贡献的开发者：

<a href="https://github.com/electronicminer/gesture-Christmas_tree-3d_with_photo/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=electronicminer/gesture-Christmas_tree-3d_with_photo" />
</a>

## 📊 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=electronicminer/gesture-Christmas_tree-3d_with_photo&type=Date)](https://star-history.com/#electronicminer/gesture-Christmas_tree-3d_with_photo&Date)
