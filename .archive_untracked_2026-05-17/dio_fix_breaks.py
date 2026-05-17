import re
import subprocess


def fix_switch_cases(filepath):
  with open(filepath, "r") as f:
    lines = f.readlines()

  result = subprocess.run(["dart", "analyze", filepath], capture_output=True, text=True)

  pattern = re.compile(
    r"interceptor_test\.dart:(\d+):\d+ - The \'case\' shouldn\'t complete normally"
  )

  case_lines = []
  for match in pattern.finditer(result.stdout + result.stderr):
    case_lines.append(int(match.group(1)))

  if not case_lines:
    print("No switch case errors found.")
    return

  print(f"Found switch case errors at lines: {case_lines}")

  insertions = {}

  for cl in sorted(set(case_lines)):
    # 1-based index in dart analyzer -> 0-based index in python
    # But wait, we need to find the NEXT case statement AFTER this case statement's code.
    # So we start searching from `cl` (which corresponds to line `cl+1` in file, wait, no, `cl` is 1-based, so its index is `cl-1`).
    # The code for this case is between `cl` and the next case.
    for i in range(cl, len(lines)):
      line = lines[i].strip()
      if line.startswith("case ") or line.startswith("default:") or line == "}":
        # calculate indentation of the next case/default/brace
        indent = len(lines[i]) - len(lines[i].lstrip())
        # Add an extra level of indentation (typically 2 spaces for a break inside a switch, or just match the case indent + 2)
        insertions[i] = " " * (indent + 2) + "break;\n"
        break

  for idx in sorted(insertions.keys(), reverse=True):
    lines.insert(idx, insertions[idx])

  with open(filepath, "w") as f:
    f.writelines(lines)

  print(f"Inserted {len(insertions)} breaks.")


if __name__ == "__main__":
  fix_switch_cases("test/interceptor_test.dart")
