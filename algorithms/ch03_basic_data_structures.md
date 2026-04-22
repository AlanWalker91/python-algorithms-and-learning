# 第3章：基本数据结构

> **核心思路**：先从生活中的类比建立直觉，再抽象出 ADT（抽象数据类型）定义操作接口，最后用 Python 实现并分析复杂度。本章覆盖四种线性结构：栈、队列、双端队列、链表。

---

## 3.1 什么是线性结构

线性结构的特点：**元素之间存在唯一的前驱和后继关系**，像一条链。

四种线性结构的区别在于**元素从哪里进、从哪里出**：

| 结构 | 进入端 | 退出端 | 原则 |
|------|--------|--------|------|
| 栈 Stack | 顶部 | 顶部 | 后进先出 LIFO |
| 队列 Queue | 尾部 | 头部 | 先进先出 FIFO |
| 双端队列 Deque | 两端 | 两端 | 灵活 |
| 链表 LinkedList | 任意 | 任意 | 基于指针 |

---

## 3.2 栈（Stack）

### 生活类比
餐盘叠放：最后放上去的盘子（栈顶），总是最先被取走。

### ADT 定义
```
Stack()       创建空栈
push(item)    压入元素到栈顶
pop()         从栈顶移除并返回元素
peek()        查看栈顶元素（不移除）
is_empty()    判断是否为空
size()        返回元素个数
```

### ⭐ Python 实现

```python
class Stack:
    """
    用 Python 列表实现栈
    
    关键设计决策：以列表末尾作为栈顶
    → append() 和 pop() 都是 O(1)
    → 如果以列表头部为栈顶，insert(0)和pop(0)都是O(n)，太慢
    """
    
    def __init__(self):
        self._data = []          # 用列表存储，末尾 = 栈顶
    
    def push(self, item):
        self._data.append(item)  # O(1)
    
    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._data.pop()  # O(1)，移除并返回末尾元素
    
    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._data[-1]    # O(1)，只看不取
    
    def is_empty(self):
        return len(self._data) == 0
    
    def size(self):
        return len(self._data)
    
    def __str__(self):
        return str(self._data) + " ← top"
```

### ⭐ 应用1：括号匹配

**问题**：判断 `"[{()}]"` 这样的字符串括号是否合法匹配。

**思路**：遇到左括号就压栈；遇到右括号就与栈顶比较——如果匹配就弹出，否则失败。

```python
def check_brackets(symbol_string):
    """
    括号匹配检测
    
    核心思想：利用栈的 LIFO 特性
    最近打开的左括号，应该被最近的右括号关闭
    """
    s = Stack()
    # 建立右括号到左括号的映射
    matches = {')': '(', ']': '[', '}': '{'}
    
    for symbol in symbol_string:
        if symbol in '([{':           # 左括号：压栈
            s.push(symbol)
        elif symbol in ')]}':         # 右括号：检查匹配
            if s.is_empty():          # 栈空说明没有对应的左括号
                return False
            if s.pop() != matches[symbol]:  # 弹出栈顶，与期望不符
                return False
    
    return s.is_empty()  # 最终栈必须为空，否则有未匹配的左括号

# 测试
print(check_brackets("((()))"))    # True
print(check_brackets("[{()}]"))    # True
print(check_brackets("([)]"))      # False ← 交叉嵌套
print(check_brackets("((()"))      # False ← 左括号多余
```

### ⭐ 应用2：进制转换

**思路**：不断取余数压栈，最后弹出时顺序就反转了——正好是高位在前。

```python
def convert_base(decimal_num, base):
    """
    十进制转任意进制（2~16）
    
    核心思想：
    除法每次得到一位数字（从低位到高位），
    用栈存储后反序弹出，得到正确顺序（从高位到低位）
    """
    digits = "0123456789ABCDEF"  # 支持到16进制
    s = Stack()
    
    if decimal_num == 0:
        return "0"
    
    while decimal_num > 0:
        remainder = decimal_num % base   # 取当前最低位
        s.push(digits[remainder])        # 压入对应字符
        decimal_num = decimal_num // base # 缩小问题规模
    
    result = ""
    while not s.is_empty():
        result += s.pop()               # 弹出顺序 = 从高位到低位
    
    return result

print(convert_base(233, 2))    # '11101001'（二进制）
print(convert_base(233, 8))    # '351'（八进制）
print(convert_base(233, 16))   # 'E9'（十六进制）
```

