from pathlib import Path
from typing import Dict, Optional, Any
import inspect
import ast

from rdagent.components.coder.CoSTEER.task import CoSTEERTask
from rdagent.core.utils import cache_with_pickle


# Because we use isinstance to distinguish between different types of tasks, we need to use sub classes to represent different types of tasks
class EnsembleTask(CoSTEERTask):
    pass


def check_python313_compatibility(code: str) -> tuple[bool, list]:
    """
    Check if a given Python code string is compatible with Python 3.13.

    Args:
        code: The Python code string to check.

    Returns:
        A tuple containing:
            - A boolean indicating if the code is compatible.
            - A list of strings describing any incompatibility issues found.
    """
    incompatibilities = []
    compatible = True

    try:
        # Attempt to parse the code into an AST
        ast_tree = ast.parse(code)

        # Check for specific syntax or features known to be incompatible with 3.13
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Await):
                # Async related feature checks (example)
                incompatibilities.append("Potential incompatibility: `await` expression found. Check if it's used correctly in the context of 3.13.")
                compatible = False
            elif isinstance(node, ast.FormattedValue) and node.conversion != -1:
                incompatibilities.append(
                    "Potential incompatibility: f-string conversion flags (e.g., !r, !s, !a) are deprecated in 3.13."
                )
                compatible = False
            elif isinstance(node, ast.Try) and hasattr(node, 'orelse'):
                incompatibilities.append(
                    "Potential incompatibility: The orelse block within the try-except statement is not recommended. Please revise the code"
                )
                compatible = False
            elif isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.AsyncFor) or isinstance(node, ast.AsyncWith):
                 incompatibilities.append(
                     "Potential incompatibility: Async functions and statements require special treatment in Python 3.13. Ensure correct usage."
                 )
                 compatible = False


    except SyntaxError as e:
        incompatibilities.append(f"Syntax error: {e}")
        compatible = False
    except Exception as e:
        incompatibilities.append(f"Other parsing error: {e}")
        compatible = False

    return compatible, incompatibilities


def check_compatibility_in_file(file_path: str) -> tuple[bool, list]:
    """
    Check the Python code in a file for compatibility with Python 3.13.

    Args:
        file_path: The path to the Python file.

    Returns:
        A tuple: (is_compatible, incompatibility_messages).
    """
    try:
        with open(file_path, "r") as f:
            code = f.read()
        return check_python313_compatibility(code)
    except FileNotFoundError:
        return False, [f"File not found: {file_path}"]
    except Exception as e:
        return False, [f"Error reading file: {file_path} - {e}"]


