# 将生成的文本保存到文件中
with open("图片序列.txt", "w", encoding="utf-8") as file:
    for x in range(1, 31):  # 从1到83
        file.write(f"![2025-1-7-设计参考jordanCarlyle风格人工智能拓展]({x}.jpg)\n")