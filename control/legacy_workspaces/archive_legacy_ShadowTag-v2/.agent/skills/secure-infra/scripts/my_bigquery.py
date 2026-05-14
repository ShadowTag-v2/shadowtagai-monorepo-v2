import sys
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError


def run_query(query_string):
    """
    Executes a BigQuery SQL query using the native Google Cloud python client.
    Requires `pip install google-cloud-bigquery` and Application Default Credentials.
    """
    try:
        # Initialize the BigQuery client. It will automatically use the Application Default Credentials
        # specified by GCLOUD or the GOOGLE_APPLICATION_CREDENTIALS env var.
        client = bigquery.Client()

        print(f"Executing Query: {query_string}")
        query_job = client.query(query_string)

        # Wait for the query to finish
        results = query_job.result()

        print("--- BIGQUERY RESULTS ---")
        for row in results:
            print(dict(row))

    except GoogleAPIError as e:
        print("--- BIGQUERY ERROR ---")
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 my_bigquery.py "<SQL_QUERY>"')
        print('Example: python3 my_bigquery.py "SELECT * FROM `my_project.my_dataset.my_table` LIMIT 10"')
        sys.exit(1)

    query_string = sys.argv[1]
    run_query(query_string)


if __name__ == "__main__":
    main()
