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
    }
]


def seed_coding_challenges():
    """Seed the database with default coding challenges."""
    print("Connecting to database...")
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Check if challenges already exist
        existing_count = db.query(CodingChallenge).count()
        if existing_count > 0:
            print(f"Found {existing_count} existing coding challenges. Skipping seed.")
            return

        print("Seeding coding challenges...")
        for challenge_data in DEFAULT_CODING_CHALLENGES:
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
            print(f"  Added: {challenge.title} ({challenge.difficulty})")

        db.commit()
        print(f"Successfully seeded {len(DEFAULT_CODING_CHALLENGES)} coding challenges!")

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
