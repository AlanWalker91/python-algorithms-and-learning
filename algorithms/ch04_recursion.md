# 第4章：递归

> **核心思路**：递归是"用同一个问题的更小版本来解决当前问题"。关键在于找到**基本情况**（终止条件）和**递归情况**（缩小问题）。本章还引出动态规划的思想。

---

## 4.1 什么是递归

递归函数就是**调用自身**的函数。

类比：**俄罗斯套娃**——打开一个娃娃，里面还是相同的结构，只是更小，直到最小的那个（基本情况）。

### 递归三要素（必须满足！）

```
1. 基本情况（Base Case）  ← 必须有，否则无限递归
   → 能直接返回答案，不需要继续递归的情况

2. 递归情况（Recursive Case）
   → 把问题转化为规模更小的同类问题

3. 向基本情况收敛
   → 每次递归调用，问题规模必须在缩小
```

### 最简单的例子：计算 n 的阶乘

```python
def factorial(n):
    """
    n! = n × (n-1) × (n-2) × ... × 1
    
    递归思路：
    - 基本情况：n == 1，直接返回 1
    - 递归情况：n! = n × (n-1)!
    """
    # ⭐ 基本情况：必须放在前面！
    if n == 1:
        return 1
    
    # 递归情况：规模从 n 缩小到 n-1
    return n * factorial(n - 1)

# 执行过程追踪（n=4）：
# factorial(4)
#   = 4 × factorial(3)
#       = 4 × 3 × factorial(2)
#           = 4 × 3 × 2 × factorial(1)
#               = 4 × 3 × 2 × 1  ← 触底，开始回溯
#           = 4 × 3 × 2
#       = 4 × 6
#   = 24
```

---

## 4.2 ⭐ 整数进制转换

递归经典应用——把十进制整数转换为任意进制字符串。

```python
def to_base(n, base):
    """
    递归实现进制转换
    
    关键洞察：
    - n % base 得到当前最低位的数字
    - n // base 是"去掉最低位"后的更小问题
    
    举例：n=13, base=2
    13 % 2 = 1  ← 最低位是1
    6  % 2 = 0  ← 次低位是0
    3  % 2 = 1  ← 第三位是1
    1  % 2 = 1  ← 最高位是1
    结果：1101（从高位到低位读）
    """
    digits = "0123456789ABCDEF"
    
    # 基本情况：n < base 时只有一位
    if n < base:
        return digits[n]
    
    # 递归情况：先递归处理高位，再拼接当前最低位
    return to_base(n // base, base) + digits[n % base]

print(to_base(13, 2))   # '1101'
print(to_base(255, 16)) # 'FF'
```

---

## 4.3 ⭐ 汉诺塔（Tower of Hanoi）

递归最经典的"震撼级"示例——展示了递归分解复杂问题的惊人能力。

**问题描述**：
- 3根柱子：A（源）、B（辅助）、C（目标）
- n个大小不同的圆盘叠在A上，大盘在下
- 规则：每次只能移动一个盘，且大盘不能放在小盘上
- 目标：把所有盘从A移到C

```python
def hanoi(n, source, target, auxiliary):
    """
    汉诺塔递归解法
    
    关键洞察（递归分解）：
    想把 n 个盘从 source 移到 target，只需：
    1. 把上面 n-1 个盘从 source 移到 auxiliary（用 target 作辅助）
    2. 把最大的盘从 source 直接移到 target
    3. 把 n-1 个盘从 auxiliary 移到 target（用 source 作辅助）
    
    基本情况：n==1，直接移动
    """
    if n == 1:
        print(f"移动圆盘 1：{source} → {target}")
        return
    
    # 步骤1：把 n-1 个盘从 source 移到 auxiliary
    hanoi(n - 1, source, auxiliary, target)
    
    # 步骤2：移动最大的盘
    print(f"移动圆盘 {n}：{source} → {target}")
    
    # 步骤3：把 n-1 个盘从 auxiliary 移到 target
    hanoi(n - 1, auxiliary, target, source)

hanoi(3, 'A', 'C', 'B')
# 移动圆盘 1：A → C
# 移动圆盘 2：A → B
# 移动圆盘 1：C → B
# 移动圆盘 3：A → C
# 移动圆盘 1：B → A
# 移动圆盘 2：B → C
# 移动圆盘 1：A → C

# n个盘需要 2ⁿ-1 次移动 → O(2ⁿ)
# n=64: 需要 18,446,744,073,709,551,615 次！
```

