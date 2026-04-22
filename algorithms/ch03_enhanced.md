# 第3章：基本数据结构

> **本章导读**：这是整本书中"最实用"的一章。你将学到的栈、队列、链表，是面试中频率最高的考点，也是后续学习树、图的底层基础。
>
> **学习路径**：生活类比建立直觉 → 抽象数据类型定义接口 → Python 实现 → 复杂度分析 → 经典面试题实战
>
> **核心问题**：同样是"存一组数据"，为什么不直接用列表？——因为不同场景下，对"在哪里存、从哪里取"有不同的约束，这些约束正是各种数据结构存在的意义。

---

## 3.0 关键术语速查

| 术语 | 英文 | 定义 |
|------|------|------|
| 线性结构 | Linear Structure | 元素之间存在一对一的前驱后继关系，像一条有序的链 |
| 抽象数据类型 | ADT (Abstract Data Type) | 只定义数据的逻辑结构和允许的操作，不涉及具体实现 |
| 栈 | Stack | 只能在一端（栈顶）进行插入和删除的线性结构，LIFO |
| 队列 | Queue | 在一端插入（队尾）、另一端删除（队头）的线性结构，FIFO |
| 双端队列 | Deque | 两端均可插入/删除的线性结构，是栈和队列的泛化 |
| 链表 | Linked List | 通过指针连接分散节点的线性结构，无需连续内存 |
| LIFO | Last In First Out | 后进先出，栈的核心规则 |
| FIFO | First In First Out | 先进先出，队列的核心规则 |
| 节点 | Node | 链表的基本单元，包含数据和指向下一节点的引用 |
| 头指针 | Head Pointer | 指向链表第一个节点的引用，是访问链表的唯一入口 |
| 压栈 | Push | 将元素放入栈顶 |
| 弹栈 | Pop | 从栈顶取出并返回元素 |
| 入队 | Enqueue | 将元素加入队尾 |
| 出队 | Dequeue | 从队头取出并返回元素 |

---

## 3.1 为什么需要这些数据结构？

### 从一个问题出发

假设你要写一个"撤销"功能（Ctrl+Z）：用户每做一步操作，你需要记录下来；用户撤销时，从**最近的一步**开始撤回。

**用普通列表能解决吗？** 当然可以，但有个问题：列表对"从哪里存、从哪里取"没有任何约束。你完全可能不小心从中间取数据，或者从头部取而不是末尾，引入 bug。

**更好的做法**：用一种**强制了访问规则**的结构——这就是**栈**（Stack）。它通过 ADT 的定义，从接口层面保证你只能从顶部存取，消灭了误操作的可能。

> **这就是 ADT 的本质意义**：不仅仅是存储数据，更是通过约束访问规则，让代码更可靠、更易推理。

### 四种线性结构的本质区别

所有线性结构都是"存一列数据"，区别只在于**访问规则**：

```
数组/列表：任意位置读写，最灵活，但约束最少
栈        ：只能从顶部存取，用于"最近的优先处理"
队列      ：尾进头出，用于"先来的优先处理"
链表      ：灵活插入删除，不需要连续内存
```

---

## 3.2 抽象数据类型（ADT）是什么？

### 定义

**ADT（Abstract Data Type，抽象数据类型）** 是对数据结构的**逻辑描述**，它定义：
1. 数据的**逻辑组织方式**（如"一列有顺序的元素"）
2. 允许执行的**操作**（如"只能从顶部取"）

**ADT 刻意不涉及实现细节**——同一个 ADT 可以有多种底层实现（用数组、链表、Python 列表……），使用者只需关心接口。

### 类比理解

```
ADT  ≈  插座标准（定义了接口：两孔/三孔，电压电流）
实现 ≈  不同厂商的插座（外观不同，内部结构不同，但都满足标准）
使用者 ≈  电器（只需要符合标准的插座，不在乎哪家生产的）
```

### ADT 与实现的关系

```
┌─────────────────────────────────────────────┐
│           Stack ADT（抽象层）                 │
│  push(item)  pop()  peek()  is_empty()       │
│  → 只定义"能做什么"，不管"怎么做"             │
└─────────────────────────────────────────────┘
              ↓ 可以有多种实现
┌──────────────────┐    ┌──────────────────────┐
│  用 Python 列表   │    │  用链表实现            │
│  _data.append()  │    │  Node + head 指针      │
│  _data.pop()     │    │  新节点插到链头         │
└──────────────────┘    └──────────────────────┘
   两种实现对外接口完全相同，使用代码无需改变
```

---

## 3.3 栈（Stack）

### 3.3.1 直觉建立：从生活类比到抽象

```
生活中的栈：
  ┌───┐
  │ C │  ← 最后放上去（Last In），最先被取走（First Out）
  ├───┤
  │ B │
  ├───┤
  │ A │  ← 最先放上去，被压在最底层
  └───┘
  餐盘叠放    浏览器历史    编辑器撤销    函数调用栈
```

