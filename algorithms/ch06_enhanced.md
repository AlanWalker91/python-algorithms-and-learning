# 第6章：树

> **本章导读**：树是从链表"升维"的结果——链表是一对一的线性关系，树是一对多的层级关系。树结构在计算机科学中无处不在：文件系统目录、HTML DOM、数据库索引、编译器语法树……都是树。
>
> **学习路径**：树的基本概念 → 二叉树表示 → 四种遍历（前/中/后序 + 层序）→ 二叉搜索树（BST）→ AVL 平衡树 → 二叉堆与优先队列
>
> **核心问题**：BST 的中序遍历为什么恰好是升序？为什么 AVL 树要引入旋转？理解这两个问题，本章就掌握了一半。

---

## 6.0 关键术语速查

| 术语 | 英文 | 定义 |
|------|------|------|
| 树 | Tree | 由节点和边组成的非线性结构，节点间满足层级关系 |
| 根节点 | Root | 没有父节点的唯一顶层节点，是访问整棵树的入口 |
| 叶节点 | Leaf | 没有子节点的节点，位于树的末端 |
| 内部节点 | Internal Node | 有子节点的非根节点 |
| 父节点 | Parent | 有子节点的节点，直接连接在子节点上方 |
| 子节点 | Child | 直接连接在某节点下方的节点 |
| 兄弟节点 | Sibling | 拥有同一父节点的节点 |
| 边 | Edge | 连接父子节点的线段，n 个节点的树恰好有 n-1 条边 |
| 路径 | Path | 从一个节点到另一个节点经过的节点序列 |
| 高度 | Height | 从根到最远叶节点的边数（空树高度为 -1 或 0，视定义而定） |
| 深度 | Depth | 从根到某节点的边数，根的深度为 0 |
| 层 | Level | 深度相同的所有节点在同一层，根在第 0 层（或第 1 层） |
| 子树 | Subtree | 某节点及其所有后代组成的树 |
| 二叉树 | Binary Tree | 每个节点最多有两个子节点（左子、右子）的树 |
| 完全二叉树 | Complete BT | 除最后一层外每层全满，且最后一层节点靠左排列 |
| 满二叉树 | Full BT | 每个节点要么是叶节点，要么有恰好两个子节点 |
| 二叉搜索树 | BST | 左子树所有值 < 根值 < 右子树所有值，递归成立 |
| AVL 树 | AVL Tree | 任意节点左右子树高度差 ≤ 1 的自平衡 BST |
| 平衡因子 | Balance Factor | 左子树高度 - 右子树高度，AVL 中必须在 {-1, 0, 1} |
| 旋转 | Rotation | AVL 树恢复平衡的操作，分左旋、右旋及其组合 |
| 二叉堆 | Binary Heap | 完全二叉树，父节点始终 ≤（最小堆）或 ≥（最大堆）子节点 |
| 优先队列 | Priority Queue | 每次出队的是优先级最高的元素，常用堆实现 |
| 前序遍历 | Preorder | 根 → 左 → 右 |
| 中序遍历 | Inorder | 左 → 根 → 右（BST 中序 = 升序序列） |
| 后序遍历 | Postorder | 左 → 右 → 根 |
| 层序遍历 | Level-order | 按层从上到下、从左到右（BFS） |

---

## 6.1 为什么需要树？

### 线性结构的局限

```
列表/链表：
  A → B → C → D → E
  只能表达"前后"关系，无法自然表达"层级"关系

现实中大量数据天然是层级结构：
  公司组织架构：CEO → 部门总监 → 员工
  文件系统    ：/ → home → user → documents → file.txt
  HTML 文档   ：<html> → <body> → <div> → <p>
  算术表达式  ：(3 + 4) * 2  →  运算符在上，操作数在下
```

### 树能做什么？

```
二叉搜索树：O(log n) 的查找、插入、删除
堆/优先队列：O(log n) 的取最值操作
文件系统   ：高效的目录层级管理
数据库索引 ：B 树、B+ 树支撑亿级数据的快速查询
```

---

## 6.2 树的基本概念

### 术语图解

```
              A           ← 根节点（Root），深度=0，层=0
            /   \
           B     C        ← 内部节点，深度=1
          / \     \
         D   E     F     ← 叶节点（Leaf），深度=2
         
树的高度 = 根到最远叶节点的边数 = 2
节点总数 = 6，边总数 = 5（节点数 - 1）

路径 A→B→D：长度为2（经过2条边）
B 的子节点：D 和 E
D 和 E 是兄弟节点
C 的子树：以 C 为根的子树，包含 C 和 F
```

### 二叉树的特殊形态

```
完全二叉树（Complete）：    满二叉树（Full）：
       1                          1
      / \                       /   \
     2   3                     2     3
    / \ /                     / \   / \
   4  5 6                    4   5 6   7
   
最后一层靠左填满              每个节点0或2个子节点
可以用数组高效存储             总节点数 = 2^h - 1（h为高度）
```

---

## 6.3 二叉树的节点与表示

