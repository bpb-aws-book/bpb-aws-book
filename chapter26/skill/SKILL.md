# Python Code Review

Review Python modules for code quality, security, and best practices.

## Checklist

### 1. String Constants
- All string literals inside functions must be declared as module-level ALL_CAPS constants at the top of the file (after imports)
- Exceptions: docstrings, dict keys, empty strings, f-strings, `__name__`/`__main__` guards, type hints
- Run the enforcement script to detect violations:
  ```bash
  python check_string_constants.py
  ```
- The script scans all `.py` files under `src/` and reports inline string assignments that should be extracted
- Fix any violations by moving strings to module-level constants with ALL_CAPS names

### 2. Error Handling
- No bare `except:` — always catch specific exceptions
- Avoid silencing errors with `except: pass`
- Lambda handlers should catch unexpected exceptions and return a proper error response

### 3. Type Safety
- Function parameters and return types should have type hints
- Avoid `Any` unless truly necessary

### 4. Security
- No hardcoded secrets, tokens, or credentials
- Environment variables for sensitive config (`os.environ`)
- No `eval()`, `exec()`, or `__import__()` with user input
- Input validation on all external data (event params, query strings)

### 5. Structure
- Functions should be under 30 lines
- No more than 3 levels of nesting
- Related constants grouped together at the top of the file
- Imports sorted: stdlib, third-party, local

### 6. Lambda-Specific
- Handlers should follow the `(event, context)` signature
- Responses must include `statusCode`, `headers` (with CORS), and JSON `body`
- Cold start considerations: keep module-level code minimal
- No blocking I/O without timeouts

## How to Review

1. Read the module
2. Run `python check_string_constants.py` for string constant violations
3. Walk through each checklist item above
4. Report findings grouped by severity: critical, warning, suggestion
5. Offer to fix any issues found

