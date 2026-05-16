# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from enum import Enum


class DAGFormat(str, Enum):
    SPARK = "spark"
    PANDAS = "pandas"
    ARROW = "arrow"
    RAY = "ray"