```python
class TreeNode:
    """
    二叉树节点
    
    每个节点包含：
    - val  ：节点存储的值（任意类型）
    - left ：左子节点引用（None 表示没有左子）
    - right：右子节点引用（None 表示没有右子）
    """
    def __init__(self, val=0, left=None, right=None):
        self.val   = val
        self.left  = left
        self.right = right
    
    def __repr__(self):
        return f"TreeNode({self.val})"


# ══ 手动构建一棵树 ══
#        1
#       / \
#      2   3
#     / \
#    4   5

root = TreeNode(1)
root.left          = TreeNode(2)
root.right         = TreeNode(3)
root.left.left     = TreeNode(4)
root.left.right    = TreeNode(5)


# ══ 工具函数：从列表构建二叉树（层序输入，None 表示空）══
from collections import deque

def build_tree(values):
    """
    从层序列表构建二叉树
    输入：[1, 2, 3, 4, 5, None, 6]
    构建：      1
              / \
             2   3
            / \ / \
           4  5 N  6
    """
    if not values or values[0] is None:
        return None
    
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    
    while queue and i < len(values):
        node = queue.popleft()
        
        # 处理左子节点
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        
        # 处理右子节点
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    
    return root
```

---

## 6.4 ⭐ 四种树遍历

遍历 = 按照某种顺序访问树中每个节点恰好一次。
四种遍历方式的区别在于**根节点相对于左右子树的访问时机**。

### 记忆口诀

```
前序：根 → 左 → 右  （根最"前"，先访问根）
中序：左 → 根 → 右  （根在"中"间）
后序：左 → 右 → 根  （根最"后"，最后访问）
层序：按层从上到下   （广度优先，用队列）
```

### 示例树

```
        A
       / \
      B   C
     / \   \
    D   E   F
```

```python
def preorder(root):
    """
    前序遍历：根 → 左 → 右
    
    用途：
    - 复制一棵树（先复制根，再复制左右子树）
    - 打印目录结构（父目录在子目录之前显示）
    - 序列化/反序列化二叉树
    
    输出：A B D E C F
    """
    if root is None:
        return []
    
    result = []
    result.append(root.val)            # ① 访问根
    result.extend(preorder(root.left)) # ② 递归左子树
    result.extend(preorder(root.right))# ③ 递归右子树
    return result


def inorder(root):
    """
    中序遍历：左 → 根 → 右
    
    ⭐ 关键性质：对 BST 做中序遍历，得到升序序列
    
    用途：
    - 输出 BST 的有序序列
    - 验证一棵树是否是合法 BST
    - 第 k 小元素等 BST 相关问题
    
    输出：D B E A C F
    """
    if root is None:
        return []
    
    result = []
    result.extend(inorder(root.left))  # ① 先遍历左子树
    result.append(root.val)            # ② 访问根
    result.extend(inorder(root.right)) # ③ 再遍历右子树
    return result


def postorder(root):
    """
    后序遍历：左 → 右 → 根
    
    用途：
    - 删除树（必须先删子节点，再删父节点）
    - 计算表达式树的值（先算子表达式，再算父运算符）
    - 统计目录总大小（先统计子目录，再加上当前目录）
    
    输出：D E B F C A
    """
    if root is None:
        return []
    
    result = []
    result.extend(postorder(root.left))  # ① 左子树
    result.extend(postorder(root.right)) # ② 右子树
    result.append(root.val)              # ③ 最后访问根
    return result


def level_order(root):
    """
    层序遍历：按层从上到下，每层从左到右
    
    实现：用队列（FIFO）—— 当前节点出队时，把它的子节点入队
         出队顺序恰好就是按层顺序
    
    用途：
    - 求树的高度（层数）
    - 打印树的结构
    - BFS 广度优先搜索的基础
    
    输出：[[A], [B, C], [D, E, F]]（按层分组）
    """
    if root is None:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)     # 当前层的节点数
        current_level = []
        
        for _ in range(level_size): # 处理完整的一层
            node = queue.popleft()
            current_level.append(node.val)
            
            if node.left:           # 左子入队（下一层）
                queue.append(node.left)
            if node.right:          # 右子入队（下一层）
                queue.append(node.right)
        
        result.append(current_level)
    
    return result


# ══ 迭代版中序遍历（面试常考，不依赖递归）══
def inorder_iterative(root):
    """
    用显式栈模拟中序遍历
    
    思路：
    一路向左走，沿途把节点压栈
    走到底后弹栈访问，然后转向右子树
    
    执行流程（树：1-2-4, 1-2-5, 1-3）：
    curr=1，压栈  stack=[1]
    curr=2，压栈  stack=[1,2]
    curr=4，压栈  stack=[1,2,4]
    curr=None，弹出4，访问4，curr=4.right=None
    弹出2，访问2，curr=2.right=5
    curr=5，压栈  stack=[1,5]
    curr=None，弹出5，访问5，curr=None
    弹出1，访问1，curr=1.right=3
    ... 以此类推
    """
    result = []
    stack = []
    curr = root
    
    while curr or stack:
        # 一路向左走到底，沿途压栈
        while curr:
            stack.append(curr)
            curr = curr.left
        
        # 弹出访问（这就是"中序"的时机）
        curr = stack.pop()
        result.append(curr.val)
        
        # 转向右子树
        curr = curr.right
    
    return result
```

### 四种遍历对比

