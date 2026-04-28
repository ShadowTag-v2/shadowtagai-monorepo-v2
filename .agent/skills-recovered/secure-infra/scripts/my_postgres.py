# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import sys
import os
import json

# We gracefully handle the absence of psycopg2 for now,
# prompting the agent to install it if missing.
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("ERROR: psycopg2 is not installed. Agent must run: pip install psycopg2-binary")
    sys.exit(1)


def get_db_url():
    url = os.environ.get("DATABASE_URL")
    if not url:
        try:
            with open(".env") as f:
                for line in f:
                    if line.startswith("DATABASE_URL="):
                        return line.strip().split("=", 1)[1].strip("\"'")
        except FileNotFoundError:
            pass
    return url


def execute_query(query):
    url = get_db_url()
    if not url:
        print("ERROR: DATABASE_URL environment variable not found in environment or .env file.")
        sys.exit(1)

    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(query)

        # If it's a SELECT returning data
        if cur.description:
            results = cur.fetchall()
            print(json.dumps(results, indent=2, default=str))
        else:
            # If it's an INSERT/UPDATE/DELETE
            conn.commit()
            print(f"SUCCESS: Query executed. Rows affected: {cur.rowcount}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"DATABASE ERROR: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 my_postgres.py "SELECT * FROM users;"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    execute_query(query)


if __name__ == "__main__":
    main()
