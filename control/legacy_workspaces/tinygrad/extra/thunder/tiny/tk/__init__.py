# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from tinygrad.device import Device

if Device.DEFAULT == "AMD":
  WARP_THREADS = 64
else:
  WARP_THREADS = 32
