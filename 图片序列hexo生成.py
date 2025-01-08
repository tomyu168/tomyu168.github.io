# 将生成的文本保存到文件中
with open("图片序列.txt", "w", encoding="utf-8") as file:
    for x in range(22, 32):  # 从1到83
        file.write(f"![2025-1-8-设计参考Carlyle和Deniot和Wearstler风格人工智能拓展-客厅]({x}.jpg)\n")