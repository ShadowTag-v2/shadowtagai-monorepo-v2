"""Simple example of using the Vertex AI RAG Service"""

import json

import requests

# Service URL
BASE_URL = "http://localhost:8000"

# Example document (abbreviated HIPAA regulation)
SAMPLE_DOCUMENT = """
HIPAA Privacy Rule

The HIPAA Privacy Rule establishes national standards to protect individuals' medical records
and other personal health information (PHI).

Storage Requirements:
1. Covered entities must implement administrative, physical, and technical safeguards to ensure
   the confidentiality, integrity, and security of electronic protected health information (ePHI).

2. Physical safeguards include facility access controls, workstation security, and device and
   media controls. All storage devices must be properly secured and encrypted.

3. Technical safeguards require access controls, audit controls, integrity controls, and
   transmission security. Encryption of ePHI at rest and in transit is strongly recommended.

4. Administrative safeguards include security management processes, workforce security procedures,
   and information access management policies.

Retention Requirements:
- Medical records must be retained for a minimum of 6 years from the date of creation or
  the date when it last was in effect, whichever is later.

Breach Notification:
- Covered entities must notify affected individuals within 60 days of discovering a breach
  of unsecured PHI affecting 500 or more individuals.
"""

# Example query
QUERY = "What are the HIPAA requirements for patient data storage?"


def test_simple_query():
    """Test basic RAG query"""
    print("=" * 80)
    print("SIMPLE QUERY TEST")
    print("=" * 80)

    response = requests.post(
        f"{BASE_URL}/query",
        json={
            "query": QUERY,
            "context": SAMPLE_DOCUMENT,
            "document_id": "hipaa_privacy_rule",
            "vertical": "healthcare_compliance",
        },
    )

    result = response.json()

    print(f"\nQuery: {QUERY}")
    print(f"\nAnswer: {result['answer']}")
    print(f"\nMethod: {result['method']}")
    print(f"Tokens Used: {result['tokens_used']}")
    print(f"Confidence: {result['confidence']}")
    print(f"\nMetadata: {json.dumps(result['metadata'], indent=2)}")


def test_vertical_list():
    """List all available verticals"""
    print("\n" + "=" * 80)
    print("AVAILABLE VERTICALS")
    print("=" * 80)

    response = requests.get(f"{BASE_URL}/verticals")
    data = response.json()

    print(f"\nTotal verticals: {data['total']}\n")

    # Group by cost tier
    cost_tiers = data["cost_tiers"]
    print(f"High-cost (Pro): {len(cost_tiers['high_cost_pro'])} verticals")
    print(f"Standard-cost (Flash): {len(cost_tiers['standard_cost_flash'])} verticals")

    print("\nSample verticals:")
    for vertical in data["verticals"][:5]:
        print(f"  - {vertical['name']}: k={vertical['k']}, model={vertical['model']}")


def test_stats():
    """Get routing statistics"""
    print("\n" + "=" * 80)
    print("ROUTING STATISTICS")
    print("=" * 80)

    response = requests.get(f"{BASE_URL}/stats")
    stats = response.json()

    print(f"\nTotal Queries: {stats['total_queries']}")
    print(f"RAG Routes: {stats['rag_routes']} ({stats['rag_percentage']:.1f}%)")
    print(f"LC Routes: {stats['lc_routes']} ({stats['lc_percentage']:.1f}%)")
    print(f"Forced LC: {stats['forced_lc']} ({stats['forced_lc_percentage']:.1f}%)")
    print(f"Avg Tokens/Query: {stats['avg_tokens_per_query']:.0f}")
    print(f"Avg Latency: {stats['avg_latency']:.2f}s")


def test_multi_hop_query():
    """Test multi-hop reasoning query"""
    print("\n" + "=" * 80)
    print("MULTI-HOP REASONING TEST")
    print("=" * 80)

    # Complex multi-hop query
    query = "How long must breach notification records be retained after a breach affecting 600 individuals?"

    response = requests.post(
        f"{BASE_URL}/query",
        json={
            "query": query,
            "context": SAMPLE_DOCUMENT,
            "document_id": "hipaa_privacy_rule",
            "vertical": "healthcare_compliance",
            "k": 10,  # Use higher k for complex queries
        },
    )

    result = response.json()

    print(f"\nQuery: {query}")
    print(f"\nAnswer: {result['answer']}")
    print(f"Method: {result['method']} (Note: complex queries may route to LC)")


if __name__ == "__main__":
    try:
        # Check service health
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code != 200:
            print("ERROR: Service is not healthy")
            print("Make sure the service is running: uvicorn src.api.main:app --reload")
            exit(1)

        # Run tests
        test_simple_query()
        test_vertical_list()
        test_stats()
        test_multi_hop_query()

        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED")
        print("=" * 80)

    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to service")
        print("Make sure the service is running: uvicorn src.api.main:app --reload")
    except Exception as e:
        print(f"ERROR: {e}")
