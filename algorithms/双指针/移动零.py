# 给定一个数组 nums，编写一个函数将所有 0 移动到数组的末尾，同时保持非零元素的相对顺序。
# 请注意 ，必须在不复制数组的情况下原地对数组进行操作。
# 输入: nums = [0,1,0,3,12]
# 输出: [1,3,12,0,0]

def moveZeroes(nums):
    slow = 0
    for fast in len(nums):
        if nums[fast] != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1
# 核心思想：用一个指针记录“下一个非零元素应该放的位置”
# 设两个指针：
# fast：遍历数组
# slow：指向下一个应该放非零元素的位置



# 举一反三练习
# 练习 1（简单）：移动所有指定值到末尾
# 把数组中所有值为 val 的元素移到末尾，其余顺序不变。比如 nums = [3,1,3,2,3,5], val = 3 → [1,2,5,3,3,3]
# 提示：和上面几乎一样，只是判断条件从 != 0 变成 != val
def moveTarget(nums, val):
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != val:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1

# 练习 2（中等）：把奇数移到前面，偶数移到后面
# nums = [2,4,1,3,6,5] → [1,3,5,2,4,6]（奇数在前且保持相对顺序）
# 提示：分两轮，第一轮把奇数移到前面，第二轮把偶数填到后面

def moveOddEven(nums):
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] % 2 != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1