| 遍历 | 顺序 | 实现 | 主要用途 |
|------|------|------|---------|
| 前序 | 根→左→右 | 递归/栈 | 复制树、序列化 |
| **中序** | 左→根→右 | 递归/栈 | **BST 排序输出**（最重要） |
| 后序 | 左→右→根 | 递归/栈 | 删除树、表达式求值 |
| **层序** | 按层 BFS | **队列** | **求高度、BFS 类问题**（最重要） |

---

## 6.5 ⭐ 二叉搜索树（BST）

### 核心性质（BST 不变式）

```
对树中任意节点 N：
  N.left  子树中所有节点的值 < N.val
  N.right 子树中所有节点的值 > N.val
  左右子树也分别满足 BST 性质（递归定义）

这个性质直接推导出：
  ⭐ BST 的中序遍历 = 升序序列
     因为中序是"左（所有更小的）→ 根 → 右（所有更大的）"
```

### BST 插入与搜索

```python
class BST:
    """
    二叉搜索树
    
    平均操作复杂度（树较平衡时）：
    - 插入：O(log n)
    - 搜索：O(log n)
    - 删除：O(log n)
    
    ⚠️ 最坏情况（有序数据依次插入）：
    退化为链表，所有操作 O(n)
    → 这是为什么需要 AVL 树的原因
    """
    
    def __init__(self):
        self.root = None
    
    # ─────────────────────────────────────────────
    # 插入（递归版）
    # ─────────────────────────────────────────────
    def insert(self, val):
        self.root = self._insert(self.root, val)
    
    def _insert(self, node, val):
        """
        递归插入
        
        执行流程（向 BST [5,3,7] 插入 4）：
        
        _insert(Node(5), 4)
          4 < 5 → 递归左子树
          _insert(Node(3), 4)
            4 > 3 → 递归右子树
            _insert(None, 4)
              node=None，基本情况，创建新节点
              return Node(4)
            Node(3).right = Node(4)  ← 连接
            return Node(3)
          Node(5).left = Node(3)     ← 连接（不变）
          return Node(5)
        
        结果：    5
                 / \
                3   7
                 \
                  4  ← 新节点
        """
        if node is None:                    # 基本情况：找到空位，创建节点
            return TreeNode(val)
        
        if val < node.val:
            node.left  = self._insert(node.left,  val)   # 去左子树
        elif val > node.val:
            node.right = self._insert(node.right, val)   # 去右子树
        # val == node.val：重复值，通常忽略（或按需处理）
        
        return node   # 返回当前节点（连接递归结果）
    
    # ─────────────────────────────────────────────
    # 搜索
    # ─────────────────────────────────────────────
    def search(self, val):
        return self._search(self.root, val)
    
    def _search(self, node, val):
        """
        递归搜索：每次比较排除一半
        
        时间：O(log n) 平均，O(n) 最坏
        """
        if node is None:           # 到达空节点，未找到
            return False
        if val == node.val:
            return True            # 命中！
        elif val < node.val:
            return self._search(node.left,  val)   # 只需搜左子树
        else:
            return self._search(node.right, val)   # 只需搜右子树
    
    # ─────────────────────────────────────────────
    # 删除（最复杂的操作）
    # ─────────────────────────────────────────────
    def delete(self, val):
        self.root = self._delete(self.root, val)
    
    def _delete(self, node, val):
        """
        删除节点（三种情况）
        
        情况1：目标是叶节点
          → 直接删除（返回 None）
          示例：删除 4
              5          5
             / \   →    / \
            3   7      3   7
             \
              4（删除）
        
        情况2：目标只有一个子节点
          → 用唯一的子节点替代它
          示例：删除 3
              5          5
             / \   →    / \
            3   7      4   7
             \
              4（接替3的位置）
        
        情况3：目标有两个子节点（最复杂）
          → 用"中序后继"（右子树最小值）替代，再删除后继
          
          为什么用中序后继？
          中序后继是"比目标大的最小值"，
          替换后仍能保证 BST 的有序性：
          左子树全部 < 后继值 < 右子树剩余值
          
          示例：删除 5（有左子3、右子7）
          找右子树最小值 = 7（本例右子无左子，7就是最小）
              5          7
             / \   →    / \
            3   7      3   ...
        """
        if node is None:
            return None
        
        if val < node.val:
            node.left  = self._delete(node.left,  val)   # 目标在左子树
        elif val > node.val:
            node.right = self._delete(node.right, val)   # 目标在右子树
        else:
            # 找到目标节点！
            
            # 情况1 & 2：无左子，直接返回右子（可能是None）
            if node.left is None:
                return node.right
            
            # 情况2：无右子，直接返回左子
            if node.right is None:
                return node.left
            
            # 情况3：有两个子节点
            # 找右子树的最小节点（中序后继）
            successor = self._find_min(node.right)
            # 用后继的值替换当前节点（不删当前节点，改值）
            node.val = successor.val
            # 再从右子树中删除后继节点
            node.right = self._delete(node.right, successor.val)
        
        return node
    
    def _find_min(self, node):
        """找子树中的最小节点（一直向左走）"""
        while node.left:
            node = node.left
        return node
    
    def inorder(self):
        """中序遍历输出（应为升序）"""
        result = []
        def _inorder(node):
            if node:
                _inorder(node.left)
                result.append(node.val)
                _inorder(node.right)
        _inorder(self.root)
        return result


# ══ 测试 ══
bst = BST()
for v in [5, 3, 7, 1, 4, 6, 8]:
    bst.insert(v)

print(bst.inorder())    # [1, 3, 4, 5, 6, 7, 8]  ← 升序！
print(bst.search(4))    # True
print(bst.search(9))    # False

bst.delete(3)           # 删除有两个子节点的节点
print(bst.inorder())    # [1, 4, 5, 6, 7, 8]  ← 仍然有序！
```

