# 给你一个字符串数组，请你将 字母异位词 组合在一起。可以按任意顺序返回结果列表。
# 输入: strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
# 输出: [["bat"],["nat","tan"],["ate","eat","tea"]]

# 核心思路
# 字母异位词的本质是：两个字符串包含的字符种类和数量完全相同，只是排列顺序不同。
# 那么把它们各自排序后，得到的结果一定相同。利用这个性质作为"分组依据"。

from collections import defaultdict

def groupAnagrams(strs):
    # 1. 创建一个默认值为 list 的字典
    #    好处：访问不存在的 key 时自动创建空列表，省去 if 判断
    groups = defaultdict(list)

    # 2. 遍历每个字符串
    for s in strs:
        # 3. 排序后转成 tuple 作为字典的 key
        #    "eat" -> sorted -> ['a','e','t'] -> tuple -> ('a','e','t')
        #    "tea" -> sorted -> ['a','e','t'] -> tuple -> ('a','e','t')
        #    两者 key 相同，会被归到同一组
        key = tuple(sorted(s))

        # 4. 把原始字符串追加到对应的组里
        groups[key].append(s)

    # 5. 返回所有分组
    return list(groups.values())

# 练习 1：按字符串长度分组（简单）
# 给定 ["hi", "abc", "ok", "hello", "def", "go"]，按长度分组，输出：
# [[\"hi\", \"ok\", \"go\"], [\"abc\", \"def\"], [\"hello\"]]

def groupByLength(nums):
    groups = defaultdict(list)

    for num in nums:
        key = len(num)
        groups[key].append(num)

    return list(groups.values())
nums = ["hi", "abc", "ok", "hello", "def", "go"]

print(groupByLength(nums))

# 练习 3：按数字的各位数字之和分组（中等）
# 给定 [12, 21, 33, 42, 15, 51]，按各位数字之和分组：
# 数字和为3: [12, 21]
# 数字和为6: [33, 42, 15, 51]
nums1 = [12, 21, 33, 42, 15, 51]
def groupBySum(nums1):
    groups = defaultdict(list)

    for num in nums1:
        key = sum(int(d) for d in str(num))
        groups[key].append(num)

    return list(groups.values())

print(groupBySum(nums1))

# 练习 2：找出数组中所有异位词对的数量（中等）
# 给定 ["abc","bca","cab","xyz","zyx"]，返回异位词对的数量。上例中 abc/bca, abc/cab, bca/cab, xyz/zyx 共 4 对。
# 提示：先分组，每组有 n 个元素，能组成 n*(n-1)/2 对
def countAnagramPairs(strs):
    groups = defaultdict(list)

    for s in strs:
        key = tuple(sorted(s))
        groups[key].append(s)

    count = 0
    for group in groups.values():
        n = len(group)
        count += n * (n - 1) // 2

    return count

# 这个模式非常常见，分组之后的"统计"可以是各种操作：计数、求最大值、求平均值等等。