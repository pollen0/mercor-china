#!/usr/bin/env python3
"""
Seed script for coding challenges.

Usage:
    python -m scripts.seed_coding_challenges

This script seeds the database with default coding challenges for technical assessments.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import CodingChallenge
from app.config import settings


def generate_cuid(prefix: str = "cc") -> str:
    """Generate a CUID-like ID."""
    return f"{prefix}{uuid.uuid4().hex[:22]}"


# Default coding challenges
DEFAULT_CODING_CHALLENGES = [
    {
        "title": "FizzBuzz",
        "title_zh": "FizzBuzz",
        "description": """Write a function `solution(n)` that returns a list of integers from 1 to n, but:
- For multiples of 3, use the string "Fizz" instead of the number
- For multiples of 5, use the string "Buzz" instead of the number
- For multiples of both 3 and 5, use the string "FizzBuzz"

Example:
- solution(5) should return [1, 2, "Fizz", 4, "Buzz"]
- solution(15) should return [1, 2, "Fizz", 4, "Buzz", "Fizz", 7, 8, "Fizz", "Buzz", 11, "Fizz", 13, 14, "FizzBuzz"]
""",
        "description_zh": """编写一个函数 `solution(n)` 返回从1到n的列表，但是：
- 3的倍数用字符串 "Fizz" 代替数字
- 5的倍数用字符串 "Buzz" 代替数字
- 同时是3和5的倍数用字符串 "FizzBuzz" 代替

示例：
- solution(5) 应返回 [1, 2, "Fizz", 4, "Buzz"]
- solution(15) 应返回 [1, 2, "Fizz", 4, "Buzz", "Fizz", 7, 8, "Fizz", "Buzz", 11, "Fizz", 13, 14, "FizzBuzz"]
""",
        "starter_code": '''def solution(n):
    """
    Return a list from 1 to n with FizzBuzz rules applied.

    Args:
        n: A positive integer

    Returns:
        A list of integers and strings
    """
    # Your code here
    pass
''',
        "test_cases": [
            {"input": "5", "expected": "[1, 2, 'Fizz', 4, 'Buzz']", "hidden": False, "name": "Basic test n=5"},
            {"input": "1", "expected": "[1]", "hidden": False, "name": "Single element"},
            {"input": "3", "expected": "[1, 2, 'Fizz']", "hidden": False, "name": "First Fizz"},
            {"input": "15", "expected": "[1, 2, 'Fizz', 4, 'Buzz', 'Fizz', 7, 8, 'Fizz', 'Buzz', 11, 'Fizz', 13, 14, 'FizzBuzz']", "hidden": True, "name": "Complete sequence"},
            {"input": "30", "expected": "[1, 2, 'Fizz', 4, 'Buzz', 'Fizz', 7, 8, 'Fizz', 'Buzz', 11, 'Fizz', 13, 14, 'FizzBuzz', 16, 17, 'Fizz', 19, 'Buzz', 'Fizz', 22, 23, 'Fizz', 'Buzz', 26, 'Fizz', 28, 29, 'FizzBuzz']", "hidden": True, "name": "Larger input"},
        ],
        "time_limit_seconds": 5,
        "difficulty": "easy"
    },
    {
        "title": "Two Sum",
        "title_zh": "两数之和",
        "description": """Given an array of integers `nums` and an integer `target`, return the indices of the two numbers that add up to `target`.

You may assume that each input has exactly one solution, and you cannot use the same element twice.

Write a function `solution(nums, target)` that returns a list of two indices.

Example:
- solution([2, 7, 11, 15], 9) should return [0, 1] (because nums[0] + nums[1] = 2 + 7 = 9)
- solution([3, 2, 4], 6) should return [1, 2] (because nums[1] + nums[2] = 2 + 4 = 6)
""",
        "description_zh": """给定一个整数数组 `nums` 和一个整数目标值 `target`，返回两个数之和等于目标值的元素下标。

假设每个输入只有一个解，且同一个元素不能使用两次。

