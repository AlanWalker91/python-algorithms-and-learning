# 第6章：树

> **核心思路**：树是链表的"升维"——从线性（一对一）扩展到层级（一对多）。掌握树遍历的三种方式，理解BST的有序性，理解AVL树如何用旋转维持平衡。

---

## 6.1 树的基本概念

```
          A           ← 根节点（Root）
        /   \
       B     C        ← 内部节点（Internal Node）
      / \     \
     D   E     F     ← 叶节点（Leaf，没有子节点）
```

### 核心术语

| 术语 | 定义 | 例子（上图）|
|------|------|-----------|
| 根（Root） | 没有父节点的节点 | A |
| 叶（Leaf） | 没有子节点的节点 | D, E, F |
| 边（Edge） | 连接父子节点的线 | A-B, A-C... |
| 层（Level） | 根为第0层，向下递增 | A=0层, D=2层 |
| 高度（Height） | 根到最远叶的边数 | 2 |
| 深度（Depth） | 某节点到根的边数 | F的深度=2 |

### 二叉树

**二叉树**：每个节点最多有两个子节点（左子 / 右子）。

```python
class BinaryTreeNode:
    """
    二叉树节点
    每个节点包含：数据 + 左子指针 + 右子指针
    """
    def __init__(self, val):
        self.val   = val
        self.left  = None   # 左子节点
        self.right = None   # 右子节点

# 手动构建上图的树
root = BinaryTreeNode('A')
root.left  = BinaryTreeNode('B')
root.right = BinaryTreeNode('C')
root.left.left   = BinaryTreeNode('D')
root.left.right  = BinaryTreeNode('E')
root.right.right = BinaryTreeNode('F')
```

---

## 6.2 ⭐ 树的遍历（三种顺序）

遍历 = 访问树中每个节点恰好一次。顺序不同，应用场景不同。

```python
# 三种遍历用同一棵树演示：
#       1
#      / \
#     2   3
#    / \
#   4   5
```

### 前序遍历（Pre-order）：根 → 左 → 右

```python
def preorder(node):
    """
    前序遍历：先处理根，再递归处理子树
    
    用途：复制树结构、打印目录结构（父目录在子目录之前）
    
    输出：1 2 4 5 3（根最先出现）
    """
    if node is None:
        return
    print(node.val, end=' ')  # ① 访问根
    preorder(node.left)       # ② 遍历左子树
    preorder(node.right)      # ③ 遍历右子树
```

### 中序遍历（In-order）：左 → 根 → 右

```python
def inorder(node):
    """
    中序遍历：先左子树，再根，再右子树
    
    ⭐ 关键性质：对二叉搜索树做中序遍历，得到升序序列！
    
    用途：BST排序输出、验证BST有效性
    
    输出：4 2 5 1 3
    """
    if node is None:
        return
    inorder(node.left)        # ① 遍历左子树
    print(node.val, end=' ')  # ② 访问根
    inorder(node.right)       # ③ 遍历右子树
```

### 后序遍历（Post-order）：左 → 右 → 根

```python
def postorder(node):
    """
    后序遍历：先处理所有子节点，再处理根
    
    用途：删除树（先删子节点再删父节点）、
         计算表达式树的值（先算子表达式）
    
    输出：4 5 2 3 1（根最后出现）
    """
    if node is None:
        return
    postorder(node.left)      # ① 遍历左子树
    postorder(node.right)     # ② 遍历右子树
    print(node.val, end=' ')  # ③ 访问根
```

### 层序遍历（Level-order / BFS）

```python
from collections import deque

def level_order(root):
    """
    层序遍历：按层从上到下，每层从左到右
    
    实现：用队列（FIFO）—— 把当前节点的子节点入队，
          按入队顺序出队就是按层顺序
    
    输出：1 2 3 4 5
    """
    if root is None:
        return
    
    q = deque([root])
    
    while q:
        node = q.popleft()              # 出队并访问
        print(node.val, end=' ')
        
        if node.left:
            q.append(node.left)         # 左子入队
        if node.right:
            q.append(node.right)        # 右子入队
```

---

## 6.3 ⭐ 二叉搜索树（BST）

### 核心性质（BST 不变式）

```
对树中每个节点 N：
  - N.left 子树中所有节点的值 < N.val
  - N.right 子树中所有节点的值 > N.val
  - 左右子树也分别满足BST性质
```

