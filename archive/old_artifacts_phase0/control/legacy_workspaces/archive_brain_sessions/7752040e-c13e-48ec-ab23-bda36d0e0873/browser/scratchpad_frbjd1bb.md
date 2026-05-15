# Task: Share Google Drive Folder with Service Account

- [x] Read scratchpad
- [x] Open Google
- [x] Search for instructions
- [x] Extract official steps
- [x] Format and return instructions

## Findings
- Sharing a folder with a service account is performed the same way as sharing with a regular user.
- The service account email `google-drive-access@shadowtag-omega-v4.iam.gserviceaccount.com` is used as the target.
- For **My Drive** folders: Use the "Share" button and add the email.
- For **Shared Drives**: Either share the folder individually or add the service account via "Manage members".
- Service accounts do not have an inbox, so "Notify people" can be unchecked.

## Official Steps (Verified)
1. **Copy Email**: `google-drive-access@shadowtag-omega-v4.iam.gserviceaccount.com`
2. **Open Drive**: Go to drive.google.com.
3. **Select Folder**: Right-click the target folder.
4. **Share**: Click "Share".
5. **Add Email**: Paste the service account email into the "Add people and groups" field.
6. **Set Role**: Select "Viewer", "Commenter", or "Editor".
7. **Notify**: (Optional) Uncheck "Notify people".
8. **Finalize**: Click "Send" or "Share".