---

## 4.4 调用栈（Call Stack）

理解递归的执行机制，必须理解调用栈。

```python
def f(x):
    print(f"进入 f({x})")
    if x == 0:
        print("触底！")
        return 0
    result = x + f(x - 1)
    print(f"返回 f({x}) = {result}")
    return result

f(3)
# 执行顺序：
# 进入 f(3)  ← 压栈
#   进入 f(2)  ← 压栈
#     进入 f(1)  ← 压栈
#       进入 f(0)  ← 压栈
#       触底！
#     返回 f(1) = 1  ← 弹栈
#   返回 f(2) = 3  ← 弹栈
# 返回 f(3) = 6  ← 弹栈
```

```
调用栈示意（f(3) 时）：
┌─────────────┐  ← 栈顶
│  f(0): x=0  │
├─────────────┤
│  f(1): x=1  │
├─────────────┤
│  f(2): x=2  │
├─────────────┤
│  f(3): x=3  │  ← 栈底
└─────────────┘

递归深度 n → 占用 O(n) 栈空间
Python 默认递归深度限制：约 1000 层
```

---

## 4.5 迷宫探索

递归在路径搜索中的应用——深度优先探索。

```python
def solve_maze(maze, start_row, start_col):
    """
    迷宫递归求解
    
    maze: 二维列表，' '=通路，'#'=墙，'E'=出口
    
    思路：从当前位置向四个方向尝试，
    如果某个方向可以走到出口，返回True；
    用'.'标记已走过的路径（避免重复走）
    """
    ROWS, COLS = len(maze), len(maze[0])
    
    # 基本情况1：出界
    if not (0 <= start_row < ROWS and 0 <= start_col < COLS):
        return False
    
    # 基本情况2：碰到墙或已访问
    cell = maze[start_row][start_col]
    if cell == '#' or cell == '.':
        return False
    
    # 基本情况3：找到出口！
    if cell == 'E':
        return True
    
    # 标记当前格为已访问
    maze[start_row][start_col] = '.'
    
    # 递归情况：向四个方向尝试
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 上下左右
    for dr, dc in directions:
        if solve_maze(maze, start_row + dr, start_col + dc):
            return True
    
    # 四个方向都走不通，回溯：取消标记
    maze[start_row][start_col] = ' '
    return False
```

---

## 4.6 ⭐ 动态规划（Dynamic Programming）

### 问题引入：找零问题

**问题**：用最少的硬币凑出指定金额。硬币面值：[1, 5, 10, 25] 美分。

#### 方案1：朴素递归（有严重重复计算）

```python
def make_change_naive(coin_list, change):
    """
    朴素递归找零
    
    思路：对每种硬币，递归求解"减去该硬币后"的最优解
    
    ⚠️ 问题：大量重复子问题
    change=11时，会重复计算 change=6、change=1 等很多次
    """
    # 基本情况：刚好凑满
    if change in coin_list:
        return 1
    # 基本情况：凑不出来
    if change < min(coin_list):
        return float('inf')
    
    min_coins = float('inf')
    for coin in [c for c in coin_list if c <= change]:
        # 递归：减去一枚硬币后的最优解 + 1
        result = make_change_naive(coin_list, change - coin) + 1
        min_coins = min(min_coins, result)
    
    return min_coins
```

#### ⭐ 方案2：记忆化递归（Memoization）

