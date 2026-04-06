# 给定一个未排序的整数数组 nums ，找出数字连续的最长序列（不要求序列元素在原数组中连续）的长度。
# 请你设计并实现时间复杂度为 O(n) 的算法解决此问题。
# 输入：nums = [100,4,200,1,3,2]
# 输出：4
# 解释：最长数字连续序列是 [1, 2, 3, 4]。它的长度为 4。

def longestConsecutive(nums):
    num_set = set(nums)  # O(n) 建集合，去重 + O(1) 查找
    longest = 0

    for num in num_set:
        # 只从起点开始计数
        if num - 1 not in num_set:
            current = num
            length = 1

            # 往后一个一个找
            while current + 1 in num_set:
                current += 1
                length += 1

            longest = max(longest, length)
    return longest

# 这道题的核心模式是 Set + 只从边界出发遍历，你可以尝试：
# 练习：找出数组中最长连续递增偶数序列的长度
# 给定 [2, 4, 6, 3, 8, 10, 12, 14]，只看偶数，找连续偶数序列（差值为2），最长是 [8, 10, 12, 14]，长度为 4。
# 提示：先筛出偶数放入 set，然后起点条件变为 num - 2 not in num_set，往后找变为 current + 2。
def longlist(nums):
    # 第一步：筛出偶数放入 set
    num_set = set()
    for num in nums:
        if num % 2 == 0:          # 取余判断偶数
            num_set.add(num)
    # 第二步：从起点出发，往后找
    max_length = 0
    for i in num_set:
        if i - 2 not in num_set:  # 起点判断：前面没有连续偶数了
            current = i
            length = 1

            while current + 2 in num_set:  # 往后持续找
                current += 2
                length += 1
            max_length = max(max_length, length)
    return max_length

# 举一反三练习
# 练习：找出字符串中最长连续字母子序列的长度
# 给定 "abcfghijzxy"，找出字母表中连续的最长序列。比如 fghij 对应 ASCII 连续，长度为 5。
# 提示：把每个字符转成 ASCII 码（ord(c)），放入 set，然后套用完全相同的模式，起点条件是 ord(c) - 1 not in char_set。

def longestStr(strs):
    str_set = set()
    longest = 0

    for st in strs:
        str_set.add(ord(st))

    for i in str_set:
        if i - 1 not in str_set:
            current = i
            current_length = 1

            while current + 1 in str_set:
                current += 1
                current_length += 1

            longest = max(longest, current_length)
    return longest
#方法总结：每道题只是三个地方不同：数据怎么预处理、起点条件是什么、步长是多少。模式本身不变。
def findLongestConsecutive(data):
    data_set = set(处理后的数据)
    longest = 0
    for item in data_set:
        if 前一个元素 not in data_set:      # 起点判断
            current = item
            length = 1
            while 下一个元素 in data_set:    # 往后延伸
                current += 步长
                length += 1
            longest = max(longest, length)
    return longest