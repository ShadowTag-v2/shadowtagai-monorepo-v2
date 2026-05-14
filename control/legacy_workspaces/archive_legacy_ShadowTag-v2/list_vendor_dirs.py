# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os

vendor_path = "/Users/pikeymickey/aiyou-stack/ShadowTag-v2/vendor"
try:
    dirs = [d for d in os.listdir(vendor_path) if os.path.isdir(os.path.join(vendor_path, d))]
    print(dirs)
except FileNotFoundError:
    print([])
