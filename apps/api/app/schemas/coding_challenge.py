"""Pydantic schemas for coding challenges."""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class TestCase(BaseModel):
    """A single test case for a coding challenge."""
    input: str  # Input to pass to solution function
    expected: str  # Expected output
    hidden: bool = False  # Whether to hide from candidate
    name: Optional[str] = None  # Display name for the test


class TestCaseResult(BaseModel):
    """Result of running a single test case."""
    name: str
    passed: bool
    actual: str
    expected: str
    hidden: bool = False
    error: Optional[str] = None


class CodingChallengeBase(BaseModel):
    """Base schema for coding challenge."""
    title: str
    title_zh: Optional[str] = None
    description: str  # Problem description
    description_zh: Optional[str] = None  # Chinese translation
    starter_code: Optional[str] = None
    test_cases: list[TestCase]
    time_limit_seconds: int = 5
    difficulty: str = "easy"

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = ["easy", "medium", "hard"]
        if v.lower() not in allowed:
            raise ValueError(f"Difficulty must be one of: {', '.join(allowed)}")
        return v.lower()


class CodingChallengeCreate(CodingChallengeBase):
    """Schema for creating a coding challenge."""
    pass


class CodingChallengeResponse(CodingChallengeBase):
    """Schema for coding challenge response."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class CodingChallengeInfo(BaseModel):
    """Brief info about a coding challenge (for question lists)."""
    id: str
    title: str
    title_zh: Optional[str] = None
    difficulty: str
    has_starter_code: bool


# ==================== Code Submission Schemas ====================

class CodeSubmitRequest(BaseModel):
    """Request to submit code for a coding challenge."""
    code: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Code cannot be empty")
        if len(v) > 50000:  # 50KB limit
            raise ValueError("Code exceeds maximum length (50KB)")
        return v


class CodeExecutionResponse(BaseModel):
    """Response from code execution."""
    response_id: str
    question_index: int
    status: str  # "processing", "success", "error", "timeout"
    execution_time_ms: Optional[int] = None
    test_results: Optional[list[TestCaseResult]] = None
    passed_count: Optional[int] = None
    total_count: Optional[int] = None


class CodingFeedback(BaseModel):
    """Detailed feedback for a coding submission."""
    response_id: str
    question_index: int
    execution_status: str
    test_results: list[TestCaseResult]
    passed_count: int
    total_count: int
    execution_time_ms: int
    ai_score: Optional[float] = None
    analysis: Optional[str] = None
    strengths: list[str] = []
    concerns: list[str] = []
    tips: list[str] = []
    suggested_approach: Optional[str] = None
    time_complexity: Optional[str] = None
    optimal_complexity: Optional[str] = None


# ==================== Extended Question Info ====================

class CodingQuestionInfo(BaseModel):
    """Question info for coding challenges."""
    index: int
    text: str  # Brief description
    text_zh: Optional[str] = None
    category: Optional[str] = None
    question_type: str = "coding"
    coding_challenge: Optional[CodingChallengeResponse] = None


# ==================== Sample Coding Challenges ====================

# Default coding challenges for seeding
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

Note: You should implement this without using built-in reverse functions.
""",
        "description_zh": """给定一个单向链表，反转它并返回反转后的链表。

为简化问题，输入以Python列表形式给出，你应该返回一个反转后的列表。

编写函数 `solution(nums)` 反转列表。

示例：
- solution([1, 2, 3, 4, 5]) 应返回 [5, 4, 3, 2, 1]
- solution([1, 2]) 应返回 [2, 1]
- solution([]) 应返回 []

注意：请不要使用内置的 reverse 函数。
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
