# 给你一个整数数组 nums ，判断是否存在三元组 [nums[i], nums[j], nums[k]] 满足 i != j、i != k 且 j != k ，
# 同时还满足 nums[i] + nums[j] + nums[k] == 0 。请你返回所有和为 0 且不重复的三元组。
# 注意：答案中不可以包含重复的三元组。
# 输入：nums = [-1,0,1,2,-1,-4]
# 输出：[[-1,-1,2],[-1,0,1]]

# 经典做法是排序 + 双指针，O(n²) 搞定。
# 核心思路：先排序，然后固定一个数 nums[i]，在它右边用双指针找两个数使三数之和为 0。

def threeSum(nums):
    nums.sort()
    result = []
    for i in range(len(nums)):
        # 剪枝：最小值大于0，后面不可能凑出0
        if nums[i] > 0:
            break
        # 去重：跳过重复的 i
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        # 双指针
        left = i + 1
        right = len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1       # 和太小，左指针右移
            elif total > 0:
                right -= 1      # 和太大，右指针左移
            else:
                result.append([nums[i], nums[left], nums[right]])
                # 去重：跳过重复的 left 和 right
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
    return result

# 练习 1：两数之和（简单）
# 给定一个已排序数组 nums 和目标值 target，找出所有不重复的两个数使它们的和等于 target。

def twoSum(nums, target):
