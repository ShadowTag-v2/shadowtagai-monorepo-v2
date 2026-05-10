"""Fix Python 2 except-comma syntax to Python 3 tuple syntax.

Transforms:
    except E1, E2:        -> except (E1, E2):
    except E1, E2, E3:    -> except (E1, E2, E3):

Does NOT touch:
    except (E1, E2):      -> already correct
    except E as var:      -> already correct
    except E:             -> single exception, no change
"""

import re
from pathlib import Path

# Pattern: except <Exception1>[, <Exception2>[, ...]:
# Must NOT already have parentheses
# Must NOT be `except ... as ...:`
PATTERN = re.compile(
  r"^(\s*)except\s+"  # leading whitespace + except keyword
  r"(?!\()"  # NOT already parenthesized
  r"([A-Za-z_.]+(?:\s*,\s*[A-Za-z_.]+)+)"  # two or more comma-separated exception names
  r"\s*:",  # trailing colon
  re.MULTILINE,
)


def fix_file(path: Path) -> int:
  """Fix all except-comma patterns in a file. Returns count of fixes."""
  text = path.read_text()
  count = 0

  def replacer(m: re.Match) -> str:
    nonlocal count
    indent = m.group(1)
    exceptions = m.group(2)
    count += 1
    return f"{indent}except ({exceptions}):"

  new_text = PATTERN.sub(replacer, text)
  if count > 0:
    path.write_text(new_text)
  return count


def main() -> None:
  roots = [
    Path("packages"),
    Path("scripts"),
    Path("src"),
  ]
  total = 0
  for root in roots:
    if not root.exists():
      continue
    for py_file in sorted(root.rglob("*.py")):
      if "__pycache__" in str(py_file) or ".venv" in str(py_file):
        continue
      fixes = fix_file(py_file)
      if fixes:
        print(f"  Fixed {fixes:2d} in {py_file}")
        total += fixes
  print(f"\nTotal fixes: {total}")


if __name__ == "__main__":
  main()
