"""
BugMind AI — AI Error Explanation Engine
Analyzes Python errors and provides:
1. Simple explanation
2. Suggested fix
3. Fixed code
4. Learning recommendation
"""

import re


# --- Error Pattern Database ---
ERROR_PATTERNS = {
    "TypeError": {
        "str_int_compare": {
            "pattern": r"'[<>]=?' not supported between instances of 'str' and 'int'",
            "explanation": "🔍 You're trying to compare a **string** with a **number**. The `input()` function always returns a string, so you need to convert it to a number first.",
            "tip": "💡 Remember: `input()` always returns a string. Use `int()` for whole numbers or `float()` for decimals.",
            "category": "Type Conversion"
        },
        "str_concat": {
            "pattern": r"can only concatenate str.*to str|must be str, not int",
            "explanation": "🔍 You're trying to join a **string** with a **number**. Python can't automatically convert between types. Use `str()` to convert the number to text, or use f-strings.",
            "tip": "💡 Use f-strings for easy formatting: `f\"Your age is {age}\"` instead of `\"Your age is \" + age`",
            "category": "String Operations"
        },
        "not_callable": {
            "pattern": r"'(int|str|float|list|dict|bool)' object is not callable",
            "explanation": "🔍 You're trying to **call** a variable as if it were a function. This usually happens when you name a variable the same as a built-in function (like `list`, `str`, `int`).",
            "tip": "💡 Avoid naming variables the same as Python built-in functions.",
            "category": "Variable Naming"
        },
        "not_subscriptable": {
            "pattern": r"'(int|float|NoneType)' object is not subscriptable",
            "explanation": "🔍 You're trying to use **square brackets []** on a value that doesn't support indexing (like a number or None).",
            "tip": "💡 Only strings, lists, tuples, and dictionaries support indexing with [].",
            "category": "Data Types"
        },
        "default": {
            "pattern": r"TypeError",
            "explanation": "🔍 There's a **type mismatch** in your code. You're using a value of the wrong type for an operation.",
            "tip": "💡 Check the types of your variables using `type(variable)` to debug.",
            "category": "Type Conversion"
        }
    },
    "SyntaxError": {
        "missing_colon": {
            "pattern": r"expected ':'|invalid syntax.*if|invalid syntax.*for|invalid syntax.*while|invalid syntax.*def",
            "explanation": "🔍 You're missing a **colon (:)** at the end of a statement. In Python, `if`, `for`, `while`, `def`, and `class` statements must end with a colon.",
            "tip": "💡 Think of the colon as saying \"here's what follows\" — it tells Python an indented block is coming next.",
            "category": "Syntax Rules"
        },
        "indentation": {
            "pattern": r"unexpected indent|IndentationError|expected an indented block",
            "explanation": "🔍 There's an **indentation problem** in your code. Python uses indentation (spaces) to define code blocks instead of braces.",
            "tip": "💡 Use 4 spaces for each indentation level. Be consistent — don't mix tabs and spaces!",
            "category": "Indentation"
        },
        "missing_paren": {
            "pattern": r"unexpected EOF|'\\)' was never closed|'\\]' was never closed",
            "explanation": "🔍 You have an **unclosed bracket** — a parenthesis `()`, bracket `[]`, or brace `{}` that was opened but never closed.",
            "tip": "💡 Count your opening and closing brackets. Most code editors highlight matching brackets.",
            "category": "Syntax Rules"
        },
        "default": {
            "pattern": r"SyntaxError",
            "explanation": "🔍 There's a **syntax error** in your code. Python couldn't understand the structure of your code.",
            "tip": "💡 Check for missing colons, brackets, quotes, or incorrect indentation.",
            "category": "Syntax Rules"
        }
    },
    "NameError": {
        "not_defined": {
            "pattern": r"name '(\w+)' is not defined",
            "explanation": "🔍 You're using a variable called **'{match}'** that hasn't been created yet. This usually means you misspelled a variable name or forgot to define it.",
            "tip": "💡 Python is case-sensitive! `name` and `Name` are different variables. Check your spelling carefully.",
            "category": "Variable Naming"
        },
        "default": {
            "pattern": r"NameError",
            "explanation": "🔍 You're trying to use a **name** (variable or function) that Python doesn't recognize.",
            "tip": "💡 Make sure you define variables before using them and check for typos.",
            "category": "Variable Naming"
        }
    },
    "ValueError": {
        "invalid_literal": {
            "pattern": r"invalid literal for int\(\) with base 10",
            "explanation": "🔍 You're trying to convert text to a number, but the text doesn't contain a valid number. For example, `int('hello')` would cause this error.",
            "tip": "💡 Always validate user input before converting. Use try/except to handle invalid input gracefully.",
            "category": "Input Validation"
        },
        "default": {
            "pattern": r"ValueError",
            "explanation": "🔍 A function received a value of the right type but an inappropriate **value**.",
            "tip": "💡 Check that the values you're passing to functions are within the expected range.",
            "category": "Input Validation"
        }
    },
    "IndexError": {
        "out_of_range": {
            "pattern": r"list index out of range",
            "explanation": "🔍 You're trying to access a position in a list that **doesn't exist**. For example, if your list has 3 items (index 0, 1, 2), accessing index 3 causes this error.",
            "tip": "💡 Remember: list indices start at 0. A list with 3 items has indices 0, 1, and 2. Use `len(list)` to check the size.",
            "category": "Data Structures"
        },
        "default": {
            "pattern": r"IndexError",
            "explanation": "🔍 You're trying to access an **index** that is out of the valid range.",
            "tip": "💡 Check your list length with `len()` before accessing indices.",
            "category": "Data Structures"
        }
    },
    "ZeroDivisionError": {
        "default": {
            "pattern": r"ZeroDivisionError|division by zero",
            "explanation": "🔍 You're trying to **divide by zero**, which is mathematically impossible.",
            "tip": "💡 Always check if the divisor is zero before dividing: `if divisor != 0: result = num / divisor`",
            "category": "Math Operations"
        }
    },
    "AttributeError": {
        "default": {
            "pattern": r"AttributeError",
            "explanation": "🔍 You're trying to access an **attribute or method** that doesn't exist on this object type.",
            "tip": "💡 Check the type of your variable with `type()` and use `dir()` to see available methods.",
            "category": "Object Methods"
        }
    },
    "KeyError": {
        "default": {
            "pattern": r"KeyError",
            "explanation": "🔍 You're trying to access a **dictionary key** that doesn't exist.",
            "tip": "💡 Use `dict.get('key', default_value)` to safely access dictionary keys without errors.",
            "category": "Data Structures"
        }
    }
}


