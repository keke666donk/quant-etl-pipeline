class Solution(object):
    def twoSum(self, nums, target):
        for i in range(len(nums)):
            for j in range(i+1,len(nums)):
                if nums[i]+nums[j]==target:
                    return[i,j]
class Solution(object):
    def twoSum(self, nums, target):
        my_dict = {}
        for i, num in enumerate(nums):
            need=target-num
            if need in my_dict:
                return [my_dict[need],i]
            else:
                my_dict[num]=i
        return []
from typing import List
class Solution(object):
    def lengthOfLongestSubstring(self, s):
        """
        :type s: str
        :rtype: int
        """
        left=0
        window={}
        right=len(s)
        max_len=0
        for i in range(len(s)):
            for j in range(i,len(s))
                