**LIFO 的本质**：最近发生的事情，最先被处理/撤销。这个规律在计算机中无处不在。

### 3.3.2 栈的 ADT 定义

```
操作              说明                          复杂度
─────────────────────────────────────────────────────
Stack()           创建空栈                       O(1)
push(item)        将 item 压入栈顶               O(1)
pop()             从栈顶弹出并返回元素            O(1)
peek()            返回栈顶元素（不移除）           O(1)
is_empty()        若栈为空返回 True               O(1)
size()            返回栈中元素个数                O(1)
```

### 3.3.3 Python 实现（详细注释版）

```python
class Stack:
    """
    用 Python 列表实现栈
    
    ═══ 设计决策：为什么以列表末尾作为栈顶？═══
    
    方案A（本方案）：末尾 = 栈顶
        push → list.append()   时间复杂度 O(1) ✅
        pop  → list.pop()      时间复杂度 O(1) ✅
    
    方案B（错误示范）：头部 = 栈顶
        push → list.insert(0, item)  时间复杂度 O(n) ❌
        pop  → list.pop(0)           时间复杂度 O(n) ❌
        原因：头部插入/删除需要移动所有现有元素
    
    结论：永远让 append/pop（末尾操作）来实现栈，性能最优。
    """
    
    def __init__(self):
        self._data = []   # 下划线前缀表示"私有"，外部不应直接访问
                          # 列表末尾 = 栈顶，列表开头 = 栈底
    
    def push(self, item):
        """压栈：O(1)"""
        self._data.append(item)   # 追加到列表末尾，即栈顶
    
    def pop(self):
        """
        弹栈：O(1)
        注意：空栈弹出是错误操作，必须先判断
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._data.pop()   # 移除并返回列表末尾元素（栈顶）
    
    def peek(self):
        """
        查看栈顶：O(1)
        peek 与 pop 的区别：peek 不移除元素，只是"偷看一眼"
        """
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._data[-1]     # 负索引 -1 = 最后一个元素
    
    def is_empty(self):
        return len(self._data) == 0
    
    def size(self):
        return len(self._data)
    
    def __str__(self):
        """让 print(stack) 有可读的输出"""
        return str(self._data) + "  ← top"


# ══ 执行流程演示 ══
s = Stack()
print(s.is_empty())   # True，初始为空

s.push('A')           # 内部: ['A']        栈: A
s.push('B')           # 内部: ['A','B']    栈: A B(top)
s.push('C')           # 内部: ['A','B','C'] 栈: A B C(top)

print(s.peek())       # 'C'，只看不取
print(s.size())       # 3

print(s.pop())        # 'C'，弹出栈顶  内部变为: ['A','B']
print(s.pop())        # 'B'            内部变为: ['A']
print(s)              # ['A']  ← top
```

---

### 3.3.4 ⭐【面试高频】应用1：有效的括号匹配

#### 问题背景

给定一个只含括号的字符串，判断括号是否合法闭合。
- `"()[]{}"` → True
- `"([{}])"` → True
- `"([)]"` → False（交叉嵌套）
- `"((("` → False（左括号多余）

这是 **LeetCode 第20题**，栈的最经典面试题。

#### 为什么用栈？——从暴力到最优

**暴力思路**：反复扫描，每次找到一对相邻匹配括号就消除，直到不能消除为止。

```python
def check_brute_force(s):
    """
    暴力解法：反复替换，O(n²)
    缺点：每轮扫描 O(n)，最坏需要 n/2 轮，总复杂度 O(n²)
    """
    prev = None
    while s != prev:          # 只要还有变化就继续
        prev = s
        s = s.replace('()', '')  # 消除相邻括号对
        s = s.replace('[]', '')
        s = s.replace('{}', '')
    return s == ''

print(check_brute_force("([{}])"))   # True，但效率差
```

**为什么栈更好？**

关键洞察：当遇到右括号时，我们只需要知道**最近的一个未匹配的左括号**是什么。"最近的"= LIFO = 栈！

```
处理 "( [ { } ] )" 的过程：

字符  操作          栈的状态      说明
'('  push('(')     ['(']         左括号，入栈等待匹配
'['  push('[')     ['(','[']     左括号，入栈
'{'  push('{')     ['(','[','{'] 左括号，入栈
'}'  pop='{',匹配  ['(','[']     遇到右括号，弹出栈顶 '{' 恰好匹配
']'  pop='[',匹配  ['(']         弹出 '[' 匹配
')'  pop='(',匹配  []            弹出 '(' 匹配
结束  栈为空        []            ✅ 合法！
```

