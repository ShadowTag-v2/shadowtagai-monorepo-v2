# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Vertex AI Vector Search Manager
Manages vector search index creation, deployment, and querying
"""

import logging
from typing import Any
from dataclasses import dataclass
from google.cloud import aiplatform
from google.cloud.aiplatform import MatchingEngineIndex, MatchingEngineIndexEndpoint

from pnkln_intelligence.config import GCPSettings

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result"""

    id: str
    distance: float
    metadata: dict[str, Any]


class VectorSearchManager:
    """
    Manages Vertex AI Vector Search indexes and endpoints

    Features:
    - Create and manage TreeAH indexes
    - Deploy indexes to endpoints with HA
    - Perform similarity searches
    - Batch index updates
    - Monitor index health
    """

    def __init__(self, settings: GCPSettings | None = None):
        self.settings = settings or GCPSettings()

        # Initialize Vertex AI
        aiplatform.init(project=self.settings.project_id, location=self.settings.location)

        self.index = None
        self.index_endpoint = None

    async def create_index(
        self,
        display_name: str | None = None,
        contents_delta_uri: str | None = None,
        dimensions: int | None = None,
        approximate_neighbors_count: int = 150,
        distance_measure_type: str = "DOT_PRODUCT_DISTANCE",
        leaf_node_embedding_count: int = 1000,
        leaf_nodes_to_search_percent: int = 7,
        description: str = "Code embeddings vector search index",
    ) -> MatchingEngineIndex:
        """
        Create a new Vertex AI vector search index

        Args:
            display_name: Index display name
            contents_delta_uri: GCS URI for embeddings
            dimensions: Embedding dimensions
            approximate_neighbors_count: Number of approximate neighbors
            distance_measure_type: Distance metric (DOT_PRODUCT_DISTANCE, COSINE_DISTANCE)
            leaf_node_embedding_count: Embeddings per leaf node
            leaf_nodes_to_search_percent: Percentage of leaf nodes to search
            description: Index description

        Returns:
            MatchingEngineIndex object
        """
        display_name = display_name or self.settings.vertex_ai_index_display_name
        dimensions = dimensions or self.settings.vertex_ai_embedding_dimensions
        contents_delta_uri = contents_delta_uri or f"gs://{self.settings.gcs_bucket_processed}/embeddings/"

        logger.info(f"Creating Vertex AI index: {display_name}")

        # Create TreeAH index configuration
        tree_ah_config = aiplatform.matching_engine.matching_engine_index_config.MatchingEngineIndexConfig(
            dimensions=dimensions,
            approximate_neighbors_count=approximate_neighbors_count,
            distance_measure_type=distance_measure_type,
            algorithm_config=aiplatform.matching_engine.matching_engine_index_config.TreeAhConfig(
                leaf_node_embedding_count=leaf_node_embedding_count, leaf_nodes_to_search_percent=leaf_nodes_to_search_percent
            ),
        )

        # Create index
        index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=display_name,
            contents_delta_uri=contents_delta_uri,
            dimensions=dimensions,
            approximate_neighbors_count=approximate_neighbors_count,
            distance_measure_type=distance_measure_type,
            leaf_node_embedding_count=leaf_node_embedding_count,
            leaf_nodes_to_search_percent=leaf_nodes_to_search_percent,
            description=description,
            labels={"component": "code-search", "environment": "production"},
        )

        logger.info(f"Index created: {index.resource_name}")
        self.index = index
        return index

    async def create_index_endpoint(
        self, display_name: str | None = None, public_endpoint_enabled: bool = True, description: str = "Code search vector endpoint"
    ) -> MatchingEngineIndexEndpoint:
        """
        Create index endpoint for serving queries

        Args:
            display_name: Endpoint display name
            public_endpoint_enabled: Enable public endpoint
            description: Endpoint description

        Returns:
            MatchingEngineIndexEndpoint object
        """
        display_name = display_name or self.settings.vertex_ai_endpoint_display_name

        logger.info(f"Creating index endpoint: {display_name}")

        endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
            display_name=display_name,
            public_endpoint_enabled=public_endpoint_enabled,
            description=description,
            labels={"component": "code-search", "environment": "production"},
        )

        logger.info(f"Endpoint created: {endpoint.resource_name}")
        self.index_endpoint = endpoint
        return endpoint

    async def deploy_index(
        self,
        index: MatchingEngineIndex | None = None,
        index_endpoint: MatchingEngineIndexEndpoint | None = None,
        deployed_index_id: str = "code-search-v1",
        machine_type: str | None = None,
        min_replica_count: int | None = None,
        max_replica_count: int | None = None,
    ) -> None:
        """
        Deploy index to endpoint

        Args:
            index: Index to deploy
            index_endpoint: Endpoint to deploy to
            deployed_index_id: Deployed index ID
            machine_type: Machine type for deployment
            min_replica_count: Minimum replicas
            max_replica_count: Maximum replicas
        """
        index = index or self.index
        index_endpoint = index_endpoint or self.index_endpoint
        machine_type = machine_type or self.settings.vertex_ai_machine_type
        min_replica_count = min_replica_count or self.settings.vertex_ai_min_replicas
        max_replica_count = max_replica_count or self.settings.vertex_ai_max_replicas

        if not index or not index_endpoint:
            raise ValueError("Index and endpoint must be created before deployment")

        logger.info(f"Deploying index {index.display_name} to endpoint {index_endpoint.display_name}")

        index_endpoint.deploy_index(
            index=index,
            deployed_index_id=deployed_index_id,
            display_name=deployed_index_id,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            enable_access_logging=True,
        )

        logger.info(f"Index deployed successfully: {deployed_index_id}")

    async def search(self, query_embedding: list[float], num_neighbors: int = 10, deployed_index_id: str = "code-search-v1") -> list[SearchResult]:
        """
        Search for nearest neighbors

        Args:
            query_embedding: Query embedding vector
            num_neighbors: Number of neighbors to return
            deployed_index_id: Deployed index ID

        Returns:
            List of SearchResult objects
        """
        if not self.index_endpoint:
            raise ValueError("Index endpoint not initialized")

        logger.debug(f"Searching for {num_neighbors} nearest neighbors")

        # Perform search
        response = self.index_endpoint.find_neighbors(deployed_index_id=deployed_index_id, queries=[query_embedding], num_neighbors=num_neighbors)

        results = []
        for neighbor_list in response:
            for neighbor in neighbor_list:
                results.append(
                    SearchResult(
                        id=neighbor.id,
                        distance=neighbor.distance,
                        metadata={},  # Metadata needs to be fetched from BigQuery
                    )
                )

        logger.info(f"Found {len(results)} results")
        return results

    async def batch_search(
        self, query_embeddings: list[list[float]], num_neighbors: int = 10, deployed_index_id: str = "code-search-v1"
    ) -> list[list[SearchResult]]:
        """
        Perform batch search for multiple queries

        Args:
            query_embeddings: List of query embedding vectors
            num_neighbors: Number of neighbors per query
            deployed_index_id: Deployed index ID

        Returns:
            List of lists of SearchResult objects
        """
        if not self.index_endpoint:
            raise ValueError("Index endpoint not initialized")

        logger.debug(f"Batch searching {len(query_embeddings)} queries")

        response = self.index_endpoint.find_neighbors(deployed_index_id=deployed_index_id, queries=query_embeddings, num_neighbors=num_neighbors)

        all_results = []
        for neighbor_list in response:
            results = []
            for neighbor in neighbor_list:
                results.append(SearchResult(id=neighbor.id, distance=neighbor.distance, metadata={}))
            all_results.append(results)

        logger.info(f"Completed batch search for {len(query_embeddings)} queries")
        return all_results

    async def update_index(self, contents_delta_uri: str, is_complete_overwrite: bool = False) -> None:
        """
        Update index with new embeddings

        Args:
            contents_delta_uri: GCS URI with new/updated embeddings
            is_complete_overwrite: Whether to completely overwrite index
        """
        if not self.index:
            raise ValueError("Index not initialized")

        logger.info(f"Updating index with data from {contents_delta_uri}")

        self.index.update_embeddings(contents_delta_uri=contents_delta_uri, is_complete_overwrite=is_complete_overwrite)

        logger.info("Index update completed")

    def get_index(self, index_name: str) -> MatchingEngineIndex:
        """Get existing index by name"""
        index = aiplatform.MatchingEngineIndex(index_name=index_name)
        self.index = index
        return index

    def get_endpoint(self, endpoint_name: str) -> MatchingEngineIndexEndpoint:
        """Get existing endpoint by name"""
        endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=endpoint_name)
        self.index_endpoint = endpoint
        return endpoint

    def list_indexes(self) -> list[MatchingEngineIndex]:
        """List all indexes in the project"""
        return aiplatform.MatchingEngineIndex.list()

    def list_endpoints(self) -> list[MatchingEngineIndexEndpoint]:
        """List all index endpoints in the project"""
        return aiplatform.MatchingEngineIndexEndpoint.list()


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        manager = VectorSearchManager()

        # Create index
        # index = await manager.create_index(
        #     display_name="pnkln-code-search",
        #     dimensions=1536
        # )

        # Create endpoint
        # endpoint = await manager.create_index_endpoint(
        #     display_name="pnkln-code-endpoint"
        # )

        # Deploy index
        # await manager.deploy_index()

        # Search
        # query_embedding = [0.1] * 1536  # Example embedding
        # results = await manager.search(query_embedding, num_neighbors=10)

        # for result in results:
        #     print(f"ID: {result.id}, Distance: {result.distance}")

        # List indexes
        indexes = manager.list_indexes()
        print(f"Found {len(indexes)} indexes")
        for idx in indexes:
            print(f"- {idx.display_name} ({idx.resource_name})")

    asyncio.run(main())
