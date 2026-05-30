# 第4章：Unicode 文本和字节序列

> **核心思想**：文本给人类阅读，字节序列供计算机处理。Python 3 明确区分了人类可读的文本字符串（`str`）和原始的字节序列（`bytes`/`bytearray`），把字节序列隐式转换成 Unicode 文本已成过去。

---

## 目录

1. [知识框架总览](#1-知识框架总览)
2. [字符、码点和编码](#2-字符码点和编码)
3. [字节序列类型：bytes 和 bytearray](#3-字节序列类型bytes-和-bytearray)
4. [基本的编码解码器](#4-基本的编码解码器)
5. [处理编码和解码问题](#5-处理编码和解码问题)
6. [处理文本文件：Unicode 三明治](#6-处理文本文件unicode-三明治)
7. [Unicode 规范化](#7-unicode-规范化)
8. [Unicode 文本排序](#8-unicode-文本排序)
9. [Unicode 数据库](#9-unicode-数据库)
10. [支持 str 和 bytes 的双模式 API](#10-支持-str-和-bytes-的双模式-api)
11. [常见误区与陷阱](#11-常见误区与陷阱)

---

## 1. 知识框架总览

```
第4章 Unicode 文本和字节序列
│
├── 基础概念
│   ├── 码点（U+XXXX）：字符的标识（整数）
│   ├── 编码：码点 → 字节序列（str.encode）
│   └── 解码：字节序列 → 码点（bytes.decode）
│
├── 字节类型
│   ├── bytes      → 不可变（Python 3）
│   ├── bytearray  → 可变
│   └── 项是 0~255 的整数，切片仍是字节序列
│
├── 常用编码
│   ├── utf-8      → Web 主流（97% 网站），变长，向后兼容 ASCII
│   ├── utf-16     → 带 BOM 字节序标记
│   ├── latin1     → 其他编码的基础
│   └── gb2312     → 简体中文
│
├── 编码/解码错误处理
│   ├── UnicodeEncodeError  → str → bytes 时出错
│   ├── UnicodeDecodeError  → bytes → str 时出错
│   └── errors='ignore'/'replace'/'xmlcharrefreplace'
│
├── 最佳实践：Unicode 三明治
│   ├── 输入尽早解码（bytes → str）
│   ├── 程序内只处理 str
│   └── 输出尽晚编码（str → bytes）
│
├── Unicode 规范化
│   ├── NFC：最少码点（推荐）
│   ├── NFD：分解合成字符
│   ├── NFKC/NFKD：兼容等价（有损，用于搜索）
│   └── casefold()：大小写同一化
│
├── 排序
│   ├── locale.strxfrm()：区域敏感排序
│   └── pyuca 库：Unicode 排序算法（推荐）
│
└── 双模式 API
    ├── str 参数 → 匹配 Unicode
    └── bytes 参数 → 只匹配 ASCII
```

---

## 2. 字符、码点和编码

```python
# =============================================
# 核心概念：码点 vs 字节
# =============================================

# 码点（code point）：字符的整数标识
# - 格式：U+XXXX（4~6 位十六进制）
# - 范围：U+0000 ~ U+10FFFF
# - 示例：字母 A = U+0041，欧元符号 € = U+20AC

# 编码（encoding）：码点 → 字节序列的算法
# 解码（decoding）：字节序列 → 码点的算法

s = 'café'
print(len(s))          # 4（4 个 Unicode 字符）

# 编码：str → bytes（需要指定编码）
b = s.encode('utf8')
print(b)               # b'caf\xc3\xa9'（5 个字节，é 用 2 字节）
print(len(b))          # 5

# 解码：bytes → str（需要指定相同的编码）
print(b.decode('utf8'))  # 'café'

# ⚠️ 记忆技巧：
# - 字节序列 → 人类可读文本 = 解码（decode）
# - 文本 → 字节序列（存储/传输）= 编码（encode）
```

---

## 3. 字节序列类型：`bytes` 和 `bytearray`

```python
# =============================================
# bytes：不可变字节序列（Python 3 新增）
# bytearray：可变字节序列（Python 2.6+）
# =============================================

# 创建 bytes 对象
cafe = bytes('café', encoding='utf_8')   # 从字符串创建
print(cafe)        # b'caf\xc3\xa9'

# 项是 0~255 的整数
print(cafe[0])     # 99（整数，不是字符！）
print(cafe[:1])    # b'c'（切片是 bytes 对象）

# 创建 bytearray（可变）
cafe_arr = bytearray(cafe)
print(cafe_arr)    # bytearray(b'caf\xc3\xa9')
cafe_arr[-1] = 0x41  # 可以修改
print(cafe_arr)    # bytearray(b'caf\xc3A')

# 字节的 4 种显示方式：
# 1. 可打印 ASCII 字符（32~126）直接显示
# 2. 转义序列：\t, \n, \r, \\
# 3. 十六进制转义：\xNN（其他字节值）
print(bytes([0, 65, 9, 127, 128]))
# b'\x00A\t\x7f\x80'（0=\x00, 65=A, 9=\t, 127=\x7f, 128=\x80）

# ---- 有用的类方法 ----
# fromhex：从十六进制字符串构建字节序列
print(bytes.fromhex('31 4B CE A9'))  # b'1K\xce\xa9'

# 从数组构建（底层操作）
import array
numbers = array.array('h', [-2, -1, 0, 1, 2])  # 短整数数组
octets = bytes(numbers)   # 直接获取内存字节
print(octets)
# b'\xfe\xff\xff\xff\x00\x00\x01\x00\x02\x00'（10 字节，5 个 16 位整数）
```

---

## 4. 基本的编码解码器

```python
# =============================================
# Python 内置 100+ 种编码解码器
# 常用别名：'utf_8' = 'utf8' = 'utf-8' = 'U8'
# =============================================

# 常见编码对比
text = 'El Niño'
for codec in ['latin_1', 'utf_8', 'utf_16']:
    encoded = text.encode(codec)
    print(f'{codec:8}: {encoded}')

# 输出：
# latin_1 : b'El Ni\xf1o'
# utf_8   : b'El Ni\xc3\xb1o'
# utf_16  : b'\xff\xfeE\x00l\x00 \x00N\x00i\x00\xf1\x00o\x00'
```

**主要编码解码器**：

| 编码 | 说明 | 适用场景 |
|------|------|---------|
| `latin1`（iso8859_1）| 其他编码的基础，每字节一字符 | 西欧语言遗留系统 |
| `cp1252` | latin1 的 Microsoft 超集，含弯引号 € 等 | Windows 应用 |
| `utf-8` | 变长 1~4 字节，向后兼容 ASCII | Web（97% 网站）|
| `utf-16le` | 固定 2 字节（BMP 字符），大于 U+FFFF 用代理对 | Windows 内部 |
| `gb2312` | 简体中文 | 中文遗留系统 |

---

## 5. 处理编码和解码问题

### 5.1 处理 `UnicodeEncodeError`

```python
city = 'São Paulo'

# UTF 编码可处理所有 Unicode 字符
print(city.encode('utf_8'))    # b'S\xc3\xa3o Paulo'
print(city.encode('utf_16'))   # b'\xff\xfeS\x00\xe3\x00...'

# iso8859_1 可处理（字符在其范围内）
print(city.encode('iso8859_1'))  # b'S\xe3o Paulo'

# cp437 不能处理 'ã'，默认抛出 UnicodeEncodeError
try:
    city.encode('cp437')
except UnicodeEncodeError as e:
    print(e)  # 'charmap' codec can't encode character '\xe3'...

# 错误处理策略：
city.encode('cp437', errors='ignore')           # b'So Paulo'（静默丢失字符）
city.encode('cp437', errors='replace')          # b'S?o Paulo'（替换为 ?）
city.encode('cp437', errors='xmlcharrefreplace')  # b'S&#227;o Paulo'（XML 实体）

# ✅ 安全检查：如果全是 ASCII，可以用任何编码
print('hello'.isascii())  # True（Python 3.7+）
```

### 5.2 处理 `UnicodeDecodeError`

```python
# 字节序列 b'Montr\xe9al'（latin1 编码的 'Montréal'）
octets = b'Montr\xe9al'

# 使用兼容编码解码正常
print(octets.decode('cp1252'))    # 'Montréal'（cp1252 是 latin1 超集）
print(octets.decode('iso8859_7')) # 'Montrιal'（希腊字母 ι，错误解码！）

# 用 utf-8 解码会抛出 UnicodeDecodeError
try:
    octets.decode('utf_8')
except UnicodeDecodeError as e:
    print(e)  # 'utf-8' can't decode byte 0xe9...

# 使用 replace 错误策略（不抛出异常，用 U+FFFD 替换）
print(octets.decode('utf_8', errors='replace'))  # 'Montr\ufffdal'（含替换字符）
```

### 5.3 BOM：字节序标记

```python
# UTF-16 编码会自动添加 BOM（字节序标记）
u16 = 'El Niño'.encode('utf_16')
print(u16[:2])     # b'\xff\xfe'（BOM，表示小端序）

# 小端序：低有效字节在前
print(list(u16))   # [255, 254, 69, 0, 108, 0, ...]（E=0x45=69）

# 明确指定字节序时不生成 BOM
u16le = 'El Niño'.encode('utf_16le')
u16be = 'El Niño'.encode('utf_16be')

# UTF-8 无须 BOM，但某些 Windows 工具会添加（UTF-8-SIG 编码）
# b'\xef\xbb\xbf' 是 UTF-8 BOM 的三字节表示
```

---

## 6. 处理文本文件：Unicode 三明治

```python
# =============================================
# 最佳实践：Unicode 三明治
# ① 输入：尽早解码（bytes → str）
# ② 处理：只用 str
# ③ 输出：尽晚编码（str → bytes）
# =============================================

# ---- 最佳做法 ----
# 写入时明确指定编码
with open('cafe.txt', 'w', encoding='utf_8') as fp:
    fp.write('café')   # 写入 4 个 Unicode 字符（占 5 字节）

# 读取时明确指定相同的编码
with open('cafe.txt', encoding='utf_8') as fp:
    print(fp.read())   # 'café'✅

# ❌ 错误：写入用 UTF-8，读取用系统默认编码（Windows 可能是 cp1252）
with open('cafe.txt', 'w', encoding='utf_8') as fp:
    fp.write('café')

with open('cafe.txt') as fp:      # 没有指定 encoding！
    print(fp.read())               # 'cafÃ©'（在 Windows 上）❌
```

### 6.1 了解系统默认编码

```python
import locale, sys

# 最重要的默认编码设置（打开文本文件的默认编码）
print(locale.getpreferredencoding())   # Linux/Mac: 'UTF-8', Windows: 'cp1252'

# 标准流编码（终端输出）
print(sys.stdout.encoding)            # 'utf-8'（Python 3.6+）
print(sys.getdefaultencoding())        # 'utf-8'（内部默认）
print(sys.getfilesystemencoding())     # 'utf-8'（Linux/Mac）

# ⚠️ Windows 可能有多种不同的编码设置，互不兼容
# 结论：始终显式指定 encoding= 参数，不要依赖默认值
```

---

## 7. Unicode 规范化

### 7.1 规范化的必要性

```python
# 'café' 可以用 4 个或 5 个码点表示，但看起来一样！
s1 = 'café'                         # 4 个码点
s2 = 'cafe\N{COMBINING ACUTE ACCENT}'  # 5 个码点（e + 组合重音符）

print(s1 == s2)    # False！（Python 看到不同的码点序列）
print(len(s1), len(s2))  # 4 5
```

### 7.2 四种规范化形式

```python
from unicodedata import normalize

s1 = 'café'
s2 = 'cafe\N{COMBINING ACUTE ACCENT}'

# NFC（推荐）：使用最少的码点（合成字符）
print(normalize('NFC', s1) == normalize('NFC', s2))   # True ✅
print(len(normalize('NFC', s1)))                        # 4

# NFD：分解合成字符（基字符 + 组合记号）
print(normalize('NFD', s1) == normalize('NFD', s2))   # True ✅
print(len(normalize('NFD', s1)))                        # 5

# NFKC/NFKD：兼容等价（有损！用于搜索，不用于持久存储）
half = '½'                        # VULGAR FRACTION ONE HALF
print(normalize('NFKC', half))   # '1⁄2'（转换后含 FRACTION SLASH）

four_sq = '4²'
print(normalize('NFKC', four_sq))  # '42'（改变了原意！）

# ⚠️ NFKC/NFKD 可能会损失信息，仅用于搜索和索引
```

### 7.3 实用规范化函数

```python
from unicodedata import normalize

def nfc_equal(str1, str2):
    """NFC 规范化后比较（等价字符视为相等）。"""
    return normalize('NFC', str1) == normalize('NFC', str2)

def fold_equal(str1, str2):
    """NFC + 大小写同一化后比较（不区分大小写）。"""
    return (normalize('NFC', str1).casefold() ==
            normalize('NFC', str2).casefold())


s1 = 'café'
s2 = 'cafe\u0301'    # café 的 NFD 形式

print(nfc_equal(s1, s2))    # True（NFC 标准等价）
print(fold_equal('A', 'a')) # True（大小写不敏感）

# casefold()：大小写同一化（比 lower() 更彻底）
# - 'µ'（MICRO SIGN）→ 'μ'（GREEK SMALL LETTER MU）
# - 'ß'（德语 Eszett）→ 'ss'
print('ß'.casefold())    # 'ss'
print('μ'.casefold())    # 'μ'（转为标准希腊字母）
```

### 7.4 去掉变音符（极端规范化）

```python
import unicodedata, string

def shave_marks(txt):
    """删除所有变音符（重音符、下加符等）。"""
    norm_txt = unicodedata.normalize('NFD', txt)     # 分解为基字符 + 组合记号
    shaved = ''.join(c for c in norm_txt
                     if not unicodedata.combining(c))  # 过滤组合记号
    return unicodedata.normalize('NFC', shaved)        # 重组


order = '"Herr Voß: caffè latte • bowl of açaí."'
print(shave_marks(order))
# '"Herr Voß: caffe latte • bowl of acai."'（去掉了 è 和 ç 的变音符）
```

---

## 8. Unicode 文本排序

```python
# Python 默认按码点排序，对非 ASCII 字符结果不理想
fruits = ['caju', 'atemoia', 'cajá', 'açaí', 'acerola']
print(sorted(fruits))
# ['acerola', 'atemoia', 'açaí', 'caju', 'cajá']  ← 葡萄牙语顺序错误

# ---- 方法一：locale.strxfrm（依赖区域设置）----
import locale
locale.setlocale(locale.LC_COLLATE, 'pt_BR.UTF-8')  # 需要操作系统支持
sorted_fruits = sorted(fruits, key=locale.strxfrm)
print(sorted_fruits)
# ['açaí', 'acerola', 'atemoia', 'cajá', 'caju']  ✅ 正确顺序

# ---- 方法二：pyuca 库（推荐，跨平台）----
import pyuca                     # pip install pyuca
coll = pyuca.Collator()
sorted_fruits = sorted(fruits, key=coll.sort_key)
print(sorted_fruits)
# ['açaí', 'acerola', 'atemoia', 'cajá', 'caju']  ✅ 正确顺序
```

---

## 9. Unicode 数据库

```python
import unicodedata

# ---- 常用函数 ----

# name()：获取字符的官方名称
print(unicodedata.name('A'))        # 'LATIN CAPITAL LETTER A'
print(unicodedata.name('€'))        # 'EURO SIGN'
print(unicodedata.name('Ω'))        # 'GREEK CAPITAL LETTER OMEGA'

# category()：获取字符的类别（两字母代码）
print(unicodedata.category('A'))    # 'Lu'（大写字母）
print(unicodedata.category('a'))    # 'Ll'（小写字母）
print(unicodedata.category('1'))    # 'Nd'（十进制数字）
print(unicodedata.category(' '))    # 'Zs'（空格分隔符）

# numeric()：获取字符的数值
print(unicodedata.numeric('½'))     # 0.5
print(unicodedata.numeric('③'))    # 3.0

# combining()：检查是否是组合记号
print(unicodedata.combining('\u0301'))  # 230（重音符，非零=是组合记号）
print(unicodedata.combining('A'))       # 0（不是组合记号）

# ---- 按名称查找字符（实用脚本）----
import sys

def find(*query_words, start=ord(' '), end=sys.maxunicode + 1):
    """按名称搜索 Unicode 字符。"""
    query = {w.upper() for w in query_words}
    for code in range(start, end):
        char = chr(code)
        name = unicodedata.name(char, None)
        if name and query.issubset(name.split()):
            print(f'U+{code:04X}\t{char}\t{name}')

# find('SIGN', 'EURO')   → U+20AC  €  EURO SIGN
# find('CAT', 'FACE')    → 所有猫脸表情符号
```

---

## 10. 支持 `str` 和 `bytes` 的双模式 API

```python
import re

# ---- str 模式：匹配 Unicode 字符 ----
re_numbers_str = re.compile(r'\d+')   # str 正则
re_words_str   = re.compile(r'\w+')   # str 正则

# ---- bytes 模式：只匹配 ASCII ----
re_numbers_bytes = re.compile(rb'\d+')  # bytes 正则
re_words_bytes   = re.compile(rb'\w+')  # bytes 正则

text_str = "Ramanujan saw \u0be7\u0bed\u0be8\u0bef as 1729."
text_bytes = text_str.encode('utf_8')

print('str  数字:', re_numbers_str.findall(text_str))
# ['੧੭੨੯', '1729']（包含泰米尔数字！）
print('bytes数字:', re_numbers_bytes.findall(text_bytes))
# [b'1729']（只有 ASCII 数字）

print('str  单词:', re_words_str.findall(text_str))
# ['Ramanujan', 'saw', '੧੭੨੯', 'as', '1729']
print('bytes单词:', re_words_bytes.findall(text_bytes))
# [b'Ramanujan', b'saw', b'as', b'1729']（只有 ASCII 单词）

# ---- os 模块：str 和 bytes 文件名 ----
import os

os.listdir('.')    # 返回 str 文件名（自动解码）
os.listdir(b'.')   # 返回 bytes 文件名（不解码）

# 两个专用函数处理文件名编码
os.fsencode('filename.txt')  # str → bytes（用文件系统编码）
os.fsdecode(b'filename.txt') # bytes → str（用文件系统编码）
```

---

## 11. 常见误区与陷阱

### ❌ 误区一：不指定编码，依赖系统默认值

```python
# ❌ 危险：不同平台默认编码不同
with open('data.txt', 'w') as f:    # 没有 encoding=！
    f.write('中文内容')

with open('data.txt') as f:          # 没有 encoding=！
    print(f.read())                   # 可能乱码或报错

# ✅ 正确：始终显式指定编码
with open('data.txt', 'w', encoding='utf-8') as f:
    f.write('中文内容')

with open('data.txt', encoding='utf-8') as f:
    print(f.read())
```

### ❌ 误区二：混淆 `str` 和 `bytes`

```python
# ❌ Python 3 不允许隐式转换
# 'hello' + b'world'   → TypeError

# ✅ 必须明确编码/解码
'hello'.encode('utf-8') + b' world'   # b'hello world'
'hello' + b' world'.decode('utf-8')   # 'hello world'
```

### ❌ 误区三：以为 `bytes[0]` 返回字符

```python
b = b'hello'
print(b[0])     # 104（整数，不是字符！）
print(b[:1])    # b'h'（切片返回 bytes）

# 与 str 的区别：
s = 'hello'
print(s[0])     # 'h'（字符串）
print(s[:1])    # 'h'（仍是字符串）
```

### ❌ 误区四：用 NFKC/NFKD 持久化存储

```python
# ❌ NFKC 有损（改变原意）
print(normalize('NFKC', '4²'))   # '42'（上标 2 变成普通 2）
print(normalize('NFKC', '½'))    # '1⁄2'（分数拆分）

# ✅ 持久化存储用 NFC
# NFKC/NFKD 只用于搜索索引和文本匹配
```

### ❌ 误区五：不了解 BOM 的影响

```python
# Windows 记事本保存 UTF-8 文件时会添加 BOM
# 读取时需要用 'utf-8-sig' 编码自动去除 BOM
with open('from_notepad.txt', encoding='utf-8-sig') as f:
    content = f.read()    # 自动去除 BOM，无论是否存在

# 检测文件是否有 BOM
with open('file.txt', 'rb') as f:
    raw = f.read(3)
    if raw.startswith(b'\xef\xbb\xbf'):
        print('UTF-8 with BOM')
```

---

*整理自《流畅的Python（第2版）》第4章 | 知识点覆盖：4.2-4.10*