```python
def is_valid_brackets(s):
    """
    栈解法：O(n) 时间，O(n) 空间
    
    核心思想：
    左括号 → 压栈（等待被右括号匹配）
    右括号 → 弹出栈顶，检查是否是对应的左括号
    
    两个边界情况必须处理：
    1. 遇到右括号时栈已空（右括号多余）
    2. 处理完所有字符后栈不为空（左括号多余）
    """
    stack = Stack()
    
    # 用字典建立右括号→左括号的映射，查找 O(1)
    match = {')': '(', ']': '[', '}': '{'}
    
    for char in s:
        if char in '([{':             # 左括号：无条件压栈
            stack.push(char)
        elif char in ')]}':           # 右括号：检查匹配
            if stack.is_empty():      # 边界：栈空说明没有对应左括号
                return False          # 例如：")abc"
            top = stack.pop()         # 弹出最近的左括号
            if top != match[char]:    # 与期望不符，如 '(' 遇到 ']'
                return False
        # 其他字符（字母、数字等）直接忽略
    
    # 边界：栈必须为空，否则有多余的左括号
    return stack.is_empty()


# ══ 测试用例（逐一分析）══
print(is_valid_brackets("()[]{}"))   # True
print(is_valid_brackets("([{}])"))   # True
print(is_valid_brackets("([)]"))     # False ← 交叉：'(' 等配对时遇到 ']'
print(is_valid_brackets("{[]"))      # False ← 结束时栈非空：['{'残留
print(is_valid_brackets(")"))        # False ← 首字符就是右括号，栈空
```

> **⚠️ 面试注意点**：
> 1. 必须处理"栈空时遇到右括号"的边界，否则 `pop()` 会报错
> 2. 最后必须检查栈是否为空，`"((("` 这类情况容易遗漏
> 3. 时间复杂度 O(n)，因为每个字符只被处理一次（压栈或弹栈）

---

### 3.3.5 应用2：进制转换

#### 执行流程详解

以 `decimal=13, base=2` 为例，逐步跟踪：

```
13 ÷ 2 = 6 余 1  → 压入 '1'    栈: ['1']
 6 ÷ 2 = 3 余 0  → 压入 '0'    栈: ['1','0']
 3 ÷ 2 = 1 余 1  → 压入 '1'    栈: ['1','0','1']
 1 ÷ 2 = 0 余 1  → 压入 '1'    栈: ['1','0','1','1']
循环结束（decimal=0）

弹栈顺序（从栈顶到栈底）：1, 1, 0, 1
拼接结果：'1101'  ✅（13的二进制）

关键：除法得到的余数是从低位到高位，
      栈的 LIFO 特性自动完成了"反转"，得到正确的高位在前的表示
```

```python
def convert_base(decimal_num, base):
    """
    十进制转任意进制（2~16）
    
    时间复杂度：O(log_base(n))，因为每次除以 base，共需 log_base(n) 次
    空间复杂度：O(log_base(n))，栈存储每一位
    """
    # 16进制需要 A-F 来表示 10-15
    digits = "0123456789ABCDEF"
    
    s = Stack()
    
    if decimal_num == 0:     # 特殊情况：0的任何进制表示都是'0'
        return "0"
    
    while decimal_num > 0:
        remainder = decimal_num % base      # 取最低位（余数）
        s.push(digits[remainder])           # 压入对应字符
        decimal_num = decimal_num // base   # 去掉最低位，缩小问题
    
    # 此时栈顶 = 最高位，从栈顶依次弹出就是正确顺序
    result = ""
    while not s.is_empty():
        result += s.pop()
    
    return result

print(convert_base(13, 2))   # '1101'
print(convert_base(255, 16)) # 'FF'
print(convert_base(8, 8))    # '10'（8的八进制是10）
```

---

### 3.3.6 ⭐【面试常考】应用3：逆波兰表达式求值

#### 背景：什么是后缀表达式？

我们习惯写的是**中缀表达式**：`3 + 4 * 2`，需要括号和优先级规则。
计算机更容易处理**后缀表达式**（逆波兰）：`3 4 2 * +`，操作符在操作数后面，无需括号，顺序天然正确。

| 中缀 | 后缀（逆波兰） |
|------|--------------|
| `3 + 4` | `3 4 +` |
| `3 + 4 * 2` | `3 4 2 * +` |
| `(3 + 4) * 2` | `3 4 + 2 *` |

#### 后缀表达式求值（LeetCode 150题）