**这个性质保证：中序遍历BST = 升序序列**

### BST 完整实现

```python
class BST:
    """
    二叉搜索树
    
    核心操作复杂度（平均）：
    - 插入：O(log n)
    - 搜索：O(log n)
    - 删除：O(log n)
    
    ⚠️ 最坏情况（数据有序插入）：退化为链表，O(n)
    """
    
    def __init__(self):
        self.root = None
    
    # ---- 插入 ----
    def insert(self, val):
        self.root = self._insert(self.root, val)
    
    def _insert(self, node, val):
        """
        递归插入
        
        比根小 → 插入左子树
        比根大 → 插入右子树
        到达空节点 → 创建新节点
        """
        if node is None:
            return BinaryTreeNode(val)   # 找到空位，创建节点
        
        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        # val == node.val：BST通常不存储重复值，忽略
        
        return node
    
    # ---- 搜索 ----
    def search(self, val):
        return self._search(self.root, val)
    
    def _search(self, node, val):
        """
        递归搜索：每次比较排除一半
        """
        if node is None:
            return False           # 到达空节点，未找到
        if val == node.val:
            return True            # 找到！
        elif val < node.val:
            return self._search(node.left, val)   # 去左子树找
        else:
            return self._search(node.right, val)  # 去右子树找
    
    # ---- 删除（最复杂的操作）----
    def delete(self, val):
        self.root = self._delete(self.root, val)
    
    def _delete(self, node, val):
        """
        删除节点，分三种情况：
        
        情况1：目标是叶节点 → 直接删除（返回None）
        情况2：目标有一个子节点 → 用子节点替代它
        情况3：目标有两个子节点 → 用右子树的最小值替代，
               然后删除右子树中的那个最小值
        """
        if node is None:
            return None
        
        if val < node.val:
            node.left = self._delete(node.left, val)
        elif val > node.val:
            node.right = self._delete(node.right, val)
        else:
            # 找到目标节点
            if node.left is None:
                return node.right  # 情况1 & 2：无左子，用右子替代
            elif node.right is None:
                return node.left   # 情况2：无右子，用左子替代
            
            # 情况3：有两个子节点
            # 找右子树的最小值（中序后继）
            successor = self._find_min(node.right)
            node.val = successor.val               # 值替换
            node.right = self._delete(node.right, successor.val)  # 删除后继
        
        return node
    
    def _find_min(self, node):
        """找子树中的最小节点（一直向左走）"""
        while node.left:
            node = node.left
        return node
    
    # ---- 中序输出（验证有序性）----
    def inorder_list(self):
        result = []
        self._inorder(self.root, result)
        return result
    
    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.val)
            self._inorder(node.right, result)

# 测试
bst = BST()
for v in [5, 3, 7, 1, 4, 6, 8]:
    bst.insert(v)

print(bst.inorder_list())   # [1, 3, 4, 5, 6, 7, 8] ← 自动有序！
print(bst.search(4))        # True
bst.delete(3)
print(bst.inorder_list())   # [1, 4, 5, 6, 7, 8]
```

---

## 6.4 ⭐ AVL树（自平衡BST）

### 问题：BST 的退化

```python
# 按有序序列插入 → BST 退化为链表
bst2 = BST()
for v in [1, 2, 3, 4, 5]:
    bst2.insert(v)
# 形状：1 → 2 → 3 → 4 → 5（右倾链表）
# 搜索复杂度退化为 O(n)！
```

### AVL树的解决方案

**平衡因子**（Balance Factor）：`左子树高度 - 右子树高度`

```
平衡条件：每个节点的平衡因子必须在 {-1, 0, 1} 之间
若失衡（|BF| > 1）→ 执行旋转操作恢复平衡
```

### 四种旋转操作

```python
# ---- 右旋（解决左-左不平衡）----
#
#     C          B
#    /    →    /   \
#   B          A     C
#  /
# A
#
def rotate_right(node):
    """
    右旋：node 的左子节点上升成为新根
    """
    new_root = node.left
    node.left = new_root.right   # 新根的右子变成 node 的左子
    new_root.right = node        # node 变成新根的右子
    
    # 更新高度（先更新被降级的节点）
    node.height = 1 + max(height(node.left), height(node.right))
    new_root.height = 1 + max(height(new_root.left), height(new_root.right))
    
    return new_root

# ---- 左旋（解决右-右不平衡）----
def rotate_left(node):
    """左旋：与右旋对称"""
    new_root = node.right
    node.right = new_root.left
    new_root.left = node
    
    node.height = 1 + max(height(node.left), height(node.right))
    new_root.height = 1 + max(height(new_root.left), height(new_root.right))
    
    return new_root

# 四种不平衡情况：
# LL型 → 一次右旋
# RR型 → 一次左旋
# LR型 → 先左旋左子，再右旋（双旋）
# RL型 → 先右旋右子，再左旋（双旋）
```

