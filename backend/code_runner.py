"""
BugMind AI — Safe Code Execution Engine
Executes Python code in a sandboxed subprocess with timeout.
"""

import subprocess
import sys
import time
import tempfile
import os
import re


# --- Configuration ---
EXECUTION_TIMEOUT = 10  # seconds
MAX_OUTPUT_LENGTH = 5000  # characters


def run_python_code(code: str) -> dict:
    """
    Execute Python code safely in a subprocess.
    Returns dict with: success, output, error, error_type, execution_time
    """
    start_time = time.time()

    # Create a temporary file for the code
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False, encoding='utf-8'
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Failed to create temp file: {str(e)}",
            "error_type": "SystemError",
            "execution_time": 0.0
        }

    try:
        # Run code in subprocess with timeout
        result = subprocess.run(
            [sys.executable, "-u", tmp_path],
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT,
            cwd=tempfile.gettempdir(),
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        )

        execution_time = round(time.time() - start_time, 3)
        stdout = result.stdout[:MAX_OUTPUT_LENGTH] if result.stdout else ""
        stderr = result.stderr[:MAX_OUTPUT_LENGTH] if result.stderr else ""

        if result.returncode == 0:
            return {
                "success": True,
                "output": stdout or "(No output)",
                "error": None,
                "error_type": None,
                "execution_time": execution_time
            }
        else:
            error_type = extract_error_type(stderr)
            error_msg = extract_error_message(stderr)
            return {
                "success": False,
                "output": stdout,
                "error": error_msg or stderr,
                "error_type": error_type,
                "execution_time": execution_time
            }

    except subprocess.TimeoutExpired:
        execution_time = round(time.time() - start_time, 3)
        return {
            "success": False,
            "output": "",
            "error": f"Code execution timed out after {EXECUTION_TIMEOUT} seconds. Check for infinite loops.",
            "error_type": "TimeoutError",
            "execution_time": execution_time
        }
    except Exception as e:
        execution_time = round(time.time() - start_time, 3)
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "error_type": "SystemError",
            "execution_time": execution_time
        }
    finally:
        # Cleanup temp file
        try:
            os.unlink(tmp_path)
        except:
            pass


def extract_error_type(stderr: str) -> str:
    """Extract the Python error type from stderr."""
    # Match patterns like: TypeError: ..., SyntaxError: ..., etc.
    patterns = [
        r'(\w+Error):',
        r'(\w+Exception):',
        r'(\w+Warning):',
    ]
    for pattern in patterns:
        match = re.search(pattern, stderr)
        if match:
            return match.group(1)
    return "UnknownError"


def extract_error_message(stderr: str) -> str:
    """Extract the clean error message from stderr."""
    lines = stderr.strip().split('\n')
    if lines:
        # The last line usually contains the actual error
        last_line = lines[-1].strip()
        if ':' in last_line:
            return last_line
        # If traceback, get the last meaningful line
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith('File') and not line.startswith('Traceback'):
                return line
    return stderr.strip()


def validate_code_safety(code: str) -> tuple:
    """
    Basic safety check for dangerous operations.
    Returns (is_safe: bool, reason: str)
    """
    dangerous_patterns = [
        (r'\bimport\s+os\b', "Importing 'os' module is restricted"),
        (r'\bimport\s+sys\b', "Importing 'sys' module is restricted"),
        (r'\bimport\s+subprocess\b', "Importing 'subprocess' is restricted"),
        (r'\bimport\s+shutil\b', "Importing 'shutil' is restricted"),
        (r'\b__import__\b', "Using __import__ is restricted"),
        (r'\beval\s*\(', "Using eval() is restricted"),
        (r'\bexec\s*\(', "Using exec() is restricted"),
        (r'\bopen\s*\(.+["\']w', "Writing to files is restricted"),
        (r'\bos\.system\b', "os.system() is restricted"),
        (r'\bos\.remove\b', "os.remove() is restricted"),
        (r'\bos\.rmdir\b', "os.rmdir() is restricted"),
    ]

    for pattern, reason in dangerous_patterns:
        if re.search(pattern, code):
            return False, reason

    return True, "Code is safe to execute"


if __name__ == "__main__":
    # Test execution
    test_code = """
x = 5
y = 10
print(f"Sum: {x + y}")
print(f"Product: {x * y}")
"""
    result = run_python_code(test_code)
    print(result)