```python
def eval_rpn(tokens):
    """
    逆波兰表达式求值
    
    执行规则：
    - 遇到数字 → 压栈
    - 遇到运算符 → 弹出两个数字，计算后压回栈
    - 最终栈里剩一个数字，就是答案
    
    时间：O(n)，空间：O(n)
    """
    stack = Stack()
    operators = {'+', '-', '*', '/'}
    
    for token in tokens:
        if token not in operators:
            stack.push(int(token))    # 数字直接压栈
        else:
            # 弹出两个操作数
            # 注意顺序！先弹出的是右操作数
            b = stack.pop()    # 右操作数（后压入的）
            a = stack.pop()    # 左操作数（先压入的）
            
            if token == '+':
                stack.push(a + b)
            elif token == '-':
                stack.push(a - b)
            elif token == '*':
                stack.push(a * b)
            elif token == '/':
                # 注意：题目要求向零截断，不是向下取整
                stack.push(int(a / b))
    
    return stack.pop()   # 最终结果


# 执行流程演示：["2","1","+","3","*"]  → (2+1)*3 = 9
# token='2': 压入 2      栈: [2]
# token='1': 压入 1      栈: [2, 1]
# token='+': 弹出1,2     计算 2+1=3，压入3   栈: [3]
# token='3': 压入 3      栈: [3, 3]
# token='*': 弹出3,3     计算 3*3=9，压入9   栈: [9]
# 返回 9 ✅

print(eval_rpn(["2","1","+","3","*"]))   # 9
print(eval_rpn(["4","13","5","/","+"]))  # 6  → 4 + (13/5) = 4+2 = 6
```

> **⚠️ 易错点**：弹出顺序！`b = pop()` 先弹，`a = pop()` 后弹。
> 对于减法和除法，`a - b` 和 `b - a` 结果完全不同，一定要搞清楚先后顺序。

---

## 3.4 队列（Queue）

### 3.4.1 直觉建立

```
队列 = 排队
新来的人从队尾加入，从队头离开，先来先服务（FIFO）

    入队方向                    出队方向
    ────────────────────────────────────▶
加入 → [E] [D] [C] [B] [A] → 离开
       队尾                   队头

现实类比：超市收银台、打印机任务队列、客服系统排队
```

### 3.4.2 队列 ADT 定义

```
操作               说明                        复杂度
────────────────────────────────────────────────────
Queue()            创建空队列                   O(1)
enqueue(item)      将 item 加入队尾             O(1)
dequeue()          从队头移除并返回元素          O(1)*
is_empty()         若队列为空返回 True           O(1)
size()             返回队列中元素个数            O(1)

* 用 Python 列表实现时 dequeue 是 O(n)，
  用 collections.deque 实现则是真正的 O(1)
```

### 3.4.3 两种实现方案对比

```python
# ═══ 方案一：用 Python 列表（教学用，有性能缺陷）═══
class Queue_List:
    """
    列表实现队列
    
    enqueue：列表末尾 append()   → O(1) ✅
    dequeue：列表头部 pop(0)     → O(n) ❌
    
    pop(0) 为什么是 O(n)？
    因为列表在内存中是连续存储的，删除第0个元素后，
    后面所有元素都需要向前移动一位，移动次数 = 元素个数 = O(n)
    """
    def __init__(self):
        self._data = []
    
    def enqueue(self, item):
        self._data.append(item)   # O(1)，加到末尾（队尾）
    
    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._data.pop(0)  # O(n)，从头部移除（队头）
    
    def is_empty(self):
        return len(self._data) == 0
    
    def size(self):
        return len(self._data)


# ═══ 方案二：用 collections.deque（生产推荐）═══
from collections import deque as _deque

class Queue:
    """
    deque 实现队列：两端操作都是 O(1)
    
    Python 的 collections.deque 底层是双向链表，
    appendleft/popleft 和 append/pop 都是 O(1)
    """
    def __init__(self):
        self._data = _deque()
    
    def enqueue(self, item):
        self._data.append(item)      # 加到右端（队尾），O(1)
    
    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._data.popleft()  # 从左端取（队头），O(1) ✅
    
    def is_empty(self):
        return len(self._data) == 0
    
    def size(self):
        return len(self._data)
```

### 3.4.4 应用：热土豆问题（约瑟夫问题变体）

#### 问题描述
n 个人围成一圈，从第1人开始报数，每数到第 k 个人就淘汰，淘汰后从下一人重新报数，最后剩下的人获胜。

#### 用队列模拟圆圈的巧妙之处

```
5人，k=3 的过程：
初始队列：[Alice, Bob, Carol, Dave, Eve]  ← Alice 在队头

第1轮：传土豆2次（k-1次）：
  Alice 出队→入队尾   [Bob, Carol, Dave, Eve, Alice]
  Bob   出队→入队尾   [Carol, Dave, Eve, Alice, Bob]
  Carol 出队，淘汰！  [Dave, Eve, Alice, Bob]

第2轮：传土豆2次：
  Dave  出队→入队尾   [Eve, Alice, Bob, Dave]
  Eve   出队→入队尾   [Alice, Bob, Dave, Eve]
  Alice 出队，淘汰！  [Bob, Dave, Eve]

... 以此类推，队列长度 = 1 时结束
```

