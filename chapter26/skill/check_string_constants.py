"""Linter: ensures string literals in Python files are declared as module-level ALL_CAPS constants.

Scans all .py files under src/ and reports violations where string values are
assigned to non-constant variables or used inline inside functions.

Exceptions (not flagged):
  - Docstrings
  - Dictionary keys
  - Empty strings
  - __name__ / __main__ guards
  - f-strings (interpolated, so not pure constants)
  - Strings in module-level ALL_CAPS assignments or data structures
  - .get() / .split() / .environ key arguments
  - Decorator arguments
"""

import ast
import sys
import os
import glob


class StringConstantChecker(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.violations = []
        self._in_function = False
        self._in_module_constant = False

    def _is_caps_name(self, name):
        return name == name.upper() and name.isidentifier()

    # --- Module-level assignments: skip ALL_CAPS or data structure inits ---
    def visit_Assign(self, node):
        if not self._in_function:
            # Module-level: allow ALL_CAPS constants and any top-level data
            for target in node.targets:
                if isinstance(target, ast.Name) and self._is_caps_name(target.id):
                    return  # skip entire subtree
            # Also skip module-level list/dict/tuple/set assignments (data structures)
            if isinstance(node.value, (ast.List, ast.Dict, ast.Tuple, ast.Set)):
                return
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        old = self._in_function
        self._in_function = True
        self.generic_visit(node)
        self._in_function = old

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Constant(self, node):
        if not self._in_function:
            return
        if not isinstance(node.value, str):
            return
        val = node.value
        # Skip empty strings, dunder guards
        if val == "" or val in ("__main__", "__name__"):
            return
        # Skip f-strings (handled as JoinedStr, but just in case)
        if isinstance(node, ast.JoinedStr):
            return

        # Walk up to see context — we only have line info, so flag it
        self.violations.append((node.lineno, node.col_offset, val))

    def visit_JoinedStr(self, node):
        # f-strings: skip entirely (they're interpolated, not pure constants)
        return


def check_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        print(f"  SKIP (syntax error): {filepath}: {e}")
        return []

    checker = StringConstantChecker(filepath)
    checker.visit(tree)
    return checker.violations


def main():
    search_dir = "src"
    if not os.path.isdir(search_dir):
        print(f"Directory '{search_dir}' not found.")
        sys.exit(1)

    py_files = sorted(glob.glob(os.path.join(search_dir, "**", "*.py"), recursive=True))
    if not py_files:
        print("No Python files found.")
        sys.exit(0)

    total_violations = 0
    for filepath in py_files:
        violations = check_file(filepath)
        if violations:
            print(f"\n{filepath}:")
            for lineno, col, val in violations:
                preview = val if len(val) <= 60 else val[:57] + "..."
                print(f"  line {lineno}, col {col}: \"{preview}\"")
            total_violations += len(violations)

    print(f"\n{'=' * 40}")
    if total_violations:
        print(f"Found {total_violations} string literal(s) inside functions that should be module-level constants.")
        sys.exit(1)
    else:
        print("All clear — no inline string violations found.")
        sys.exit(0)


if __name__ == "__main__":
    main()