编写函数 `solution(nums, target)` 返回包含两个下标的列表。

示例：
- solution([2, 7, 11, 15], 9) 应返回 [0, 1]（因为 nums[0] + nums[1] = 2 + 7 = 9）
- solution([3, 2, 4], 6) 应返回 [1, 2]（因为 nums[1] + nums[2] = 2 + 4 = 6）
""",
        "starter_code": '''def solution(nums, target):
    """
    Find two numbers that add up to target.

    Args:
        nums: List of integers
        target: Target sum

    Returns:
        List of two indices [i, j] where nums[i] + nums[j] == target
    """
    # Your code here
    pass
''',
        "test_cases": [
            {"input": "[2, 7, 11, 15], 9", "expected": "[0, 1]", "hidden": False, "name": "Basic example"},
            {"input": "[3, 2, 4], 6", "expected": "[1, 2]", "hidden": False, "name": "Non-adjacent elements"},
            {"input": "[3, 3], 6", "expected": "[0, 1]", "hidden": False, "name": "Same values"},
            {"input": "[1, 2, 3, 4, 5], 9", "expected": "[3, 4]", "hidden": True, "name": "Larger array"},
            {"input": "[-1, -2, -3, -4, -5], -8", "expected": "[2, 4]", "hidden": True, "name": "Negative numbers"},
        ],
        "time_limit_seconds": 5,
        "difficulty": "easy"
    },
    {
        "title": "Reverse Linked List",
        "title_zh": "反转链表",
        "description": """Given a singly linked list, reverse it and return the reversed list.

For simplicity, the input is given as a Python list, and you should return a reversed list.

Write a function `solution(nums)` that reverses the list.

Example:
- solution([1, 2, 3, 4, 5]) should return [5, 4, 3, 2, 1]
- solution([1, 2]) should return [2, 1]
- solution([]) should return []

Note: You should implement this without using built-in reverse functions or slicing.
""",
        "description_zh": """给定一个单向链表，反转它并返回反转后的链表。

为简化问题，输入以Python列表形式给出，你应该返回一个反转后的列表。

编写函数 `solution(nums)` 反转列表。

示例：
- solution([1, 2, 3, 4, 5]) 应返回 [5, 4, 3, 2, 1]
- solution([1, 2]) 应返回 [2, 1]
- solution([]) 应返回 []

注意：请不要使用内置的 reverse() 函数或切片 [::-1]。
""",
        "starter_code": '''def solution(nums):
    """
    Reverse a list (simulating linked list reversal).

    Args:
        nums: List of integers

    Returns:
        Reversed list

    Note: Do not use built-in reverse() or [::-1]
    """
    # Your code here
    pass
''',
        "test_cases": [
            {"input": "[1, 2, 3, 4, 5]", "expected": "[5, 4, 3, 2, 1]", "hidden": False, "name": "Basic reversal"},
            {"input": "[1, 2]", "expected": "[2, 1]", "hidden": False, "name": "Two elements"},
            {"input": "[]", "expected": "[]", "hidden": False, "name": "Empty list"},
            {"input": "[1]", "expected": "[1]", "hidden": False, "name": "Single element"},
            {"input": "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]", "expected": "[10, 9, 8, 7, 6, 5, 4, 3, 2, 1]", "hidden": True, "name": "Longer list"},
        ],
        "time_limit_seconds": 5,
        "difficulty": "medium"
    },
    {
        "title": "Valid Parentheses",
        "title_zh": "有效括号",
        "description": """Given a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.

Write a function `solution(s)` that returns True if the string is valid, False otherwise.

Example:
- solution("()") should return True
- solution("()[]{}") should return True
- solution("(]") should return False
- solution("([)]") should return False
- solution("{[]}") should return True
""",
        "description_zh": """给定一个只包含 '('、')'、'{'、'}'、'[' 和 ']' 的字符串，判断字符串是否有效。

有效字符串需满足：
1. 左括号必须用相同类型的右括号闭合。
2. 左括号必须以正确的顺序闭合。
3. 每个右括号都有一个对应的相同类型的左括号。