### ⭐ 应用3：中缀表达式转后缀（逆波兰表达式）

**为什么需要？**：计算机处理 `3 + 4 * 2` 时需要知道优先级，后缀表达式 `3 4 2 * +` 无需括号即可明确顺序。

```python
def infix_to_postfix(infix_expr):
    """
    中缀转后缀
    
    规则：
    1. 操作数直接输出
    2. 左括号压栈
    3. 右括号：弹出直到遇到左括号
    4. 运算符：弹出所有优先级≥当前运算符的符号，再压入当前运算符
    """
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '(': 0}
    op_stack = Stack()
    output = []
    
    for token in infix_expr.split():
        if token not in '+-*/()':
            output.append(token)           # 操作数直接输出
        elif token == '(':
            op_stack.push(token)           # 左括号压栈
        elif token == ')':
            # 弹出直到遇到左括号
            while not op_stack.is_empty() and op_stack.peek() != '(':
                output.append(op_stack.pop())
            op_stack.pop()                 # 弹出左括号（丢弃）
        else:
            # 运算符：弹出优先级更高或相同的
            while (not op_stack.is_empty() and
                   precedence.get(op_stack.peek(), 0) >= precedence[token]):
                output.append(op_stack.pop())
            op_stack.push(token)
    
    while not op_stack.is_empty():
        output.append(op_stack.pop())
    
    return ' '.join(output)

print(infix_to_postfix("3 + 4 * 2"))         # '3 4 2 * +'
print(infix_to_postfix("( 3 + 4 ) * 2"))     # '3 4 + 2 *'
```

---

## 3.3 队列（Queue）

### 生活类比
超市排队结账：先来的人先结账，后来的人在队尾等候。

### ADT 定义
```
Queue()       创建空队列
enqueue(item) 元素加入队尾
dequeue()     从队头移除并返回元素
is_empty()    判断是否为空
size()        返回元素个数
```

### Python 实现

```python
class Queue:
    """
    用列表实现队列
    
    设计：列表末尾 = 队尾（enqueue用append，O(1)）
          列表头部 = 队头（dequeue用pop(0)，O(n)）
    
    ⚠️ 注意：pop(0) 是 O(n)，如果性能要求高
    应改用 collections.deque（双端队列）
    """
    
    def __init__(self):
        self._data = []
    
    def enqueue(self, item):
        self._data.append(item)      # 加入队尾，O(1)
    
    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._data.pop(0)     # 从队头移除，O(n)
    
    def is_empty(self):
        return len(self._data) == 0
    
    def size(self):
        return len(self._data)
```

### ⭐ 应用：热土豆问题（约瑟夫问题）

**问题**：n个人围坐一圈，每数到第k个人就淘汰，最后剩下谁？

```python
def hot_potato(names, num):
    """
    传土豆模拟
    
    思路：
    用队列模拟圆圈——每次把队头移到队尾（传土豆），
    数到num时就把当前队头淘汰（出局）
    """
    q = Queue()
    for name in names:
        q.enqueue(name)    # 所有人入队
    
    while q.size() > 1:
        # 传 num-1 次：队头移到队尾（传土豆）
        for _ in range(num - 1):
            q.enqueue(q.dequeue())
        
        # 第 num 个人出局
        eliminated = q.dequeue()
        print(f"淘汰：{eliminated}")
    
    return q.dequeue()     # 最后剩下的人

winner = hot_potato(["Alice","Bob","Carol","Dave","Eve"], 3)
print(f"获胜者：{winner}")
```

---

## 3.4 双端队列（Deque）

### 特点
两端都可以进出，是栈和队列的结合。

```python
from collections import deque  # Python内置高效双端队列

# ⭐ 应用：回文检测
def is_palindrome(word):
    """
    回文检测
    
    思路：将字符放入双端队列，
    每次同时从两端取出比较，若全部相等则是回文
    """
    d = deque(word)          # 直接用字符串初始化
    while len(d) > 1:
        if d.popleft() != d.pop():  # 左端和右端比较
            return False
    return True

print(is_palindrome("radar"))   # True
print(is_palindrome("hello"))   # False
print(is_palindrome("racecar")) # True
```

---

## 3.5 ⭐ 链表（Linked List）

### 为什么需要链表？

