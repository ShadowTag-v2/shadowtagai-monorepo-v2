import json
import logging

import functions_framework
from retriever import search_knowledge_base

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KB-Retriever")


@functions_framework.http
def retrieve(request):
    """
    HTTP Cloud Function to query the Knowledge Base.
    Expects JSON: {"query": "string"}
    """
    try:
        request_json = request.get_json(silent=True)

        if not request_json or "query" not in request_json:
            return (
                json.dumps({"error": "Missing 'query' parameter"}),
                400,
                {"Content-Type": "application/json"},
            )

        query = request_json["query"]
        logger.info(f"Searching Knowledge Base for: {query}")

        results = search_knowledge_base(query)

        return (json.dumps(results), 200, {"Content-Type": "application/json"})

    except Exception as e:
        logger.error(f"Retrieval Error: {e}")
        return (json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"})
