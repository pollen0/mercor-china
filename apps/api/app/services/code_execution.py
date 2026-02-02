"""
Code execution service using Piston API.
Piston is a free, open-source code execution sandbox.
"""
import httpx
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("pathway.code_execution")

PISTON_URL = "https://emkc.org/api/v2/piston"


@dataclass
class TestCaseResult:
    """Result of a single test case execution."""
    name: str
    passed: bool
    actual: str
    expected: str
    hidden: bool = False
    error: Optional[str] = None


@dataclass
class ExecutionResult:
    """Result of code execution against all test cases."""
    success: bool
    stdout: str
    stderr: str
    execution_time_ms: int
    test_results: list[dict]  # [{name, passed, actual, expected, hidden, error}]
    error: Optional[str] = None


class CodeExecutionService:
    """Service for executing Python code via Piston API."""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    async def _execute_code(self, code: str, run_timeout_ms: int = 5000) -> dict:
        """Execute Python code via Piston API."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(
                    f"{PISTON_URL}/execute",
                    json={
                        "language": "python",
                        "version": "3.10",
                        "files": [{"content": code}],
                        "run_timeout": run_timeout_ms,
                    }
                )
                resp.raise_for_status()
                return resp.json()
            except httpx.TimeoutException:
                return {
                    "run": {
                        "stdout": "",
                        "stderr": "Execution timed out",
                        "code": -1,
                        "signal": "SIGKILL"
                    }
                }
            except httpx.HTTPError as e:
                logger.error(f"Piston API error: {e}")
                return {
                    "run": {
                        "stdout": "",
                        "stderr": f"Execution service error: {str(e)}",
                        "code": -1
                    }
                }

    async def execute_python(
        self,
        code: str,
        test_cases: list[dict],
        time_limit_seconds: int = 5
    ) -> ExecutionResult:
        """
        Execute Python code against test cases via Piston API.

        Args:
            code: The Python code to execute (should define a 'solution' function)
            test_cases: List of test case dicts with keys:
                - input: string input to pass to solution()
                - expected: string expected output
                - hidden: bool whether test is hidden from candidate
                - name: optional name for the test
            time_limit_seconds: Maximum execution time per test case

        Returns:
            ExecutionResult with success status and individual test results
        """
        results: list[dict] = []
        total_time_ms = 0
        all_passed = True
        last_stdout = ""
        last_stderr = ""

        for i, test in enumerate(test_cases):
            test_input = test.get("input", "")
            expected = str(test.get("expected", "")).strip()
            test_name = test.get("name", f"Test {i + 1}")
            is_hidden = test.get("hidden", False)

            # Wrap user code with test harness
            wrapped_code = f'''{code}

# Test execution
import sys
try:
    result = solution({test_input})
    print(result)
except Exception as e:
    print(f"Error: {{type(e).__name__}}: {{e}}", file=sys.stderr)
    sys.exit(1)
'''

            # Execute the code
            data = await self._execute_code(
                wrapped_code,
                run_timeout_ms=time_limit_seconds * 1000
            )

            run_data = data.get("run", {})
            actual = run_data.get("stdout", "").strip()
            stderr = run_data.get("stderr", "").strip()
            exit_code = run_data.get("code", 0)

            last_stdout = actual
            last_stderr = stderr

            # Check for timeout or error
            error = None
            if run_data.get("signal") == "SIGKILL":
                error = "Timeout"
                passed = False
            elif exit_code != 0:
                error = stderr or "Runtime error"
                passed = False
            else:
                # Compare output
                passed = actual == expected

            if not passed:
                all_passed = False

            # Estimate execution time (Piston doesn't always return precise timing)
            exec_time = 100  # Default estimate in ms
            total_time_ms += exec_time

            results.append({
                "name": test_name,
                "passed": passed,
                "actual": actual if not is_hidden else "[hidden]",
                "expected": expected if not is_hidden else "[hidden]",
                "hidden": is_hidden,
                "error": error,
            })

        return ExecutionResult(
            success=all_passed,
            stdout=last_stdout,
            stderr=last_stderr,
            execution_time_ms=total_time_ms,
            test_results=results,
            error=last_stderr if last_stderr else None,
        )

    async def validate_syntax(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Validate Python syntax without executing the code.

        Returns:
            Tuple of (is_valid, error_message)
        """
        check_code = f'''
import ast
import sys

code = {repr(code)}

try:
    ast.parse(code)
    print("valid")
except SyntaxError as e:
    print(f"SyntaxError at line {{e.lineno}}: {{e.msg}}")
'''
        data = await self._execute_code(check_code, run_timeout_ms=3000)
        output = data.get("run", {}).get("stdout", "").strip()

        if output == "valid":
            return True, None
        else:
            return False, output

    async def get_runtime_info(self) -> dict:
        """Get available Python runtime information from Piston."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(f"{PISTON_URL}/runtimes")
                resp.raise_for_status()
                runtimes = resp.json()

                # Find Python runtime
                python_runtime = next(
                    (r for r in runtimes if r.get("language") == "python"),
                    None
                )
                return python_runtime or {"language": "python", "version": "unknown"}
            except Exception as e:
                logger.error(f"Failed to get runtime info: {e}")
                return {"language": "python", "version": "3.10", "error": str(e)}


# Global instance
code_execution_service = CodeExecutionService()
