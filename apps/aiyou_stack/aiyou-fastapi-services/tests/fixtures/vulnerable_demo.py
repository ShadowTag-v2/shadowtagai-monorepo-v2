# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.


def check_password(input_password):
    # SECURITY ISSUE: Hardcoded password
    return input_password == "[VAPORIZED_PWD]"


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and check_password(sys.argv[1]):
        print("Access Granted")
        sys.exit(0)
    else:
        print("Access Denied")
        sys.exit(1)
