import re


def fix_switch_cases(filepath):
  with open(filepath, "r") as f:
    lines = f.readlines()

  # We will identify the lines that analyzer reported
  # interceptor_test.dart:113, 115, 120, 125, 130, 135, 140, 145, 150, 164, 167, 170, 177, 215, 320, 327, 332, 339, 346, 517, 519, 526

  # Actually, a better way is to run dart analyze, parse the lines, and insert 'break;' at the end of the previous line (before the next case/default).

  import subprocess

  result = subprocess.run(["dart", "analyze", filepath], capture_output=True, text=True)

  # parse errors
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

  # For each case line reported, we need to find the next case or default and insert break; before it.
  # The analyzer reports the line of the `case` statement that completes normally.
  # We should search from that line downwards for the next `case` or `default`, or `}`.

  insertions = {}  # line_index_to_insert_before: "break;"

  for cl in sorted(set(case_lines)):
    # find the next case/default/closing brace
    for i in range(cl, len(lines)):
      line = lines[i].strip()
      if line.startswith("case ") or line.startswith("default:") or line == "}":
        # calculate indentation
        indent = len(lines[i]) - len(lines[i].lstrip())
        insertions[i] = " " * indent + "break;\n"
        break

  # apply insertions in reverse order to not mess up line numbers
  for idx in sorted(insertions.keys(), reverse=True):
    lines.insert(idx, insertions[idx])

  with open(filepath, "w") as f:
    f.writelines(lines)

  print(f"Inserted {len(insertions)} breaks.")


fix_switch_cases("test/interceptor_test.dart")