```python
def hot_potato(names, num):
    """
    热土豆模拟（约瑟夫问题）
    
    思路：用队列模拟圆圈
    "传土豆" = dequeue（队头出）+ enqueue（再入队尾）
    "淘汰"  = dequeue（出队不再入队）
    
    时间：O(n * k)，每轮 O(k) 操作，共 n-1 轮淘汰
    """
    q = Queue()
    for name in names:
        q.enqueue(name)    # 按顺序入队，第一个人在队头
    
    while q.size() > 1:    # 队列长度 > 1 时继续游戏
        
        # 传土豆 num-1 次（把队头移到队尾，模拟"数数但未到k"）
        for _ in range(num - 1):
            q.enqueue(q.dequeue())   # 队头出，加到队尾
        
        # 数到第 num 个人，淘汰（出队但不再入队）
        out = q.dequeue()
        print(f"淘汰：{out}，剩余：{q.size()} 人")
    
    return q.dequeue()   # 最后一人

winner = hot_potato(["Alice", "Bob", "Carol", "Dave", "Eve"], 3)
print(f"最终获胜：{winner}")
# 淘汰：Carol，剩余：4 人
# 淘汰：Alice，剩余：3 人
# 淘汰：Eve，  剩余：2 人
# 淘汰：Bob，  剩余：1 人
# 最终获胜：Dave
```

---

## 3.5 双端队列（Deque）

### 定义与特点

双端队列（Double-ended Queue，Deque）是栈和队列的**泛化**：
- 可以从**两端**任意插入和删除
- 用它可以模拟栈（只用一端）也可以模拟队列（两端各用一端）

```
左端  ←→  [A] [B] [C] [D] [E]  ←→  右端
addLeft/removeLeft              addRight/removeRight
```

### ADT 定义

```
Deque()           创建空双端队列
add_front(item)   在左端添加元素         O(1)
add_rear(item)    在右端添加元素         O(1)
remove_front()    移除并返回左端元素     O(1)
remove_rear()     移除并返回右端元素     O(1)
is_empty()        是否为空
size()            元素个数
```

### ⭐【面试常考】应用：回文检测

#### 问题
判断一个字符串是否是回文（正读反读相同），如 `"racecar"`, `"abcba"`。

#### 暴力 vs 双端队列

```python
# 方案1：字符串反转（最简洁，Python特有）
def is_palindrome_v1(s):
    return s == s[::-1]   # O(n) 时间 O(n) 空间

# 方案2：双指针（最优，O(1)额外空间）
def is_palindrome_v2(s):
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True

# 方案3：双端队列（体现 Deque 的思想）
from collections import deque

def is_palindrome_deque(s):
    """
    双端队列法：将字符逐一加入，从两端同时比较
    
    执行流程（"racecar"）：
    初始：deque(['r','a','c','e','c','a','r'])
    第1轮：popleft='r', pop='r'  → 相等，继续
    第2轮：popleft='a', pop='a'  → 相等，继续
    第3轮：popleft='c', pop='c'  → 相等，继续
    剩余：deque(['e'])，长度=1，停止
    结果：True ✅
    """
    d = deque(s)
    while len(d) > 1:
        if d.popleft() != d.pop():   # 左端 vs 右端
            return False
    return True

# 实际面试扩展：忽略大小写和非字母数字字符
def is_palindrome_clean(s):
    """LeetCode 125 题的完整版本"""
    # 预处理：只保留字母和数字，转为小写
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]

print(is_palindrome_clean("A man, a plan, a canal: Panama"))  # True
print(is_palindrome_clean("race a car"))                       # False
```

---

## 3.6 ⭐ 链表（Linked List）

### 3.6.1 为什么需要链表？从内存角度理解

```
Python 列表（本质是动态数组）：
内存中连续存储：
[地址100] [地址104] [地址108] [地址112] [地址116]
  val=1      val=2    val=3    val=4    val=5

在位置1插入新元素：需要把 2,3,4,5 全部向右移动一格
代价：O(n)

链表：
每个节点可以在内存任意位置：
[地址052]    [地址200]    [地址031]    [地址178]
 val=1        val=2        val=3        val=4
 next=200     next=031     next=178     next=None

在头部插入：只需修改新节点的 next 和 head 指针
代价：O(1)！！
```

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  data=1 │───▶│  data=2 │───▶│  data=3 │───▶│  data=4 │───▶ None
│  next   │    │  next   │    │  next   │    │  next   │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     ▲
    head（链表唯一的入口！）
```

### 3.6.2 节点类（链表的积木）

```python
class Node:
    """
    链表节点：最简单的复合数据结构
    
    data：存储的实际数据（可以是任何类型）
    next：存储下一个节点的"地址"（Python中是引用/指针）
    
    当 next = None 时，表示这是链表的最后一个节点
    """
    def __init__(self, data):
        self.data = data    # 数据域
        self.next = None    # 指针域，初始指向"空"


# ══ 手动构建链表，理解指针的含义 ══
n1 = Node(10)
n2 = Node(20)
n3 = Node(30)

# 建立连接（修改指针）
n1.next = n2    # 节点1 → 节点2
n2.next = n3    # 节点2 → 节点3
# n3.next 默认 None，表示链表结束