### BST 的退化问题

```python
# 有序插入 → 退化为链表 → O(n) 操作

bst_bad = BST()
for v in [1, 2, 3, 4, 5]:   # 有序插入
    bst_bad.insert(v)

# 形状：1
#        \
#         2
#          \
#           3
#            \
#             4
#              \
#               5
# 搜索5：需要走5步 = O(n)，失去了 BST 的意义

# 解决方案：AVL 树（自动保持平衡）
```

---

## 6.6 ⭐ AVL 树（自平衡 BST）

### 为什么需要 AVL 树？

```
BST 的问题：性能依赖于树的形状
  完美平衡的树：高度 O(log n) → 操作 O(log n) ✅
  完全退化的树：高度 O(n)     → 操作 O(n)     ❌

AVL 树的承诺：任何情况下保证高度 O(log n)
实现手段：插入/删除后检查平衡，如果失衡就"旋转"恢复
```

### 平衡因子

```
平衡因子（BF）= 左子树高度 - 右子树高度

AVL 条件：每个节点的 |BF| ≤ 1，即 BF ∈ {-1, 0, 1}

示例：
      5  (BF=0)              5  (BF=2，失衡！)
     / \                    /
    3   7                  3
   (BF=0)(BF=0)           /
                          1

高度函数：空节点高度=-1，叶节点高度=0
BF = height(left_child) - height(right_child)
```

### 四种失衡情况与旋转

```
失衡类型      形状        解决方案
────────────────────────────────────────────────
LL 型        z           一次右旋
             /
            y
           /
          x

RR 型        z           一次左旋
              \
               y
                \
                 x

LR 型        z           先左旋 y，再右旋 z
             /
            y
             \
              x

RL 型        z           先右旋 y，再左旋 z
              \
               y
              /
             x
```

```python
class AVLNode:
    def __init__(self, val):
        self.val    = val
        self.left   = None
        self.right  = None
        self.height = 0       # 叶节点高度为 0


class AVLTree:
    """
    AVL 自平衡二叉搜索树
    
    所有操作保证 O(log n)，因为高度始终 O(log n)
    代价：每次插入/删除后需要检查并可能执行旋转
    """
    
    def _height(self, node):
        """空节点高度定义为 -1"""
        return node.height if node else -1
    
    def _balance_factor(self, node):
        """平衡因子 = 左高 - 右高"""
        return self._height(node.left) - self._height(node.right)
    
    def _update_height(self, node):
        """更新节点高度（子节点高度的最大值 + 1）"""
        node.height = 1 + max(self._height(node.left),
                               self._height(node.right))
    
    def _rotate_right(self, z):
        """
        右旋（解决 LL 型失衡）
        
        旋转前：        旋转后：
            z               y
           /               / \
          y          →    x   z
         /
        x
        
        操作：y 上升为新根，z 降为 y 的右子
        """
        y = z.left          # y 将成为新根
        T3 = y.right        # y 原来的右子（将成为 z 的新左子）
        
        y.right = z         # z 成为 y 的右子
        z.left  = T3        # T3 成为 z 的新左子
        
        # 先更新 z（被降级），再更新 y（新根）
        self._update_height(z)
        self._update_height(y)
        
        return y            # 返回新根
    
    def _rotate_left(self, z):
        """
        左旋（解决 RR 型失衡），与右旋对称
        
        旋转前：        旋转后：
            z               y
             \             / \
              y    →      z   x
               \
                x
        """
        y = z.right
        T2 = y.left
        
        y.left  = z
        z.right = T2
        
        self._update_height(z)
        self._update_height(y)
        
        return y
    
    def _rebalance(self, node):
        """
        检查并恢复平衡
        
        根据平衡因子判断失衡类型，选择对应旋转操作
        """
        self._update_height(node)
        bf = self._balance_factor(node)
        
        # LL 型：左边太重，且左子也左倾
        if bf > 1 and self._balance_factor(node.left) >= 0:
            return self._rotate_right(node)
        
        # LR 型：左边太重，但左子右倾
        if bf > 1 and self._balance_factor(node.left) < 0:
            node.left = self._rotate_left(node.left)   # 先左旋左子
            return self._rotate_right(node)             # 再右旋
        
        # RR 型：右边太重，且右子也右倾
        if bf < -1 and self._balance_factor(node.right) <= 0:
            return self._rotate_left(node)
        
        # RL 型：右边太重，但右子左倾
        if bf < -1 and self._balance_factor(node.right) > 0:
            node.right = self._rotate_right(node.right)  # 先右旋右子
            return self._rotate_left(node)                # 再左旋
        
        return node   # 已平衡，无需旋转
    
    def insert(self, root, val):
        """插入后自动重新平衡"""
        if root is None:
            return AVLNode(val)
        
        if val < root.val:
            root.left  = self.insert(root.left,  val)
        elif val > root.val:
            root.right = self.insert(root.right, val)
        
        return self._rebalance(root)   # 插入后检查并恢复平衡


# 演示：有序插入不再退化
avl = AVLTree()
root = None
for v in [1, 2, 3, 4, 5]:      # 有序插入（BST 会退化为链表）
    root = avl.insert(root, v)

# AVL 树维持平衡，高度约 log₂(5) ≈ 2-3，不会退化
```

