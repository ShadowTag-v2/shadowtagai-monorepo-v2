import sys
import os
import json
import fcntl

# A robust, local JSON-based Key-Value memory store.
# Uses fcntl for file locking to prevent corruption under concurrent agent writes,
# directly addressing the "shatter under concurrent writes" issue of standard memory MCPs.

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".beads", "agent_memory.json")


def ensure_file_exists():
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)


def read_memory():
    ensure_file_exists()
    with open(MEMORY_FILE) as f:
        # Acquire a shared lock
        fcntl.flock(f, fcntl.LOCK_SH)
        try:
            data = json.load(f)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return data


def write_memory(data):
    ensure_file_exists()
    with open(MEMORY_FILE, "r+") as f:
        # Acquire an exclusive lock
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 my_memory.py --get <key>")
        print("  python3 my_memory.py --set <key> <value>")
        print("  python3 my_memory.py --delete <key>")
        print("  python3 my_memory.py --list")
        sys.exit(1)

    action = sys.argv[1]

    if action == "--list":
        data = read_memory()
        print(json.dumps(data, indent=2))
        return

    key = sys.argv[2]

    if action == "--get":
        data = read_memory()
        value = data.get(key)
        if value is not None:
            print(value)
        else:
            print(f"Key '{key}' not found.")
            sys.exit(1)

    elif action == "--set":
        if len(sys.argv) < 4:
            print("Missing value for --set")
            sys.exit(1)
        value = sys.argv[3]

        # Try to parse value as JSON if possible, otherwise store as string
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass

        data = read_memory()
        data[key] = value
        write_memory(data)
        print(f"SUCCESS: Stored '{key}'")

    elif action == "--delete":
        data = read_memory()
        if key in data:
            del data[key]
            write_memory(data)
            print(f"SUCCESS: Deleted '{key}'")
        else:
            print(f"Key '{key}' not found.")

    else:
        print(f"Unknown action: {action}")


if __name__ == "__main__":
    main()