# head 是访问链表的唯一入口，永远指向第一个节点
head = n1

# 遍历链表：沿着 next 指针走
current = head
while current is not None:
    print(current.data, end=' → ')   # 10 → 20 → 30 →
    current = current.next
print("None")
```

### 3.6.3 ⭐ 无序链表完整实现（含执行流程图解）

```python
class UnorderedLinkedList:
    """
    无序单向链表
    
    核心属性：
    - self.head：始终指向第一个节点
    - 空链表：self.head = None
    
    操作复杂度：
    - add（头部插入）：O(1)  ← 链表最大优势
    - search（查找）：O(n)
    - remove（删除）：O(n)
    - size（计数）  ：O(n)
    """
    
    def __init__(self):
        self.head = None    # 空链表，head 指向 None
    
    # ─────────────────────────────────────────────
    # 插入（头部插入，O(1)）
    # ─────────────────────────────────────────────
    def add(self, item):
        """
        头部插入新节点
        
        执行流程（以向空链表插入 1，再插入 2 为例）：
        
        步骤1：插入 1
          新建 Node(1)，next=None
          new_node.next = self.head  →  new_node.next = None
          self.head = new_node       →  head → [1|None]
        
        步骤2：插入 2
          新建 Node(2)，next=None
          new_node.next = self.head  →  Node(2).next → Node(1)
          self.head = new_node       →  head → [2| → ] → [1|None]
        
        结果：head → 2 → 1 → None
        注意：因为是头部插入，最后插入的排在最前面
        """
        new_node = Node(item)
        new_node.next = self.head   # ① 新节点指向当前头节点
        self.head = new_node        # ② head 改指向新节点
                                    # ① 必须在 ② 之前！否则会丢失原链表
    
    # ─────────────────────────────────────────────
    # 遍历（O(n)）
    # ─────────────────────────────────────────────
    def size(self):
        """
        遍历整个链表计数
        
        为什么不能直接返回一个成员变量？
        可以维护一个 self._size 计数器，但这里用遍历演示链表遍历模式
        """
        count = 0
        current = self.head           # 从头开始
        while current is not None:    # 直到走到链尾
            count += 1
            current = current.next    # 向后移一步
        return count
    
    def search(self, item):
        """线性查找，O(n)"""
        current = self.head
        while current is not None:
            if current.data == item:
                return True
            current = current.next
        return False
    
    # ─────────────────────────────────────────────
    # 删除（双指针技术，O(n)）
    # ─────────────────────────────────────────────
    def remove(self, item):
        """
        删除第一个值为 item 的节点
        
        ═══ 核心技巧：双指针（previous + current）═══
        
        为什么需要 previous 指针？
        删除节点需要把"前一个节点的 next"跳过被删节点，
        但链表是单向的，无法从当前节点找到上一个节点，
        所以必须在遍历时同时记录"上一个节点"。
        
        执行流程：链表 5 → 3 → 8 → None，删除 3
        
        初始：previous=None, current=Node(5)
        
        第1步：current.data=5 ≠ 3
          previous = Node(5)
          current  = Node(3)   ← 向前走
        
        第2步：current.data=3 == 3，找到！
          previous 不为 None，执行：
          previous.next = current.next
          即 Node(5).next = Node(8)
          结果：5 → 8 → None  ✅ 节点3被跳过（删除）
        
        特殊情况：删除的是头节点（previous=None）
          直接让 self.head = current.next
        """
        current = self.head
        previous = None
        
        while current is not None:
            if current.data == item:   # 找到目标节点
                if previous is None:
                    # 情况1：删除头节点
                    self.head = current.next
                else:
                    # 情况2：删除中间或尾节点
                    previous.next = current.next   # 跳过当前节点
                return   # 删除成功，退出
            
            # 未找到，继续向前
            previous = current          # previous 跟上
            current = current.next      # current 前进
        
        raise ValueError(f"{item} not in list")
    
    def __str__(self):
        nodes = []
        current = self.head
        while current:
            nodes.append(str(current.data))
            current = current.next
        return " → ".join(nodes) + " → None" if nodes else "None"


# ══ 测试：完整操作流程 ══
ll = UnorderedLinkedList()

# 插入（头部插入，注意：结果是逆序）
for val in [1, 2, 3, 4, 5]:
    ll.add(val)
print(ll)              # 5 → 4 → 3 → 2 → 1 → None

print(ll.search(3))    # True
print(ll.search(9))    # False
print(ll.size())       # 5

ll.remove(3)           # 删除中间节点
print(ll)              # 5 → 4 → 2 → 1 → None

ll.remove(5)           # 删除头节点
print(ll)              # 4 → 2 → 1 → None

