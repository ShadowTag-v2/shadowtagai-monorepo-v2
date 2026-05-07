import re
import subprocess
import json


def fix_file(filepath, line_no):
    with open(filepath) as f:
        lines = f.readlines()

    idx = line_no - 1
    # Check if this line is `raise SystemExit(1)` or similar
    line = lines[idx]
    if "raise SystemExit(1)" in line:
        # Search backwards for `except`
        var_name = None
        for i in range(idx, max(-1, idx - 20), -1):
            m = re.search(r"except\s+.*?\s+as\s+(\w+):", lines[i])
            if m:
                var_name = m.group(1)
                break
            m = re.search(r"except\s+.*?:", lines[i])
            if m:
                var_name = "None"
                break

        if var_name == "None":
            lines[idx] = line.replace("raise SystemExit(1)", "raise SystemExit(1) from None")
        elif var_name:
            lines[idx] = line.replace("raise SystemExit(1)", f"raise SystemExit(1) from {var_name}")

        with open(filepath, "w") as f:
            f.writelines(lines)


result = subprocess.run(["ruff", "check", "--output-format=json"], capture_output=True, text=True)
if not result.stdout:
    print("No stdout from ruff:", result.stderr)
else:
    data = json.loads(result.stdout)
    for err in sorted(data, key=lambda x: x["location"]["row"], reverse=True):
        if err["code"] == "B904":
            fix_file(err["filename"], err["location"]["row"])

print("Done fixing B904.")
