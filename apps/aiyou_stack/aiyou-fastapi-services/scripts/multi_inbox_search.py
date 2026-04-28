# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import argparse
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Scopes required for the search
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_service(subject_email, credentials_path):
    """Authenticates as the Service Account and then 'impersonates' (delegates to)
    the subject_email using Domain-Wide Delegation.
    """
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

    try:
        # Load Service Account Credentials
        creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=SCOPES,
        )

        # Create a delegated credential for the specific user
        delegated_creds = creds.with_subject(subject_email)

        # Build the Gmail Service
        return build("gmail", "v1", credentials=delegated_creds)
    except Exception as e:
        print(f"❌ Auth Error for {subject_email}: {e}")
        return None


def search_inbox(service, target_email, query):
    print(f"\n🔍 Searching inbox: {target_email}")
    print(f"   Query: '{query}'")

    hits = []
    try:
        # Include Spam/Trash to be thorough
        results = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=50, includeSpamTrash=True)
            .execute()
        )

        messages = results.get("messages", [])
        print(f"   Found {len(messages)} matching threads.")

        for msg in messages:
            txt = service.users().messages().get(userId="me", id=msg["id"]).execute()
            payload = txt.get("payload", {})
            headers = payload.get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            snippet = txt.get("snippet", "")

            print(f"   - Match: {subject} ({sender})")
            hits.append(f"**[{target_email}]** {subject}\nFrom: {sender}\nSnippet: {snippet}\n")

    except Exception as e:
        print(f"⚠️  Search failed for {target_email}: {e}")
        hits.append(f"ERROR searching {target_email}: {e!s}\n")

    return hits


def main():
    parser = argparse.ArgumentParser(description="Antigravity Multi-Inbox Search")
    parser.add_argument(
        "--targets",
        nargs="+",
        help="List of email addresses to search",
        required=True,
    )
    parser.add_argument("--query", help="Gmail search query", required=True)
    parser.add_argument(
        "--creds",
        help="Path to Service Account JSON",
        default="credentials/service_account.json",
    )
    parser.add_argument(
        "--output",
        help="Output file for results",
        default="multi_search_results.md",
    )

    args = parser.parse_args()

    all_results = []
    all_results.append(f"# Antigravity Search Results\nQuery: `{args.query}`\n")

    print("🚀 Initiating Antigravity Multi-Inbox Search Protocol...")

    for target in args.targets:
        service = get_service(target, args.creds)
        if service:
            results = search_inbox(service, target, args.query)
            all_results.extend(results)
        else:
            all_results.append(f"❌ Authentication Failed for {target}\n")

    # Save Results
    with open(args.output, "w") as f:
        f.writelines(all_results)

    print(f"\n✅ Search Complete. Results saved to {args.output}")


if __name__ == "__main__":
    main()