编写函数 `solution(s)` 返回 True（有效）或 False（无效）。

示例：
- solution("()") 应返回 True
- solution("()[]{}") 应返回 True
- solution("(]") 应返回 False
- solution("([)]") 应返回 False
- solution("{[]}") 应返回 True
""",
        "starter_code": '''def solution(s):
    """
    Check if a string of brackets is valid.

    Args:
        s: String containing only '(){}[]'

    Returns:
        True if valid, False otherwise
    """
    # Your code here
    pass
''',
        "test_cases": [
            {"input": "'()'", "expected": "True", "hidden": False, "name": "Simple valid"},
            {"input": "'()[]{}'", "expected": "True", "hidden": False, "name": "Multiple types"},
            {"input": "'(]'", "expected": "False", "hidden": False, "name": "Mismatched"},
            {"input": "'([)]'", "expected": "False", "hidden": False, "name": "Wrong order"},
            {"input": "'{[]}'", "expected": "True", "hidden": False, "name": "Nested"},
            {"input": "''", "expected": "True", "hidden": True, "name": "Empty string"},
            {"input": "'((()))'", "expected": "True", "hidden": True, "name": "Deeply nested"},
            {"input": "'((()'", "expected": "False", "hidden": True, "name": "Unclosed"},
        ],
        "time_limit_seconds": 5,
        "difficulty": "easy"
    },
    {
        "title": "Palindrome Check",
        "title_zh": "回文检查",
        "description": """Given a string, determine if it is a palindrome, considering only alphanumeric characters and ignoring cases.

Write a function `solution(s)` that returns True if the string is a palindrome, False otherwise.

Example:
- solution("A man, a plan, a canal: Panama") should return True
- solution("race a car") should return False
- solution("") should return True (empty string is a palindrome)
""",
        "description_zh": """给定一个字符串，判断它是否是回文，只考虑字母和数字字符，忽略大小写。

编写函数 `solution(s)` 返回 True（是回文）或 False（不是回文）。

示例：
- solution("A man, a plan, a canal: Panama") 应返回 True
- solution("race a car") 应返回 False
- solution("") 应返回 True（空字符串是回文）
""",
        "starter_code": '''def solution(s):
    """
    Check if a string is a palindrome (ignoring non-alphanumeric characters and case).

    Args:
        s: Input string

    Returns:
        True if palindrome, False otherwise
    """
    # Your code here
    pass
''',
        "test_cases": [
            {"input": "'A man, a plan, a canal: Panama'", "expected": "True", "hidden": False, "name": "Classic example"},
            {"input": "'race a car'", "expected": "False", "hidden": False, "name": "Not palindrome"},
            {"input": "''", "expected": "True", "hidden": False, "name": "Empty string"},
            {"input": "' '", "expected": "True", "hidden": False, "name": "Single space"},
            {"input": "'Was it a car or a cat I saw?'", "expected": "True", "hidden": True, "name": "Sentence palindrome"},
            {"input": "'12321'", "expected": "True", "hidden": True, "name": "Numeric palindrome"},
        ],
        "time_limit_seconds": 5,
        "difficulty": "easy"
    },
    {
        "title": "Binary Search",
        "title_zh": "二分查找",
        "description": """Given a sorted array of integers and a target value, return the index of the target if it exists, or -1 if it doesn't.

Write a function `solution(nums, target)` that implements binary search.

Your solution must run in O(log n) time complexity.

Example:
- solution([-1, 0, 3, 5, 9, 12], 9) should return 4
- solution([-1, 0, 3, 5, 9, 12], 2) should return -1
- solution([5], 5) should return 0
""",
        "description_zh": """给定一个升序排列的整数数组和一个目标值，如果目标值存在则返回其索引，否则返回 -1。

编写函数 `solution(nums, target)` 实现二分查找。

你的解法必须是 O(log n) 时间复杂度。

