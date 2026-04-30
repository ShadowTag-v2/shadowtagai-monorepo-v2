import io
from pathlib import Path

import PyPDF2
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Configuration
TOKEN_FILE = Path("token.json")
OUTPUT_FILE = Path("biz_plan_valuation.txt")

# Only Valuation Folder
FOLDERS = {"Valuation and Stats": "10oQU5IokLQP4KnmYk5sA9Zx5jEHBF33k"}

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    return creds


def list_files_in_folder(service, folder_id):
    print(f"Querying folder: {folder_id}")
    try:
        results = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents",  # Removed trashed check for broader results
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType)",
            )
            .execute()
        )
        files = results.get("files", [])
        print(f"Found {len(files)} files in {folder_id}")
        return files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []


def download_file_content(service, file_id, mime_type):
    try:
        if mime_type.startswith("application/vnd.google-apps"):
            if "document" in mime_type:
                request = service.files().export_media(fileId=file_id, mimeType="text/plain")
            elif "spreadsheet" in mime_type:
                request = service.files().export_media(fileId=file_id, mimeType="text/csv")
            else:
                return None, "Unsupported Google App Type"
        else:
            request = service.files().get_media(fileId=file_id)

        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return file_content.getvalue(), None
    except Exception as e:
        return None, str(e)


def extract_text(content, mime_type):
    if mime_type == "application/pdf":
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() for page in pdf_reader.pages)
        except Exception as e:
            return f"[PDF Extraction Error: {e}]"
    else:
        return content.decode("utf-8", errors="ignore")


def list_files_recursive(service, folder_id, depth=0, max_depth=3):
    if depth > max_depth:
        return []

    all_files = []
    print(f"{'  ' * depth}Listing folder {folder_id}...")

    try:
        results = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents",
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType)",
            )
            .execute()
        )
        items = results.get("files", [])

        for item in items:
            if item["mimeType"] == "application/vnd.google-apps.folder":
                # Recurse
                print(f"{'  ' * (depth + 1)}Found subfolder: {item['name']}")
                all_files.extend(list_files_recursive(service, item["id"], depth + 1, max_depth))
            else:
                all_files.append(item)

    except Exception as e:
        print(f"Error listing {folder_id}: {e}")

    return all_files


def main():
    creds = get_credentials()
    if not creds:
        print("No creds")
        return

    service = build("drive", "v3", credentials=creds)

    with open(OUTPUT_FILE, "w") as f:
        f.write("=== VALUATION DATA START ===\n")

    for label, folder_id in FOLDERS.items():
        print(f"--- Processing {label} ({folder_id}) ---")
        files = list_files_recursive(service, folder_id)
        print(f"Total files found: {len(files)}")

        for file in files:
            name = file["name"]
            mime = file["mimeType"]

            # Skip likely binaries or large archives
            if any(
                name.lower().endswith(ext)
                for ext in [".tar.gz", ".zip", ".dmg", ".iso", ".bin", ".exe"]
            ):
                print(f"  Skipping binary/archive: {name}")
                continue

            print(f"  Fetching: {name}")
            content, error = download_file_content(service, file["id"], mime)

            if error:
                print(f"    Error: {error}")
                continue

            if content:
                if len(content) > 5 * 1024 * 1024:
                    print("    Skipping large file > 5MB")
                    continue

                text = extract_text(content, mime)

                try:
                    with open(OUTPUT_FILE, "a") as f:
                        f.write(f"\n\n=== SOURCE: {label} / {name} ===\n\n{text}")
                    print(f"    Extracted {len(text)} chars (saved)")
                except Exception as e:
                    print(f"    Error writing to file: {e}")


if __name__ == "__main__":
    main()