def analyze_error(code: str, error_message: str, error_type: str = None) -> dict:
    """
    Analyze a Python error and return explanation, fix, and learning tip.
    """
    if not error_type:
        error_type = _detect_error_type(error_message)

    # Find matching pattern
    explanation_data = _find_matching_pattern(error_type, error_message)

    # Generate fix suggestion
    suggested_fix, fixed_code = _generate_fix(code, error_type, error_message)

    # Build response
    explanation = explanation_data.get("explanation", f"An error occurred: {error_message}")

    # Replace {match} placeholders with actual values
    match = re.search(r"name '(\w+)' is not defined", error_message)
    if match:
        explanation = explanation.replace("{match}", match.group(1))

    return {
        "explanation": explanation,
        "suggested_fix": suggested_fix,
        "fixed_code": fixed_code,
        "learning_tip": explanation_data.get("tip", "💡 Review the error message carefully — it often tells you exactly what went wrong."),
        "error_category": explanation_data.get("category", "General")
    }


def _detect_error_type(error_message: str) -> str:
    """Detect the error type from the error message."""
    error_types = [
        "TypeError", "SyntaxError", "NameError", "ValueError",
        "IndexError", "ZeroDivisionError", "AttributeError",
        "KeyError", "ImportError", "FileNotFoundError",
        "IndentationError", "RuntimeError", "TimeoutError"
    ]
    for et in error_types:
        if et in error_message:
            return et
    return "UnknownError"


def _find_matching_pattern(error_type: str, error_message: str) -> dict:
    """Find the best matching error pattern."""
    # Handle IndentationError as SyntaxError
    lookup_type = error_type
    if error_type == "IndentationError":
        lookup_type = "SyntaxError"

    patterns = ERROR_PATTERNS.get(lookup_type, {})

    # Try to find a specific pattern match
    for key, data in patterns.items():
        if key == "default":
            continue
        if re.search(data["pattern"], error_message, re.IGNORECASE):
            return data

    # Fall back to default for that error type
    if "default" in patterns:
        return patterns["default"]

    # Generic fallback
    return {
        "explanation": f"🔍 A **{error_type}** occurred in your code: {error_message}",
        "tip": "💡 Read the error message carefully — Python tries to tell you what went wrong and where.",
        "category": "General"
    }


