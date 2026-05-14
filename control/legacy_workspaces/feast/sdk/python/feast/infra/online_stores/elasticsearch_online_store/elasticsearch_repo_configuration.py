# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from tests.integration.feature_repos.integration_test_repo_config import (
    IntegrationTestRepoConfig,
)
from tests.integration.feature_repos.universal.online_store.elasticsearch import (
    ElasticSearchOnlineStoreCreator,
)

FULL_REPO_CONFIGS = [
    IntegrationTestRepoConfig(
        online_store="elasticsearch",
        online_store_creator=ElasticSearchOnlineStoreCreator,
    ),
]