列表在内存中是连续存储的，插入/删除中间元素需要移动大量数据（O(n)）。
链表通过**指针**连接不连续的节点，可以 O(1) 地在头部插入。

```
列表内存布局：[1][2][3][4][5]  ← 连续，随机访问快
链表内存布局：[1]→[2]→[3]→[4]→[5]→None  ← 分散，插入删除快
```

### 节点类

```python
class Node:
    """
    链表的基本单元
    每个节点保存：数据 + 指向下一个节点的引用
    """
    def __init__(self, data):
        self.data = data    # 存储的数据
        self.next = None    # 指向下一个节点，初始为None

# 手动构建链表
n1 = Node(1)
n2 = Node(2)
n3 = Node(3)
n1.next = n2    # 1 → 2
n2.next = n3    # 2 → 3  完整链：1 → 2 → 3 → None
```

### ⭐ 无序链表完整实现

```python
class UnorderedList:
    """
    无序单向链表
    
    设计：head 指针指向第一个节点
    头部插入：O(1)  ← 链表的核心优势
    查找/删除：O(n) ← 需要遍历
    """
    
    def __init__(self):
        self.head = None    # 初始为空链表
    
    def is_empty(self):
        return self.head is None
    
    def add(self, item):
        """
        头部插入（O(1)）
        
        步骤：
        1. 创建新节点
        2. 新节点的next指向当前head
        3. head指向新节点
        """
        new_node = Node(item)
        new_node.next = self.head   # 新节点指向原头部
        self.head = new_node        # head更新为新节点
    
    def size(self):
        """遍历计数，O(n)"""
        count = 0
        current = self.head
        while current is not None:
            count += 1
            current = current.next  # 沿指针前进
        return count
    
    def search(self, item):
        """线性查找，O(n)"""
        current = self.head
        while current is not None:
            if current.data == item:
                return True
            current = current.next
        return False
    
    def remove(self, item):
        """
        删除节点，O(n)
        
        技巧：需要记录前一个节点（previous）
        因为删除时需要修改前节点的next指针
        """
        current = self.head
        previous = None
        
        while current is not None:
            if current.data == item:
                if previous is None:
                    # 删除的是头节点
                    self.head = current.next
                else:
                    # 删除的是中间或尾节点
                    previous.next = current.next
                return
            previous = current
            current = current.next
        
        raise ValueError(f"{item} not in list")
    
    def __str__(self):
        """打印链表：1 → 2 → 3 → None"""
        result = []
        current = self.head
        while current is not None:
            result.append(str(current.data))
            current = current.next
        return ' → '.join(result) + ' → None'

# 测试
lst = UnorderedList()
for x in [1, 2, 3, 4, 5]:
    lst.add(x)           # 头部插入，所以顺序是反的

print(lst)               # 5 → 4 → 3 → 2 → 1 → None
print(lst.search(3))     # True
lst.remove(3)
print(lst)               # 5 → 4 → 2 → 1 → None
```

---

## 3.6 各结构操作复杂度对比

| 操作 | 列表(list) | 栈(Stack) | 队列(Queue) | 链表 |
|------|-----------|-----------|-------------|------|
| 头部插入 | O(n) | — | — | **O(1)** |
| 尾部插入 | O(1) | O(1) push | O(1) enqueue | O(n) |
| 头部删除 | O(n) | — | O(n) dequeue | **O(1)** |
| 尾部删除 | O(1) | O(1) pop | — | O(n) |
| 按索引访问 | **O(1)** | — | — | O(n) |
| 查找 | O(n) | — | — | O(n) |

---

## 3.7 本章要点总结

| 结构 | 记住什么 |
|------|----------|
| **栈** | LIFO；括号匹配、进制转换、表达式解析的标准工具 |
| **队列** | FIFO；BFS广度优先遍历必用；用`collections.deque`性能更好 |
| **双端队列** | 两端均可操作；回文检测经典应用 |
| **链表** | 头部插入O(1)；无需连续内存；是树和图的底层基础 |

> **给初学者的建议**：
> 1. 先把栈的括号匹配**手写一遍**，这是理解LIFO的最好方式。
> 2. 链表删除节点时"双指针"（current + previous）是核心技巧，反复练习。
> 3. 实际Python开发中，`collections.deque` 兼具栈和队列功能，且两端操作都是O(1)，优先使用。