def _generate_fix(code: str, error_type: str, error_message: str) -> tuple:
    """
    Generate a suggested fix and fixed code.
    Returns (suggested_fix_description, fixed_code)
    """
    fixed_code = code
    suggestion = ""

    if error_type == "TypeError":
        # String to int comparison
        if "not supported between" in error_message and "str" in error_message:
            # Find the comparison and wrap with int()
            match = re.search(r"(\w+)\s*([<>=!]+)\s*(\d+)", code)
            if match:
                var_name = match.group(1)
                operator = match.group(2)
                value = match.group(3)
                old_expr = f"{var_name} {operator} {value}"
                new_expr = f"int({var_name}) {operator} {value}"
                fixed_code = code.replace(old_expr, new_expr)
                suggestion = f"Convert `{var_name}` to integer before comparing: `int({var_name})`"

        # String concatenation with int
        elif "can only concatenate str" in error_message or "must be str, not int" in error_message:
            suggestion = "Use f-strings or str() to convert numbers to strings before concatenating"
            # Try to find + concatenation with potential int
            fixed_code = re.sub(
                r'(\"\s*\+\s*)(\w+)',
                lambda m: m.group(1) + f'str({m.group(2)})',
                code
            )

    elif error_type == "SyntaxError":
        # Missing colon after if/for/while/def
        if "expected ':'" in error_message or "invalid syntax" in error_message:
            lines = code.split('\n')
            fixed_lines = []
            for line in lines:
                stripped = line.rstrip()
                if re.match(r'\s*(if|elif|else|for|while|def|class|try|except|finally|with)\b', stripped):
                    if not stripped.endswith(':'):
                        stripped += ':'
                        suggestion = "Added missing colon (:) at the end of the statement"
                fixed_lines.append(stripped)
            fixed_code = '\n'.join(fixed_lines)

    elif error_type == "NameError":
        match = re.search(r"name '(\w+)' is not defined", error_message)
        if match:
            var_name = match.group(1)
            suggestion = f"Variable `{var_name}` is not defined. Check for typos or define it before use."

    elif error_type == "ValueError":
        if "invalid literal" in error_message:
            suggestion = "Add input validation with try/except before converting to int/float"
            # Wrap int() conversions in try/except
            if "int(" in code:
                fixed_code = f"try:\n{_indent_code(code)}\nexcept ValueError:\n    print('Please enter a valid number')"

    elif error_type == "IndexError":
        suggestion = "Check the list length before accessing an index"

    elif error_type == "ZeroDivisionError":
        suggestion = "Add a check for zero before dividing"

    if not suggestion:
        suggestion = f"Review the error: {error_message}"

    return suggestion, fixed_code


def _indent_code(code: str, spaces: int = 4) -> str:
    """Indent all lines of code by the specified number of spaces."""
    indent = ' ' * spaces
    return '\n'.join(indent + line for line in code.split('\n'))


# --- Quick Analysis for Real-time Detection ---

def quick_analyze(code: str) -> list:
    """
    Quick static analysis of code for common issues.
    Returns a list of potential issues found.
    """
    issues = []
    lines = code.split('\n')

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Missing colon
        if re.match(r'(if|elif|for|while|def|class)\s+.+[^:]\s*$', stripped):
            issues.append({
                "line": i,
                "type": "SyntaxError",
                "message": f"Missing colon (:) at end of '{stripped.split()[0]}' statement",
                "severity": "error"
            })

        # input() comparison without int()
        if re.search(r'input\(', stripped):
            # Check if there's a comparison on a line after
            for j in range(i, min(i + 5, len(lines))):
                next_line = lines[j - 1].strip() if j <= len(lines) else ""
                if re.search(r'\w+\s*[<>=!]+\s*\d+', next_line) and 'int(' not in next_line and 'float(' not in next_line:
                    issues.append({
                        "line": j,
                        "type": "TypeError",
                        "message": "Comparing input() result (string) with a number. Use int() or float() to convert first.",
                        "severity": "warning"
                    })

        # print without parentheses (Python 2 style)
        if re.match(r'print\s+["\']', stripped):
            issues.append({
                "line": i,
                "type": "SyntaxError",
                "message": "print is a function in Python 3. Use print() with parentheses.",
                "severity": "error"
            })

    return issues


if __name__ == "__main__":
    # Test analysis
    test_code = "age = input('Enter age:')\nif age > 18\n    print('Adult')"
    test_error = "TypeError: '>' not supported between instances of 'str' and 'int'"
    result = analyze_error(test_code, test_error, "TypeError")
    print(result)
