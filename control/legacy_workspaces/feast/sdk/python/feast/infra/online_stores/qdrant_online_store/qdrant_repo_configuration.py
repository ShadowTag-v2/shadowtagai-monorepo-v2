# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from tests.integration.feature_repos.integration_test_repo_config import (
    IntegrationTestRepoConfig,
)
from tests.integration.feature_repos.universal.online_store.qdrant import (
    QdrantOnlineStoreCreator,
)

FULL_REPO_CONFIGS = [
    IntegrationTestRepoConfig(
        online_store="qdrant", online_store_creator=QdrantOnlineStoreCreator
    ),
]