```python
def make_change_memo(coin_list, change, memo={}):
    """
    记忆化递归（自顶向下动态规划）
    
    核心思想：把已经计算过的结果存起来，避免重复计算
    这就是"记忆化"—— memo 字典是一个"备忘录"
    """
    # 查缓存：如果已经算过，直接返回
    if change in memo:
        return memo[change]
    
    # 基本情况
    if change in coin_list:
        memo[change] = 1
        return 1
    if change < min(coin_list):
        return float('inf')
    
    min_coins = float('inf')
    for coin in [c for c in coin_list if c <= change]:
        result = make_change_memo(coin_list, change - coin, memo) + 1
        min_coins = min(min_coins, result)
    
    # 存入缓存
    memo[change] = min_coins
    return min_coins
```

#### ⭐ 方案3：动态规划（自底向上，最优）

```python
def make_change_dp(coin_list, change):
    """
    自底向上动态规划
    
    核心思想：
    从最小子问题（change=1）开始，逐步构建到目标
    dp[i] = 凑出 i 分钱所需的最少硬币数
    
    状态转移方程：
    dp[i] = min(dp[i - coin] + 1) for coin in coin_list if coin <= i
    """
    # 初始化：dp[0]=0（0分不需要硬币），其余设为无穷大
    dp = [float('inf')] * (change + 1)
    dp[0] = 0
    
    # 从 1 到 change 逐一填表
    for amount in range(1, change + 1):
        for coin in coin_list:
            if coin <= amount and dp[amount - coin] + 1 < dp[amount]:
                dp[amount] = dp[amount - coin] + 1  # 状态转移
    
    return dp[change] if dp[change] != float('inf') else -1

# 测试
coins = [1, 5, 10, 25]
print(make_change_dp(coins, 11))   # 3（10+1+?? 不对，是10+1=11，2枚）
# 实际：11 = 10 + 1，答案是 2
print(make_change_dp(coins, 30))   # 2（25+5）
print(make_change_dp(coins, 36))   # 3（25+10+1）
```

### 动态规划的两个核心特征

```
1. 重叠子问题（Overlapping Subproblems）
   → 同一个子问题会被重复求解多次
   → 解决方案：记忆化 / 填表

2. 最优子结构（Optimal Substructure）
   → 原问题的最优解包含子问题的最优解
   → 可以从子问题的最优解推导出原问题的最优解
```

---

## 4.7 递归 vs 迭代

```python
# 同一个问题的两种实现方式对比

# 递归：代码简洁，但有调用栈开销
def sum_recursive(n):
    if n == 0:
        return 0
    return n + sum_recursive(n - 1)   # O(n) 时间，O(n) 栈空间

# 迭代：稍显冗长，但更高效
def sum_iterative(n):
    total = 0
    for i in range(n + 1):
        total += i                    # O(n) 时间，O(1) 空间

# 选择建议：
# - 问题本身天然递归（树、图遍历）→ 用递归
# - 追求极致性能，或递归层次很深 → 用迭代
# - Python有默认递归深度限制（~1000），注意不要超出
```

---

## 4.8 本章要点总结

| 概念 | 要点 |
|------|------|
| **三要素** | 基本情况 + 递归情况 + 必须收敛，缺一不可 |
| **调用栈** | 每层递归占一个栈帧；深度过大会栈溢出 |
| **汉诺塔** | O(2ⁿ)；展示了递归的表达力 |
| **记忆化** | 空间换时间，避免重复计算 |
| **⭐DP关键** | 找到"状态转移方程"是动态规划的核心 |

> **给初学者的建议**：
> 1. 写递归时，**先写基本情况**，再写递归情况——永远从"能直接回答的最小情况"开始思考。
> 2. 调试递归时，多加 `print` 打印当前参数和返回值，把执行过程可视化。
> 3. 动态规划初学先掌握"找零问题"，理解了这一题，再举一反三到背包问题等。