示例：
- solution([-1, 0, 3, 5, 9, 12], 9) 应返回 4
- solution([-1, 0, 3, 5, 9, 12], 2) 应返回 -1
- solution([5], 5) 应返回 0
""",
        "starter_code": '''def solution(nums, target):
    """
    Find the index of target in a sorted array using binary search.

    Args:
        nums: Sorted list of integers
        target: Value to search for

    Returns:
        Index of target, or -1 if not found
    """
    # Your code here
    pass
''',
        "test_cases": [
            {"input": "[-1, 0, 3, 5, 9, 12], 9", "expected": "4", "hidden": False, "name": "Found in array"},
            {"input": "[-1, 0, 3, 5, 9, 12], 2", "expected": "-1", "hidden": False, "name": "Not found"},
            {"input": "[5], 5", "expected": "0", "hidden": False, "name": "Single element found"},
            {"input": "[5], -5", "expected": "-1", "hidden": False, "name": "Single element not found"},
            {"input": "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 1", "expected": "0", "hidden": True, "name": "First element"},
            {"input": "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 10", "expected": "9", "hidden": True, "name": "Last element"},
        ],
        "time_limit_seconds": 5,
        "difficulty": "easy"
    },
    {
        "title": "Maximum Subarray",
        "title_zh": "最大子数组和",
        "description": """Given an integer array, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.

Write a function `solution(nums)` that returns the maximum subarray sum.

Example:
- solution([-2, 1, -3, 4, -1, 2, 1, -5, 4]) should return 6 (the subarray [4, -1, 2, 1] has the largest sum = 6)
- solution([1]) should return 1
- solution([5, 4, -1, 7, 8]) should return 23

Hint: Think about Kadane's algorithm.
""",
        "description_zh": """给定一个整数数组，找到具有最大和的连续子数组（至少包含一个数字），返回其最大和。

编写函数 `solution(nums)` 返回最大子数组和。

示例：
- solution([-2, 1, -3, 4, -1, 2, 1, -5, 4]) 应返回 6（子数组 [4, -1, 2, 1] 的和最大 = 6）
- solution([1]) 应返回 1
- solution([5, 4, -1, 7, 8]) 应返回 23

提示：考虑使用 Kadane 算法。
""",
        "starter_code": '''def solution(nums):
    """
    Find the maximum sum of a contiguous subarray.

    Args:
        nums: List of integers (at least one element)

    Returns:
        Maximum subarray sum
    """
    # Your code here
    pass
''',
        "test_cases": [
            {"input": "[-2, 1, -3, 4, -1, 2, 1, -5, 4]", "expected": "6", "hidden": False, "name": "Classic example"},
            {"input": "[1]", "expected": "1", "hidden": False, "name": "Single element"},
            {"input": "[5, 4, -1, 7, 8]", "expected": "23", "hidden": False, "name": "All positive result"},
            {"input": "[-1]", "expected": "-1", "hidden": False, "name": "Single negative"},
            {"input": "[-2, -1]", "expected": "-1", "hidden": True, "name": "All negative"},
            {"input": "[1, 2, 3, 4, 5]", "expected": "15", "hidden": True, "name": "All positive"},
        ],
        "time_limit_seconds": 5,
        "difficulty": "medium"
    },
    {
        "title": "Merge Intervals",
        "title_zh": "合并区间",
        "description": """Given an array of intervals where intervals[i] = [start_i, end_i], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.

Write a function `solution(intervals)` that returns the merged intervals.

Example:
- solution([[1,3], [2,6], [8,10], [15,18]]) should return [[1,6], [8,10], [15,18]]
  (Intervals [1,3] and [2,6] overlap, so they are merged into [1,6])
- solution([[1,4], [4,5]]) should return [[1,5]]
  (Intervals [1,4] and [4,5] are adjacent, so they are merged)
""",
        "description_zh": """给定一个区间数组，其中 intervals[i] = [start_i, end_i]，合并所有重叠的区间，返回一个不重叠的区间数组，该数组覆盖输入中的所有区间。