---

## 6.5 ⭐ 二叉堆（Binary Heap / 优先队列）

**核心特性**：
- **结构性质**：完全二叉树（从左到右填满）
- **堆性质（最小堆）**：父节点 ≤ 子节点（根是最小值）

```python
class MinHeap:
    """
    最小堆（用列表实现）
    
    ⭐ 关键技巧：用列表存储完全二叉树
    - 索引 i 的左子节点：2*i
    - 索引 i 的右子节点：2*i + 1
    - 索引 i 的父节点：i // 2
    （索引从1开始，0位置占位不用）
    """
    
    def __init__(self):
        self.heap = [0]    # [0] 是占位，实际数据从索引1开始
    
    def insert(self, val):
        """
        插入：先加到末尾，再上浮（sift up）
        保持堆性质：若比父节点小，就与父节点交换
        """
        self.heap.append(val)
        i = len(self.heap) - 1
        
        # 上浮：与父节点比较，若更小则交换
        while i > 1 and self.heap[i] < self.heap[i // 2]:
            self.heap[i], self.heap[i // 2] = self.heap[i // 2], self.heap[i]
            i = i // 2
    
    def delete_min(self):
        """
        删除最小值（根）：
        1. 把最后一个元素移到根
        2. 下沉（sift down）：与较小的子节点交换，恢复堆性质
        """
        if len(self.heap) == 1:
            return None
        
        min_val = self.heap[1]               # 根 = 最小值
        self.heap[1] = self.heap.pop()       # 末尾元素移到根
        
        self._sift_down(1)
        return min_val
    
    def _sift_down(self, i):
        """下沉：把位置i的元素向下移到正确位置"""
        n = len(self.heap)
        while 2 * i < n:                     # 至少有左子节点
            left, right = 2 * i, 2 * i + 1
            
            # 找较小的子节点
            smaller = left
            if right < n and self.heap[right] < self.heap[left]:
                smaller = right
            
            # 如果当前节点已经不大于子节点，停止
            if self.heap[i] <= self.heap[smaller]:
                break
            
            self.heap[i], self.heap[smaller] = self.heap[smaller], self.heap[i]
            i = smaller

# 测试
heap = MinHeap()
for v in [5, 3, 8, 1, 4]:
    heap.insert(v)

print(heap.delete_min())   # 1（最小值）
print(heap.delete_min())   # 3
print(heap.delete_min())   # 4
```

### 堆的应用：优先队列

```python
import heapq   # Python 内置堆模块（最小堆）

# 优先队列：任务调度
tasks = [(3, '低优先级任务'), (1, '紧急任务'), (2, '普通任务')]
heapq.heapify(tasks)   # O(n) 建堆

while tasks:
    priority, name = heapq.heappop(tasks)   # O(log n) 弹出最小
    print(f"执行[优先级{priority}]：{name}")
# 输出按优先级从小到大
```

---

## 6.6 本章要点总结

| 概念 | 要点 |
|------|------|
| **三种遍历** | 前序=根先；中序=根中间（BST中序=有序）；后序=根最后 |
| **层序遍历** | 用队列实现；BFS的基础 |
| **⭐ BST** | 左小右大；中序有序；平均O(log n) |
| **BST删除** | 有两个子节点时用中序后继替代，是难点 |
| **⭐ AVL树** | 平衡因子保持[-1,0,1]；旋转恢复平衡；所有操作O(log n) |
| **最小堆** | 父≤子；根=最小值；insert和deleteMin都是O(log n) |

> **给初学者的建议**：
> 1. 三种遍历必须能**默写**，记忆方法：前/中/后 = 根的访问时机在左右的前/中/后。
> 2. BST 插入和搜索用递归写最清晰，先掌握这两个，删除最复杂放最后。
> 3. 实际使用 Python 的 `heapq` 模块而非手写堆；面试时理解原理即可。