---

## 6.7 ⭐ 二叉堆与优先队列

### 为什么需要优先队列？

```
场景：医院急诊，病人按病情严重程度处理，不是先来先服务

普通队列：FIFO，先来先出
优先队列：每次出队的是"优先级最高"的元素

实现优先队列的最优数据结构：二叉堆
  插入：O(log n)
  取最值：O(log n)
  建堆：O(n)
  
如果用排序数组实现：取最值 O(1)，但插入 O(n)
如果用无序数组实现：插入 O(1)，但取最值 O(n)
二叉堆两者兼顾
```

### 二叉堆的结构

```
最小堆性质：父节点的值 ≤ 任意子节点的值
           堆顶（根）= 整个堆的最小值

用数组存储完全二叉树（从索引1开始，索引0占位不用）：
          1              数组：[0, 1, 3, 5, 9, 7, 8, 6]
         / \             索引：  0  1  2  3  4  5  6  7
        3   5
       / \ / \
      9  7 8  6

索引 i 的规律：
  父节点：i // 2
  左子节点：2 * i
  右子节点：2 * i + 1

验证：索引3（值=5）的父节点 = 3//2 = 1（值=1）✅
     索引2（值=3）的子节点 = 4（值=9）和 5（值=7）✅
```

```python
class MinHeap:
    """
    最小堆（数组实现）
    
    核心操作：
    - insert（插入）：加到末尾，然后上浮（sift up）
    - delete_min（删除最小）：取堆顶，末尾补位，然后下沉（sift down）
    """
    
    def __init__(self):
        self._heap = [0]   # 索引0不用，实际数据从索引1开始
    
    @property
    def size(self):
        return len(self._heap) - 1
    
    def insert(self, val):
        """
        插入：末尾追加，然后上浮恢复堆性质
        
        执行流程（向堆 [1,3,5,9,7,8,6] 插入 2）：
        
        追加到末尾：[1, 3, 5, 9, 7, 8, 6, 2]（2在索引7）
        
        上浮过程：
        i=7，父=i//2=3，heap[3]=5，2<5 → 交换
        [1, 3, 2, 9, 7, 8, 6, 5]（2在索引3）
        
        i=3，父=i//2=1，heap[1]=1，2>1 → 停止！
        
        最终堆：[1, 3, 2, 9, 7, 8, 6, 5]
        仍满足堆性质 ✅
        """
        self._heap.append(val)      # 加到末尾
        self._sift_up(self.size)    # 从末尾开始上浮
    
    def _sift_up(self, i):
        """上浮：将索引 i 的元素向上移到正确位置"""
        while i > 1:                         # 还没到根
            parent = i // 2
            if self._heap[i] < self._heap[parent]:
                # 比父节点小，交换（上浮）
                self._heap[i], self._heap[parent] = \
                    self._heap[parent], self._heap[i]
                i = parent
            else:
                break                        # 已满足堆性质，停止
    
    def delete_min(self):
        """
        删除并返回最小值（堆顶）
        
        执行流程（堆 [1, 3, 2, 9, 7, 8, 6]）：
        
        取堆顶：min_val = 1
        末尾补位：把 6（末尾）移到堆顶
        [6, 3, 2, 9, 7, 8]（索引1=6）
        
        下沉过程：
        i=1（值=6），左子=2（值=3），右子=3（值=2）
        较小子=3（值=2），6>2 → 交换
        [2, 3, 6, 9, 7, 8]（6在索引3）
        
        i=3（值=6），左子=6（越界），右子=7（越界）
        无子节点，停止
        
        返回 1 ✅
        """
        if self.size == 0:
            raise IndexError("heap is empty")
        
        min_val = self._heap[1]              # 堆顶 = 最小值
        self._heap[1] = self._heap.pop()     # 末尾元素移到堆顶
        
        if self.size > 0:
            self._sift_down(1)               # 从堆顶开始下沉
        
        return min_val
    
    def _sift_down(self, i):
        """下沉：将索引 i 的元素向下移到正确位置"""
        n = self.size
        while 2 * i <= n:                   # 至少有左子节点
            left  = 2 * i
            right = 2 * i + 1
            
            # 找较小的子节点
            smallest = left
            if right <= n and self._heap[right] < self._heap[left]:
                smallest = right
            
            if self._heap[i] > self._heap[smallest]:
                # 比较小的子节点大，交换（下沉）
                self._heap[i], self._heap[smallest] = \
                    self._heap[smallest], self._heap[i]
                i = smallest
            else:
                break                        # 已满足堆性质，停止
    
    def peek(self):
        """查看最小值但不删除"""
        if self.size == 0:
            raise IndexError("heap is empty")
        return self._heap[1]


# ══ Python 内置 heapq 模块（生产使用）══
import heapq

# heapq 实现最小堆，索引从0开始
heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 1)
heapq.heappush(heap, 3)

print(heapq.heappop(heap))   # 1（最小值）
print(heapq.heappop(heap))   # 3

# 最大堆：取负值插入（Python heapq 只有最小堆）
max_heap = []
for v in [1, 5, 3, 8, 2]:
    heapq.heappush(max_heap, -v)   # 存负值

print(-heapq.heappop(max_heap))   # 8（最大值）

# O(n) 建堆（比逐个插入的 O(n log n) 更快）
data = [5, 3, 8, 1, 4]
heapq.heapify(data)               # 原地建堆，O(n)
print(data[0])                    # 1（堆顶=最小值）
```

