file_path = "your_file.txt"  # 设置文件路径

file = open(file_path, "a", encoding="utf-8")
file.truncate(0)

# 调用函数来写入内容到文件中
file.write("中文不能输入吗凭什么")

# 追加更多内容
file.write("Additional content\n")

# 可以再次调用 write_to_file() 函数来添加更多内容