编写函数 `solution(intervals)` 返回合并后的区间。

示例：
- solution([[1,3], [2,6], [8,10], [15,18]]) 应返回 [[1,6], [8,10], [15,18]]
  （区间 [1,3] 和 [2,6] 重叠，合并为 [1,6]）
- solution([[1,4], [4,5]]) 应返回 [[1,5]]
  （区间 [1,4] 和 [4,5] 相邻，合并为 [1,5]）
""",
        "starter_code": '''def solution(intervals):
    """
    Merge overlapping intervals.

    Args:
        intervals: List of [start, end] pairs

    Returns:
        List of merged non-overlapping intervals
    """
    # Your code here
    pass
''',
        "test_cases": [
            {"input": "[[1,3], [2,6], [8,10], [15,18]]", "expected": "[[1, 6], [8, 10], [15, 18]]", "hidden": False, "name": "Multiple merges"},
            {"input": "[[1,4], [4,5]]", "expected": "[[1, 5]]", "hidden": False, "name": "Adjacent intervals"},
            {"input": "[[1,4]]", "expected": "[[1, 4]]", "hidden": False, "name": "Single interval"},
            {"input": "[[1,4], [0,4]]", "expected": "[[0, 4]]", "hidden": True, "name": "Overlap at start"},
            {"input": "[[1,4], [2,3]]", "expected": "[[1, 4]]", "hidden": True, "name": "Contained interval"},
            {"input": "[[1,4], [0,0]]", "expected": "[[0, 0], [1, 4]]", "hidden": True, "name": "Non-overlapping"},
        ],
        "time_limit_seconds": 5,
        "difficulty": "medium"
    },
    {
        "title": "Climbing Stairs",
        "title_zh": "爬楼梯",
        "description": """You are climbing a staircase. It takes n steps to reach the top.

Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?

Write a function `solution(n)` that returns the number of distinct ways to climb n steps.

Example:
- solution(2) should return 2 (1+1 or 2)
- solution(3) should return 3 (1+1+1, 1+2, or 2+1)
- solution(4) should return 5 (1+1+1+1, 1+1+2, 1+2+1, 2+1+1, 2+2)
""",
        "description_zh": """你正在爬楼梯。需要 n 步才能到达顶部。

每次你可以爬 1 步或 2 步。你有多少种不同的方法可以爬到顶部？

编写函数 `solution(n)` 返回爬 n 步的不同方法数。

示例：
- solution(2) 应返回 2（1+1 或 2）
- solution(3) 应返回 3（1+1+1、1+2 或 2+1）
- solution(4) 应返回 5（1+1+1+1、1+1+2、1+2+1、2+1+1、2+2）
""",
        "starter_code": '''def solution(n):
    """
    Calculate the number of distinct ways to climb n stairs.

    Args:
        n: Number of steps (positive integer)

    Returns:
        Number of distinct ways to climb
    """
    # Your code here
    pass
''',
        "test_cases": [
            {"input": "2", "expected": "2", "hidden": False, "name": "Two steps"},
            {"input": "3", "expected": "3", "hidden": False, "name": "Three steps"},
            {"input": "4", "expected": "5", "hidden": False, "name": "Four steps"},
            {"input": "1", "expected": "1", "hidden": False, "name": "One step"},
            {"input": "5", "expected": "8", "hidden": True, "name": "Five steps"},
            {"input": "10", "expected": "89", "hidden": True, "name": "Ten steps"},
        ],
        "time_limit_seconds": 5,
        "difficulty": "easy"
    },
    {
        "title": "Find First and Last Position",
        "title_zh": "查找元素的第一个和最后一个位置",
        "description": """Given an array of integers sorted in ascending order, find the starting and ending position of a given target value.

If the target is not found in the array, return [-1, -1].

You must write an algorithm with O(log n) runtime complexity.

Write a function `solution(nums, target)` that returns [first_position, last_position].