---

## 6.8 ⭐【面试题实战】

### 面试题1：二叉树的最大深度（LeetCode 104，Easy）

**题目**：给定二叉树根节点，返回其最大深度（根到最远叶节点的层数）。

```python
def max_depth(root):
    """
    递归解法（后序遍历思想）
    
    关键洞察：
    树的最大深度 = max(左子树深度, 右子树深度) + 1
    空树深度 = 0
    
    这是一个典型的"分治"结构：
    不需要知道左右子树内部结构，只需要它们各自返回深度
    
    时间：O(n)，遍历每个节点一次
    空间：O(h)，h 为树高（递归栈深度）
    """
    if root is None:       # 基本情况：空树深度为 0
        return 0
    
    left_depth  = max_depth(root.left)    # 递归求左子树深度
    right_depth = max_depth(root.right)   # 递归求右子树深度
    
    # 当前节点的深度 = 左右子树最大深度 + 1（加上当前节点这一层）
    return max(left_depth, right_depth) + 1


# 执行流程（树：1-2-4, 1-2-5, 1-3）：
# max_depth(1)
#   left  = max_depth(2)
#             left  = max_depth(4) → 0+1=1（4是叶节点）
#             right = max_depth(5) → 0+1=1
#             return max(1,1)+1=2
#   right = max_depth(3) → 0+1=1
#   return max(2,1)+1=3  ✅

tree = build_tree([1, 2, 3, 4, 5])
print(max_depth(tree))   # 3
```

---

### 面试题2：对称二叉树（LeetCode 101，Easy）

**题目**：判断一棵二叉树是否轴对称（镜像对称）。

```python
def is_symmetric(root):
    """
    递归判断是否镜像对称
    
    关键洞察：
    对称 ≠ 左子树等于右子树
    而是：左子树是右子树的"镜像"
    
    镜像的定义（递归）：
    两棵树 p 和 q 互为镜像，当且仅当：
    1. p.val == q.val
    2. p.left 是 q.right 的镜像
    3. p.right 是 q.left 的镜像
    
    时间：O(n)，空间：O(h)
    """
    def is_mirror(p, q):
        # 两者都为空：对称
        if p is None and q is None:
            return True
        # 一个为空一个不为空：不对称
        if p is None or q is None:
            return False
        # 值不同：不对称
        if p.val != q.val:
            return False
        
        # 递归检查：外侧和内侧是否都对称
        return is_mirror(p.left, q.right) and \
               is_mirror(p.right, q.left)
    
    return is_mirror(root.left, root.right)


#     1
#    / \
#   2   2    ← 对称
#  / \ / \
# 3  4 4  3

tree = build_tree([1, 2, 2, 3, 4, 4, 3])
print(is_symmetric(tree))   # True

tree2 = build_tree([1, 2, 2, None, 3, None, 3])
print(is_symmetric(tree2))  # False
```

---

### 面试题3：二叉树的层序遍历（LeetCode 102，Medium）

**题目**：返回二叉树的层序遍历结果（每层的节点值列表）。

```python
def level_order_traversal(root):
    """
    BFS 层序遍历，按层分组输出
    
    核心技巧：在处理每一层时，先记录当前队列长度
    该长度就是当前层的节点数，处理完这些节点就是一层结束
    
    执行流程（树：1-2-3-4-5）：
    
    初始：queue=[1]
    
    第1轮（第0层）：
      level_size=1，处理节点1
      节点1：加入2,3到队列
      result=[[1]]，queue=[2,3]
    
    第2轮（第1层）：
      level_size=2，处理节点2,3
      节点2：加入4,5；节点3：无子
      result=[[1],[2,3]]，queue=[4,5]
    
    第3轮（第2层）：
      level_size=2，处理节点4,5（无子）
      result=[[1],[2,3],[4,5]]，queue=[]
    
    时间：O(n)，空间：O(n)（队列最大存一层）
    """
    if not root:
        return []
    
    result = []
    queue  = deque([root])
    
    while queue:
        level_size = len(queue)    # 关键：当前层节点数
        level_vals = []
        
        for _ in range(level_size):
            node = queue.popleft()
            level_vals.append(node.val)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        result.append(level_vals)
    
    return result


tree = build_tree([3, 9, 20, None, None, 15, 7])
print(level_order_traversal(tree))   # [[3], [9, 20], [15, 7]]
```

> **⭐ 层序遍历的模板非常通用**，以下问题都基于它：
> - 二叉树的右视图（每层最后一个节点）
> - 二叉树的锯齿形遍历（奇数层从左到右，偶数层从右到左）
> - 二叉树的最小深度（找到第一个叶节点所在层）

---

