import json
import subprocess


def fix_f821():
    for _ in range(5):
        result = subprocess.run(["ruff", "check", "--output-format=json"], capture_output=True, text=True)
        if result.returncode == 0:
            print("All linting issues resolved!")
            break

        data = json.loads(result.stdout)
        files_to_fix = set()
        for err in data:
            if err["code"] == "F821" and err["message"] == "Undefined name `os`":
                files_to_fix.add(err["filename"])

        if not files_to_fix:
            print("No F821 'os' errors found. Exiting loop.")
            break

        for fp in files_to_fix:
            with open(fp) as f:
                content = f.read()
            if "import os" not in content:
                with open(fp, "w") as f:
                    f.write("import os\n" + content)
        print(f"Fixed {len(files_to_fix)} files.")


if __name__ == "__main__":
    fix_f821()