Example:
- solution([5, 7, 7, 8, 8, 10], 8) should return [3, 4]
- solution([5, 7, 7, 8, 8, 10], 6) should return [-1, -1]
- solution([], 0) should return [-1, -1]
""",
        "description_zh": """给定一个按升序排列的整数数组，找出给定目标值的开始位置和结束位置。

如果目标值在数组中不存在，返回 [-1, -1]。

你必须设计一个时间复杂度为 O(log n) 的算法。

编写函数 `solution(nums, target)` 返回 [第一个位置, 最后一个位置]。

示例：
- solution([5, 7, 7, 8, 8, 10], 8) 应返回 [3, 4]
- solution([5, 7, 7, 8, 8, 10], 6) 应返回 [-1, -1]
- solution([], 0) 应返回 [-1, -1]
""",
        "starter_code": '''def solution(nums, target):
    """
    Find the first and last position of target in a sorted array.

    Args:
        nums: Sorted list of integers
        target: Value to search for

    Returns:
        [first_index, last_index] or [-1, -1] if not found
    """
    # Your code here
    pass
''',
        "test_cases": [
            {"input": "[5, 7, 7, 8, 8, 10], 8", "expected": "[3, 4]", "hidden": False, "name": "Multiple occurrences"},
            {"input": "[5, 7, 7, 8, 8, 10], 6", "expected": "[-1, -1]", "hidden": False, "name": "Not found"},
            {"input": "[], 0", "expected": "[-1, -1]", "hidden": False, "name": "Empty array"},
            {"input": "[1], 1", "expected": "[0, 0]", "hidden": False, "name": "Single element found"},
            {"input": "[1, 1, 1, 1, 1], 1", "expected": "[0, 4]", "hidden": True, "name": "All same elements"},
            {"input": "[1, 2, 3, 4, 5], 3", "expected": "[2, 2]", "hidden": True, "name": "Single occurrence"},
        ],
        "time_limit_seconds": 5,
        "difficulty": "medium"
    }
]


def seed_coding_challenges():
    """Seed the database with default coding challenges."""
    print("Connecting to database...")
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Get existing challenge titles to avoid duplicates
        existing_titles = {c.title for c in db.query(CodingChallenge.title).all()}
        existing_count = len(existing_titles)

        if existing_count > 0:
            print(f"Found {existing_count} existing coding challenges.")

        print("Seeding new coding challenges...")
        added_count = 0
        for challenge_data in DEFAULT_CODING_CHALLENGES:
            # Skip if challenge with same title already exists
            if challenge_data["title"] in existing_titles:
                print(f"  Skipping (exists): {challenge_data['title']}")
                continue

            challenge = CodingChallenge(
                id=generate_cuid(),
                title=challenge_data["title"],
                title_zh=challenge_data["title_zh"],
                description=challenge_data["description"],
                description_zh=challenge_data["description_zh"],
                starter_code=challenge_data["starter_code"],
                test_cases=challenge_data["test_cases"],
                time_limit_seconds=challenge_data["time_limit_seconds"],
                difficulty=challenge_data["difficulty"],
            )
            db.add(challenge)
            added_count += 1
            print(f"  Added: {challenge.title} ({challenge.difficulty})")

        db.commit()
        print(f"Successfully added {added_count} new coding challenges! Total: {existing_count + added_count}")

    except Exception as e:
        print(f"Error seeding coding challenges: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def list_coding_challenges():
    """List all coding challenges in the database."""
    print("Connecting to database...")
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        challenges = db.query(CodingChallenge).all()
        print(f"\nFound {len(challenges)} coding challenges:\n")
        for c in challenges:
            test_count = len(c.test_cases) if c.test_cases else 0
            print(f"  [{c.difficulty.upper()}] {c.title} ({c.title_zh}) - {test_count} tests")
            print(f"    ID: {c.id}")
            print()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage coding challenges")
    parser.add_argument("--list", action="store_true", help="List existing challenges")
    args = parser.parse_args()

    if args.list:
        list_coding_challenges()
    else:
        seed_coding_challenges()