### 面试题4：验证二叉搜索树（LeetCode 98，Medium）

**题目**：判断给定的二叉树是否是合法的 BST。

**常见错误思路**：只检查每个节点是否 `node.left.val < node.val < node.right.val`，这是错的！

```
反例：
     5
    / \
   1   4     ← 4 < 5，看似符合
      / \
     3   6   ← 3 < 5（根），但 3 在根的右子树，应该 > 5，违反 BST！

仅检查父子关系会漏掉跨层级的约束。
```

```python
def is_valid_bst(root):
    """
    正确方案：传递上下界约束
    
    对每个节点，它的值必须在 (min_val, max_val) 范围内：
    - 根节点：(-∞, +∞)
    - 左子节点：(-∞, 父节点值)  （左子必须比父小）
    - 右子节点：(父节点值, +∞)  （右子必须比父大）
    
    执行流程（检查树：5-1-4-3-6）：
    
    _validate(5, -∞, +∞)：5在范围内，继续
      _validate(1, -∞, 5)：1在范围内，继续
        _validate(None, -∞, 1)：空，返回True
        _validate(None, 1, 5)：空，返回True
      _validate(4, 5, +∞)：4 < 5（下界），返回False！❌
    
    返回 False ✅
    
    时间：O(n)，空间：O(h)
    """
    def _validate(node, min_val, max_val):
        if node is None:
            return True   # 空节点合法
        
        # 当前节点值必须严格在 (min_val, max_val) 范围内
        if node.val <= min_val or node.val >= max_val:
            return False
        
        # 左子树：上界更新为当前值；右子树：下界更新为当前值
        return (_validate(node.left,  min_val, node.val) and
                _validate(node.right, node.val, max_val))
    
    return _validate(root, float('-inf'), float('inf'))


# 另一种思路：中序遍历应为严格递增序列
def is_valid_bst_inorder(root):
    """
    中序遍历方案：BST 中序 = 升序，检查是否严格递增
    
    用 prev 记录上一个访问的节点值，
    若当前节点 ≤ prev，说明不是严格递增，BST 不合法
    """
    prev = [float('-inf')]   # 用列表存以便在嵌套函数中修改
    
    def inorder(node):
        if node is None:
            return True
        if not inorder(node.left):
            return False
        if node.val <= prev[0]:    # 当前值必须严格大于前一个
            return False
        prev[0] = node.val
        return inorder(node.right)
    
    return inorder(root)


tree_valid = build_tree([2, 1, 3])
tree_invalid = build_tree([5, 1, 4, None, None, 3, 6])
print(is_valid_bst(tree_valid))    # True
print(is_valid_bst(tree_invalid))  # False
```

---

### 面试题5：二叉树的最近公共祖先（LeetCode 236，Medium）

**题目**：给定二叉树的两个节点 p 和 q，找到它们的最近公共祖先（LCA）。

**LCA 定义**：节点 v 是 p 和 q 的 LCA，当且仅当 v 是 p 和 q 的祖先，且不存在比 v 更低的公共祖先。（一个节点也可以是自身的祖先）

```python
def lowest_common_ancestor(root, p, q):
    """
    LCA 递归解法
    
    关键洞察（分三种情况讨论）：
    
    情况1：当前节点是 p 或 q
      → 直接返回当前节点
      （另一个节点一定在当前节点的子树里，当前节点就是LCA）
    
    情况2：p 和 q 分别在左右子树
      → 当前节点就是 LCA（唯一一个"分叉点"）
      （左递归返回非None，右递归也返回非None → 当前节点是LCA）
    
    情况3：p 和 q 都在同侧子树
      → LCA 在那一侧子树里
      （左递归返回None，右递归返回非None → LCA在右子树，反之亦然）
    
    执行流程（树：3-5-1-6-2-0-8, p=5, q=1）：
    
    lca(3, 5, 1)
      left  = lca(5, 5, 1)  → 5==p，返回 Node(5)
      right = lca(1, 5, 1)  → 1==q，返回 Node(1)
      left非None，right非None → 当前节点3是LCA！返回 Node(3)
    
    时间：O(n)，空间：O(h)
    """
    # 基本情况
    if root is None:
        return None
    if root is p or root is q:   # 找到其中一个目标
        return root
    
    # 分别在左右子树中搜索
    left  = lowest_common_ancestor(root.left,  p, q)
    right = lowest_common_ancestor(root.right, p, q)
    
    # 左右都找到了 → 当前节点是分叉点，即 LCA
    if left and right:
        return root
    
    # 只有一侧找到了 → LCA 在那一侧
    return left if left else right


# 构建测试树：3-5-1-6-2-0-8-None-None-7
#         3
#        / \
#       5   1
#      / \ / \
#     6  2 0  8
#       / \
#      7   4

root = TreeNode(3)
n5 = TreeNode(5); n1 = TreeNode(1)
root.left = n5; root.right = n1
n6 = TreeNode(6); n2 = TreeNode(2)
n5.left = n6; n5.right = n2
n0 = TreeNode(0); n8 = TreeNode(8)
n1.left = n0; n1.right = n8
n7 = TreeNode(7); n4 = TreeNode(4)
n2.left = n7; n2.right = n4

# p=5, q=1 → LCA = 3（根）
result = lowest_common_ancestor(root, n5, n1)
print(result.val)   # 3

# p=5, q=4 → LCA = 5（p本身是祖先）
result2 = lowest_common_ancestor(root, n5, n4)
print(result2.val)  # 5
```

