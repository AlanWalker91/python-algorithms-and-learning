# 给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子，下雨之后能接多少雨水。
# 如果 left_max < right_max：
#   当前位置的水量由 left_max 决定（短板在左边）
#   → 处理左边，left 右移
#
# 如果 left_max >= right_max：
#   当前位置的水量由 right_max 决定（短板在右边）
#   → 处理右边，right 左移

def trap(height):
    left = 0
    right = len(height) - 1
    left_max = 0
    right_max = 0
    result = 0

    while left < right:
        if height[left] < height[right]:
            left_max = max(left_max, height[left])
            result += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            result += right_max - height[right]
            right -= 1

    return result