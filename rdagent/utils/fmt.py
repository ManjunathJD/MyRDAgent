"""
Tools that support generating better formats.
"""

from typing import List
def shrink_text(text: str, context_lines: int = 200, line_len: int = 5000) -> str:
    """
    When the context is too long, hide the part in the middle.

    >>> shrink_text("line1\\nline2\\nline3", context_lines=2, line_len=5)
    'line1\\n... (1 lines are hidden) ...\\nline3'

    >>> shrink_text("short line", context_lines=2, line_len=5)
    'sh... (5 chars are hidden) ...ine'

    >>> shrink_text("a" * 5010, context_lines=2, line_len=10)
    'aaaaa... (5000 chars are hidden) ...aaaaa'
    """

    lines: List[str] = text.splitlines()
    total_lines: int = len(lines)

    new_lines: List[str] = []
    for line in lines:
        if len(line) > line_len:
            # If any line is longer than line_len, we can't shrink it
            line = f"{line[:line_len // 2]}... ({len(line) - line_len} chars are hidden) ...{line[- line_len + line_len // 2:]}"
        new_lines.append(line) # type: ignore
    lines = new_lines

    if total_lines <= context_lines:
        return "\n".join(lines)

    # Calculate how many lines to show from start and end
    half_lines = context_lines // 2
    start: str = "\n".join(lines[:half_lines])
    end: str = "\n".join(lines[-half_lines:])

    # Count the number of lines we're hiding
    hidden_lines: int = total_lines - half_lines * 2

    return f"{start}\n... ({hidden_lines} lines are hidden) ...\n{end}"