> **⚠️ 面试注意点**：
> 1. 比较节点要用 `is`（引用相等），不要用 `==`（值相等）
> 2. "一个节点可以是自身的祖先"这个条件很关键，影响了情况1的处理
> 3. 代码中 `if left and right: return root` 这一行是整个算法的核心，要能清楚解释为什么

---

## 6.9 本章要点总结

### 核心概念映射表

| 概念 | 定义 | 关键特征 | 主要应用 |
|------|------|----------|---------|
| **二叉树** | 每节点最多两个子节点 | 递归结构，遍历是基础 | 所有树形问题的基础 |
| **前序遍历** | 根→左→右 | 根最先访问 | 树的复制、序列化 |
| **中序遍历** | 左→根→右 | BST中序=升序 ⭐ | BST排序输出、验证BST |
| **后序遍历** | 左→右→根 | 根最后访问 | 树的删除、表达式求值 |
| **层序遍历** | BFS按层 | 用队列实现 | 求高度、BFS类问题 |
| **BST** | 左<根<右（递归） | 中序有序，O(log n) | 有序存储、快速查找 |
| **AVL树** | 自平衡BST | |BF|≤1，旋转恢复 | 保证O(log n)最坏情况 |
| **最小堆** | 父≤子（完全二叉树） | 堆顶=最小值 | 优先队列、TopK问题 |

### 遍历方法速查

| 遍历 | 顺序 | 实现核心 | 记忆技巧 |
|------|------|---------|---------|
| 前序 | **根**→左→右 | 先 append(root.val) | 根在"前" |
| 中序 | 左→**根**→右 | 递归左，append，递归右 | 根在"中" |
| 后序 | 左→右→**根** | 最后 append(root.val) | 根在"后" |
| 层序 | 按层 BFS | deque，记录层大小 | 队列=宽度优先 |

### BST 操作复杂度

| 操作 | 平均（平衡树） | 最坏（退化链表） | AVL 树最坏 |
|------|--------------|----------------|-----------|
| 搜索 | O(log n) | O(n) | **O(log n)** |
| 插入 | O(log n) | O(n) | **O(log n)** |
| 删除 | O(log n) | O(n) | **O(log n)** |

### 面试高频考点

| 题目 | 核心思路 | 时间 | 空间 | 难度 |
|------|---------|------|------|------|
| 最大深度 LC104 | 后序：max(左深度, 右深度)+1 | O(n) | O(h) | Easy |
| 对称二叉树 LC101 | 镜像递归：左左=右右，左右=右左 | O(n) | O(h) | Easy |
| 层序遍历 LC102 | BFS + 记录每层大小 | O(n) | O(n) | Medium |
| 验证BST LC98 | 传上下界约束，或中序判断严格递增 | O(n) | O(h) | Medium |
| 最近公共祖先 LC236 | 分三种情况，左右都找到则当前节点是LCA | O(n) | O(h) | Medium |

### 常见陷阱（坑点）

| 陷阱 | 说明 | 解决方法 |
|------|------|---------|
| 验证 BST 只看父子 | 忽略了跨层级约束 | 传入上下界参数 |
| LCA 用 `==` 比较 | 值相同≠同一节点 | 用 `is` 比较引用 |
| 层序不记层大小 | 无法分层输出 | 先 `level_size=len(queue)` |
| 堆索引从0开始 | 手写堆时父子索引公式变了 | 统一从1开始，0占位 |
| BST 删除漏情况 | 遗漏"有两个子节点"的情况 | 分三种情况明确讨论 |
| 递归树遍历忘判空 | `None.val` 直接报错 | 第一行必须 `if root is None: return` |

### 工具速查

```python
# 层序遍历 / BFS 模板
from collections import deque
queue = deque([root])
while queue:
    node = queue.popleft()
    if node.left:  queue.append(node.left)
    if node.right: queue.append(node.right)

# 按层分组模板（多一步记录层大小）
while queue:
    for _ in range(len(queue)):   # 关键：处理完整一层
        node = queue.popleft()
        ...

# Python 最小堆
import heapq
heapq.heappush(heap, val)
heapq.heappop(heap)      # 弹出最小值
heap[0]                  # 查看最小值（不删除）
heapq.heapify(lst)       # O(n) 原地建堆

# Python 最大堆（取负值）
heapq.heappush(heap, -val)
-heapq.heappop(heap)     # 弹出最大值
```

---

> **给初学者的学习建议**：
> 1. **四种遍历先背模板**，然后各找一道 LeetCode 题实战（104、94、145、102），每种遍历的应用场景会在做题中自然理解。
> 2. **BST 的删除是难点**，三种情况要分清楚。遇到"有两个子节点"时，用"中序后继替代"的思路最清晰，不容易出错。
> 3. **验证 BST 的错误思路（只看父子）是经典陷阱**，面试时要主动指出正确做法（传上下界），展示你对 BST 性质的深刻理解。
> 4. **实际开发中直接用 `heapq`**，面试时能描述堆的原理（上浮/下沉）即可，不需要手写完整实现。