ll.remove(1)           # 删除尾节点
print(ll)              # 4 → 2 → None
```

---

### 3.6.4 ⭐⭐【面试重点】链表经典题目

#### 题目1：反转链表（LeetCode 206）

这是链表最核心的面试题，考察对指针操作的掌握。

**暴力思路**：把所有值放到列表里，反转后重建链表。
- 时间 O(n)，空间 O(n)，但面试官通常要求 O(1) 空间原地反转。

```python
def reverse_list(head):
    """
    迭代原地反转链表
    
    核心：用三个指针 prev, curr, next_node
    每步把 curr.next 从指向"后面"改为指向"前面"
    
    执行流程（1 → 2 → 3 → None）：
    
    初始：prev=None, curr=Node(1)
    
    第1步：
      next_node = curr.next    → Node(2)  保存后继，防止丢失
      curr.next = prev         → Node(1).next = None  反转！
      prev = curr              → prev = Node(1)
      curr = next_node         → curr = Node(2)
      此时：None ← 1  2 → 3 → None
    
    第2步：
      next_node = curr.next    → Node(3)
      curr.next = prev         → Node(2).next = Node(1)  反转！
      prev = curr              → prev = Node(2)
      curr = next_node         → curr = Node(3)
      此时：None ← 1 ← 2  3 → None
    
    第3步：
      next_node = curr.next    → None
      curr.next = prev         → Node(3).next = Node(2)  反转！
      prev = curr              → prev = Node(3)
      curr = next_node         → curr = None
      此时：None ← 1 ← 2 ← 3
    
    循环结束（curr=None），prev=Node(3) 就是新的头节点
    最终：3 → 2 → 1 → None  ✅
    """
    prev = None
    curr = head
    
    while curr is not None:
        next_node = curr.next    # ① 保存后继（关键！防止断链）
        curr.next = prev         # ② 反转当前节点的指针
        prev = curr              # ③ prev 前进
        curr = next_node         # ④ curr 前进
    
    return prev   # prev 就是反转后的新头节点


# 辅助函数：构建链表
def build_list(values):
    if not values:
        return None
    head = Node(values[0])
    cur = head
    for v in values[1:]:
        cur.next = Node(v)
        cur = cur.next
    return head

def print_list(head):
    vals = []
    while head:
        vals.append(str(head.data))
        head = head.next
    print(" → ".join(vals) + " → None")

head = build_list([1, 2, 3, 4, 5])
print_list(head)                    # 1 → 2 → 3 → 4 → 5 → None
new_head = reverse_list(head)
print_list(new_head)                # 5 → 4 → 3 → 2 → 1 → None
```

#### 题目2：检测链表中的环（LeetCode 141）

**问题**：给定链表，判断是否有环（某节点的 next 指向链表中已存在的节点）。

**暴力思路（用集合）**：遍历时把每个节点存到集合，若节点已在集合中，说明有环。
- 时间 O(n)，空间 O(n)

```python
def has_cycle_set(head):
    """暴力：用集合记录已访问节点，O(n) 空间"""
    visited = set()
    current = head
    while current:
        if id(current) in visited:   # id() 获取内存地址，唯一标识对象
            return True
        visited.add(id(current))
        current = current.next
    return False
```

**优化：Floyd 判圈算法（快慢指针）**

```python
def has_cycle_floyd(head):
    """
    Floyd 判圈算法（龟兔赛跑）
    
    核心思想：
    设两个指针：slow（每次走1步）和 fast（每次走2步）
    - 若无环：fast 会先到达 None，结束
    - 若有环：fast 最终会追上 slow（在环内相遇）
    
    为什么 fast 一定能追上 slow？
    设 fast 比 slow 快1步/轮，每轮差距缩小1，
    差距从某值最终变为0，即相遇。
    
    时间：O(n)，空间：O(1)  ← 相比集合方法节省空间
    """
    if not head or not head.next:
        return False
    
    slow = head         # 慢指针，每次走1步
    fast = head         # 快指针，每次走2步
    
    while fast and fast.next:
        slow = slow.next          # 慢指针走1步
        fast = fast.next.next     # 快指针走2步
        
        if slow is fast:          # 相遇！有环
            return True
    
    return False   # fast 到达 None，无环
