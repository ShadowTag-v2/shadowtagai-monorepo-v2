import base64
import os

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scopes (read-only is sufficient for searching)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    # UPDATED: Use the existing token file from previous steps
    token_path = "credentials/gmail_token.json"
    if os.path.exists(token_path):
        try:
            from google.oauth2.credentials import Credentials

            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception:
            creds = None

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/client_secret.json", SCOPES
            )
            # Use fixed port 8080 to match the "Web Application" credentials if needed
            creds = flow.run_local_server(port=8080)

        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service


def search_messages(service, query):
    try:
        # UPDATED: Broaden query and include spam/trash
        # Use simple 'rollup' which should match fuzzy, but let's be explicit
        query = "rollup OR roll-up OR 'roll up'"
        results = (
            service.users().messages().list(userId="me", q=query, includeSpamTrash=True).execute()
        )
        messages = results.get("messages", [])

        while "nextPageToken" in results:
            page_token = results["nextPageToken"]
            results = (
                service.users()
                .messages()
                .list(userId="me", q=query, pageToken=page_token, includeSpamTrash=True)
                .execute()
            )
            messages.extend(results.get("messages", []))

        return messages
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def get_message_content(service, msg_id):
    try:
        message = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        payload = message["payload"]
        headers = payload.get("headers", [])

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")

        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data")
                    if data:
                        body += base64.urlsafe_b64decode(data).decode("utf-8")
        elif "body" in payload:
            data = payload["body"].get("data")
            if data:
                body = base64.urlsafe_b64decode(data).decode("utf-8")

        return {"id": msg_id, "subject": subject, "sender": sender, "date": date, "body": body}
    except Exception as e:
        print(f"Error retrieving message {msg_id}: {e}")
        return None


def main():
    service = get_gmail_service()
    query = "rollup"
    print(f"Searching for emails with query: '{query}'...")

    messages = search_messages(service, query)
    print(f"Found {len(messages)} messages.")

    output_file = "ingested_rollup_emails.md"

    with open(output_file, "w") as f:
        f.write("# Ingested 'Rollup' Emails\n\n")

        for i, msg in enumerate(messages[:20]):  # Cap at 20 for now to avoid huge output
            content = get_message_content(service, msg["id"])
            if content:
                print(f"[{i + 1}] Processed: {content['subject']}")
                f.write(f"## {i + 1}. {content['subject']}\n")
                f.write(f"**From:** {content['sender']}\n")
                f.write(f"**Date:** {content['date']}\n\n")
                f.write("### Body\n")
                f.write(f"{content['body']}\n")
                f.write("---\n\n")

    print(f"\nIngestion complete. Saved to {output_file}")


if __name__ == "__main__":
    main()
