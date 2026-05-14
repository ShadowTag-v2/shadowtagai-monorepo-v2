# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import enum


class AuthType(enum.Enum):
    """
    Identify the type of authorization.
    """

    NONE = "no_auth"
    OIDC = "oidc"
    KUBERNETES = "kubernetes"
