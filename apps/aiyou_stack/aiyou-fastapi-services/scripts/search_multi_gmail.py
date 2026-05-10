import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes for Gmail functionality
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Token files for multiple accounts
TOKEN_FILES = ["credentials/gmail_token.json", "credentials/gmail_token_secondary.json"]
CLIENT_SECRET_FILE = "credentials/client_secret.json"


def get_gmail_service(token_file, account_name="Primary"):
    creds = None
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception:
            print(f"⚠️  Token {token_file} is invalid.")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f"🔄 Refreshing token for {account_name}...")
            creds.refresh(Request())
        else:
            print(f"🔑 Authenticating {account_name} Account...")
            print(f"   (Please verify the '{account_name}' account in the browser pop-up)")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            # Use different ports to avoid conflicts? flow usually handles random port or 8080.
            # Always use 8080 as it's likely the only whitelisted Redirect URI
            port = 8080
            creds = flow.run_local_server(port=port)

        # Save the credentials
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def search_account(service, account_name):
    # 1. DUMP ALL LABELS (No Filtering)
    print(f"\n📂 DUMPING ALL LABELS for {account_name}...")
    try:
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        notes_label_id = None
        for label in labels:
            print(f"   - Label: {label['name']} | ID: {label['id']} | Type: {label['type']}")
            if "note" in label["name"].lower():
                notes_label_id = label["id"]
                print(f"     ✅ MATCH FOUND: {label['name']} ({label['id']})")
    except Exception as e:
        print(f"   ⚠️ Could not list labels: {e}")

    # 2. Search Focused on Found Label OR Broad
    query = "rollup"  # Simple query matching user screenshot
    print(f"\nExample Query: {query}")

    if notes_label_id:
        print(f"\n🔍 Searching Specific Label: {notes_label_id}...")
        label_ids = [notes_label_id]
    else:
        print("\n🔍 Searching Global (No Label Filter)...")
        label_ids = []

    try:
        results = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                labelIds=label_ids or None,
                maxResults=50,
                includeSpamTrash=True,
            )
            .execute()
        )
        messages = results.get("messages", [])

        print(f"   Found {len(messages)} potential matches.")

        hits = []
        for msg in messages:
            txt = service.users().messages().get(userId="me", id=msg["id"]).execute()
            payload = txt["payload"]
            headers = payload.get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            snippet = txt.get("snippet", "")

            print(f"   - [{account_name}] Found: {subject}")
            hits.append(f"[{account_name}] {subject}: {snippet}")

        return hits
    except Exception as e:
        print(f"❌ Error searching {account_name}: {e}")
        return []


def main():
    if not os.path.exists(CLIENT_SECRET_FILE):
        print("❌ Client Secret not found. Please add 'credentials/client_secret.json'.")
        return

    all_hits = []

    # 1. Primary Account (Existing)
    print("--- 1. Processing Primary Account ---")
    service1 = get_gmail_service(TOKEN_FILES[0], "Primary (ehanc69)")
    all_hits.extend(search_account(service1, "Primary"))

    # 2. Secondary Account (New)
    print("\n--- 2. Processing Secondary Account ---")
    print(
        "ℹ️  To search a second account, you will need to authenticate in the browser window that opens.",
    )
    try:
        service2 = get_gmail_service(TOKEN_FILES[1], "Secondary")
        all_hits.extend(search_account(service2, "Secondary"))
    except Exception as e:
        print(f"⚠️  Skipping Secondary Account (Auth failed or cancelled): {e}")

    # Output
    with open("ingested_biz_plans.md", "w") as f:
        f.write("# Ingested Business Plans (Multi-Account)\n\n")
        f.writelines(f"* {hit}\n" for hit in all_hits)

    print(f"\n✅ Scan Complete. Saved {len(all_hits)} items to ingested_biz_plans.md")


if __name__ == "__main__":
    main()