```

> **⚠️ 面试注意点**：
> 1. 用 `id()` 比较对象地址，不能用 `==` 比较值（值相同不代表是同一节点）
> 2. 快慢指针中，循环条件是 `fast and fast.next`，防止空指针异常
> 3. `is` 比较引用，`==` 比较值，这里必须用 `is`

#### 题目3：找链表中点（LeetCode 876）

```python
def find_middle(head):
    """
    快慢指针找中点
    
    当 fast 到达末尾时，slow 恰好在中间
    偶数个节点时返回后半段的第一个节点
    
    执行流程（1 → 2 → 3 → 4 → 5）：
    初始：slow=1, fast=1
    第1轮：slow=2, fast=3
    第2轮：slow=3, fast=5
    fast.next=None，停止，返回 slow=3（中点）✅
    """
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```

---

## 3.7 各结构操作复杂度对比

| 操作 | Python list | Stack | Queue(deque) | 链表 |
|------|:-----------:|:-----:|:------------:|:----:|
| 头部插入 | O(n) | — | O(1) | **O(1)** |
| 尾部插入 | O(1) | O(1) push | O(1) enqueue | O(n) |
| 头部删除 | O(n) | — | **O(1)** dequeue | **O(1)** |
| 尾部删除 | O(1) | O(1) pop | O(1) | O(n) |
| 按索引访问 | **O(1)** | — | — | O(n) |
| 查找（值）| O(n) | O(n) | O(n) | O(n) |
| 内存布局 | 连续 | 连续 | 分散 | 分散 |

---

## 3.8 本章要点总结

### 核心概念映射表

| 概念 | 定义 | 关键特征 | 实现工具 | 典型应用场景 |
|------|------|----------|---------|-------------|
| **ADT** | 只定义接口，不管实现 | 封装、抽象 | Python class | 所有数据结构的设计基础 |
| **栈 Stack** | 后进先出（LIFO） | 只操作顶部 | list / deque | 括号匹配、撤销操作、DFS、表达式求值 |
| **队列 Queue** | 先进先出（FIFO） | 尾进头出 | collections.deque | 打印队列、BFS、任务调度 |
| **双端队列 Deque** | 两端均可进出 | 栈+队列的超集 | collections.deque | 回文检测、滑动窗口最大值 |
| **链表** | 指针连接的节点序列 | 无需连续内存 | Node 类 | 频繁头部插入、内存敏感场景 |

### 核心思想总结

| 结构 | 核心思想 | 一句话记忆 |
|------|----------|----------|
| 栈 | LIFO——最近的最先处理 | "最后进来的最先出去，像叠盘子" |
| 队列 | FIFO——先到先服务 | "排队买票，先来先得" |
| 双端队列 | 两端灵活操作 | "栈和队列的合体" |
| 链表 | 指针建立连接，O(1)头插 | "通过地址找下一个，像寻宝游戏" |

### 关键方法速查

| 操作 | 栈 | 队列（deque）| 链表 |
|------|----|-----------|----|
| 添加 | `push()` / `append()` | `enqueue()` / `append()` | `add()` （头部）|
| 删除 | `pop()` | `dequeue()` / `popleft()` | `remove()` |
| 查看不删除 | `peek()` / `[-1]` | `[0]` | 遍历 |
| 判空 | `is_empty()` | `is_empty()` | `head is None` |

### 面试高频考点

| 题目类型 | 对应结构 | 核心技巧 | 复杂度 |
|----------|---------|---------|--------|
| 括号匹配 | 栈 | 左括号压栈，右括号比对弹出 | O(n) / O(n) |
| 逆波兰表达式 | 栈 | 数字压栈，运算符弹两个算 | O(n) / O(n) |
| 回文判断 | 双端队列/双指针 | 两端同时比较 | O(n) / O(1) |
| 反转链表 | 链表 | 三指针 prev/curr/next | O(n) / O(1) |
| 检测环 | 链表 | 快慢指针（Floyd算法） | O(n) / O(1) |
| 找链表中点 | 链表 | 快慢指针 | O(n) / O(1) |

### 工具选择指南

```
需要"后进先出"？
  → 用 Stack，或者直接用 list（append/pop）

需要"先进先出"？
  → 用 collections.deque，不要用 list（pop(0)是O(n)）

需要两端操作（如滑动窗口）？
  → 直接用 collections.deque

需要频繁头部插入/删除？
  → 用链表

需要按索引随机访问？
  → 用 list（链表访问第n个是O(n)）
```

### 注意事项（坑点）

1. **`list.pop(0)` 是 O(n)**：用列表模拟队列时，`pop(0)` 需要移动所有元素，大数据量时极慢。生产代码用 `collections.deque`。
2. **链表删除须维护 previous 指针**：单向链表无法反向，删除时必须记录前驱。
3. **链表插入两步顺序不能颠倒**：头部插入时，必须先让新节点指向旧头（`new_node.next = head`），再更新 head，否则原链表丢失。
4. **快慢指针循环条件**：`while fast and fast.next`，两个条件都要有，防止空指针异常。
5. **弹栈顺序影响结果**：逆波兰求值中，`b = pop()` 先弹（是右操作数），`a = pop()` 后弹（是左操作数），`a - b` 不是 `b - a`。

---

> **给初学者的学习建议**：
> 1. 栈的括号匹配和链表的反转，必须**不看提示手写一遍**，这是检验理解的最好方式。
> 2. 学链表最大的障碍是指针操作——建议在纸上画图，每步操作后画出指针指向，不要光靠脑子想。
> 3. 面试时如果忘了链表某个操作，先想"我需要知道哪个节点的前驱/后继"，答案就有了。
> 4. `collections.deque` 是 Python 中最实用的数据结构之一，背下它的接口（`append`/`appendleft`/`pop`/`popleft`）。
