# 题目：反转字符串
# 用栈来实现字符串反转。比如输入 "hello"，输出 "olleh"。
def reverse_string(s):
    stack = []
    for char in s:
        stack.append(char)
    result = ""
    while stack:
        result += stack.pop()
    return result

print(reverse_string("hello"))
