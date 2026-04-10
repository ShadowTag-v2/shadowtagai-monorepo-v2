# Claude.ai Google Drive Integration: Configuration Requirements and Troubleshooting

## The core issue: Claude's Drive connector doesn't search folders

**Claude.ai's Google Drive integration is fundamentally document-based, not folder-based.** The connector cannot browse or search folders to enumerate files. Instead, you must explicitly add individual Google Docs through direct selection, which explains why searching for your "ShadowTag-v2_Phase_Docs" folder returns zero results. This limitation stems from OAuth scope restrictions and the integration's architecture.

The integration is currently in **beta status**, available exclusively to **paid subscribers** (Pro, Team, or Enterprise plans), and supports **only Google Docs** up to 10MB with text-only extraction. Mobile and desktop platforms offer the same core functionality, but the iOS app lacks access to desktop connector management features available in the web/desktop versions.

---

## Precise sharing settings and OAuth requirements

### What OAuth scopes control Drive access

Google Drive third-party apps access files through OAuth 2.0 authorization with specific scope-based permissions. While Anthropic doesn't explicitly document Claude's exact OAuth scopes, the integration's behavior indicates it likely uses **`https://www.googleapis.com/auth/drive.file`** or a similar restricted scope rather than full Drive access.

**Critical distinction between OAuth scopes:**

**`drive.file` scope** (recommended, non-restricted): The app can only access files that users explicitly open through Google Picker or create with the app. Selecting a folder through Picker grants access to the folder object itself but **not its contents**. This per-file authorization model provides user control but creates the limitation you're experiencing.

**`drive.readonly` scope** (restricted): Provides read-only access to all Drive files regardless of folder structure or explicit selection. Requires Google security assessment and is primarily used by backup/sync tools. Claude likely doesn't use this scope given the per-document selection interface.

**The fundamental limitation**: If Claude uses `drive.file` scope (the recommended security approach), it cannot enumerate folder contents or perform Drive-wide searches. Users must select specific documents individually.

### Drive sharing settings vs OAuth authorization

**Drive sharing settings and OAuth permissions operate independently.** A file's sharing status (private, link-shared, or public) does **not** determine whether an OAuth-authorized app can access it. What matters is:

1. **User's personal permissions**: You must have view/edit access to the document
2. **OAuth scope granted**: Determines what operations the app can perform
3. **Explicit authorization**: With `drive.file` scope, each document must be individually selected

A private document you select via Picker becomes accessible to Claude. A public document you haven't selected remains inaccessible. The sharing status is irrelevant to OAuth app access when operating under user authentication.

---

## Folder-level vs file-level permissions for OAuth applications

### How Drive's permission model works

Google Drive uses hierarchical permission inheritance where folders propagate access rights downward to all children recursively. When you have "viewer" or "editor" access to a folder, you inherit those permissions for all files within.

**However, this inheritance doesn't extend to OAuth apps using `drive.file` scope.** When a third-party app requests the recommended non-restricted scope, selecting a folder through Google Picker grants access only to that folder as a single resource, not its contents. This security feature prevents apps from gaining blanket access to entire folder trees through a single user action.

**OAuth scope behavior with folders:**

With **`drive.file` scope**: User selects Folder A → App can access Folder A metadata → App **cannot** access files inside Folder A → User must select each file individually

With **`drive.readonly` or `drive` scopes**: User authorizes app → App can enumerate and access all folders and files → Requires Google security assessment → Not practical for most third-party AI tools

**Practical implications**: Claude's integration cannot recursively access folder contents even when you've selected a folder. You must add documents one at a time through the interface.

---

## Service account requirements and explicit sharing

### Do folders need explicit sharing with Claude's service account?

**No, Claude.ai does not use a service account model requiring explicit email-based sharing.** The integration uses standard user OAuth authentication where Claude accesses Drive on behalf of the authenticated user.

**Two distinct authentication patterns:**

**User account OAuth** (what Claude uses): The app acts on behalf of the logged-in user, accessing documents the user has permission to view. No service account email exists to share files with. Access is granted through the OAuth consent screen and subsequent document selection.

**Service account authentication**: Used for server-to-server automation without user interaction. Requires sharing files with the service account's email address (`[email protected]`). This model is used by backup tools and enterprise automation but not by Claude.

**Verification**: When you check Google's third-party connections at myaccount.google.com/connections, you'll see "Claude for Google Drive" listed as an OAuth app, not a service account with a shareable email address.

---

## iOS Claude.ai app vs desktop web version differences

### Platform capabilities and limitations

**Core Google Drive integration functionality is consistent** across web, desktop, and iOS platforms. All versions allow adding Google Docs through the "+" button interface with OAuth authentication. However, significant differences exist in connector management and advanced features.

**iOS mobile app capabilities:**
- ✅ Google Workspace integrations (Drive, Gmail, Calendar)
- ✅ Voice mode with conversational document access
- ✅ Native iOS app integrations (Messages, Mail, Reminders, Maps)
- ✅ Camera integration and iOS Shortcuts
- ❌ **No access to MCP (Model Context Protocol) connector setup or management**
- ❌ No desktop extensions (Apple Notes, Chrome, local file access)

**Desktop and web capabilities:**
- ✅ All mobile features plus additional connector management
- ✅ MCP connector configuration and advanced integrations
- ✅ Desktop extensions for local applications
- ✅ Enhanced project knowledge management

**Critical finding for your situation**: The iOS app provides identical Google Drive document access as desktop/web versions. The limitation you're experiencing (0 search results) is not iOS-specific but rather a fundamental constraint of how the Drive integration works across all platforms.

**Known iOS-specific issues**: While research found desktop connector crashes and stability problems (July-October 2025), the iOS app doesn't appear to have platform-specific Drive integration bugs. However, the iOS app cannot access or configure MCP connectors, which are desktop/web-only features.

---

## Step-by-step instructions: Making folders accessible to Claude

### The fundamental constraint

**Claude's Drive connector cannot make entire folders "accessible" in the sense of browsing or searching contents.** The integration is document-centric by design. Here's what you can actually do:

### Method 1: Add individual documents from your folder (recommended)

**Step 1: Prepare your documents**
1. Open drive.google.com in a browser
2. Navigate to your "ShadowTag-v2_Phase_Docs" folder
3. Verify documents are Google Docs format (not .docx, .pdf, or other formats)
4. Convert if needed: Open .docx files → File → Save as Google Docs
5. Check each document is under 10MB
6. Confirm you have view/edit permissions

**Step 2: Get document URLs**
1. Open each Google Doc you want Claude to access
2. Copy the full URL from browser address bar
3. Alternatively, right-click document → Get link → Copy link

**Step 3: Add to Claude via iOS app**
1. Open Claude.ai iOS app
2. Start a new chat or open existing conversation
3. Tap the **"+"** button in the chat interface
4. Select **"Add from Google Drive"**
5. First time: Authenticate with your Google Account
   - Review permissions Claude is requesting
   - Tap "Allow" to grant access
6. **Paste document URL** directly into the search/URL field
7. Select the document from results
8. Send your message - Claude now has access to that specific document

**Step 4: Repeat for additional documents**
- Each document from your folder must be added individually
- Claude will sync the latest version automatically
- Documents remain accessible in that conversation/project

### Method 2: Add documents to Claude Projects (for persistent access)

**Step 1: Create or open a private project**
1. In Claude.ai (web or app), navigate to Projects
2. Create a new private project or open existing one
3. Only private projects support Drive integration

**Step 2: Add documents to project knowledge**
1. Click **"Add Content"** in project knowledge section
2. Select **"Google Drive"**
3. Authenticate if first time
4. Paste document URLs from your "ShadowTag-v2_Phase_Docs" folder
5. Each added document becomes part of project knowledge base

**Benefits of Projects approach:**
- Documents persist across all chats within the project
- Automatic syncing with latest Drive versions
- Build knowledge base from multiple documents in your folder
- All project chats can reference these documents

### Method 3: Use "recently accessed" list

**If you frequently work with documents in your folder:**
1. Open each document in drive.google.com or Google Docs app
2. View or edit them to add to "recent" list
3. In Claude, click "+" → "Add from Google Drive"
4. Your recently accessed docs from that folder will appear
5. Select from the recent list rather than searching

### What doesn't work (and why)

❌ **Searching for folder name**: Claude cannot search folder names or enumerate folder contents due to OAuth scope limitations

❌ **Selecting folder via picker**: Even if you could select the folder object, the `drive.file` scope doesn't grant recursive access to contents

❌ **General Drive search queries**: The integration doesn't provide Drive-wide search functionality - it's limited to recently accessed documents or direct URLs

❌ **Expecting automatic folder discovery**: You must explicitly authorize each document individually

---

## Troubleshooting: Drive connector shows 0 results

### Why you're seeing 0 results

Based on your description ("ShadowTag-v2_Phase_Docs" folder visible in Drive mobile app but Claude returns 0 results), the issue is **not a configuration problem but a fundamental design limitation**.

**Root causes for 0 results:**

**Primary cause**: Claude's Drive integration doesn't search folders or perform Drive-wide queries. When you search for "ShadowTag-v2_Phase_Docs" or any folder name, it returns 0 results because:
- The search only queries recently accessed Google Docs
- It cannot enumerate folder contents
- Folder names aren't searchable entities in the integration
- OAuth scope prevents recursive folder access

**Secondary causes to verify:**

**File format mismatch**: Only Google Docs are supported
- Check if documents in your folder are .docx, .pdf, or other formats
- Convert to Google Docs: Open file → File → Save as Google Docs
- .docx files, even in Drive, won't appear in Claude's interface

**Permission issues**: You must have explicit access
- Verify you can open documents by visiting drive.google.com
- Check sharing settings show you as owner or viewer/editor
- For work/school accounts, IT may have restricted permissions

**Authentication state**: Connection may need refresh
- Go to Claude Settings → Integrations
- Verify Google Drive shows as "Connected"
- If disconnected, reconnect via Settings

**File size limitations**: Documents over 10MB excluded
- Check document sizes in Drive
- Large documents won't appear in selectable lists
- Compress or split documents if needed

### Systematic troubleshooting steps

**Step 1: Verify integration is properly connected**
1. Open Claude.ai iOS app
2. Go to Settings (profile icon)
3. Tap "Integrations"
4. Confirm Google Drive shows:
   - "Connected" status with your email address
   - Green checkmark or active indicator
5. If not connected or showing error, proceed to Step 2

**Step 2: Disconnect and reconnect authentication**
1. In Settings → Integrations → Google Drive
2. Tap the menu button (...)
3. Select **"Disconnect"**
4. Confirm disconnection
5. Return to chat interface
6. Tap "+" → "Add from Google Drive"
7. Complete OAuth authentication flow again
8. Review and approve permissions

**Step 3: Revoke and re-grant from Google side**
1. Visit **myaccount.google.com/connections** in browser
2. Navigate to "Have access to your Google Account"
3. Search for "Claude for Google Drive"
4. Click the entry to view details
5. Select **"Remove access"** or **"Delete all connections"**
6. Confirm removal
7. Return to Claude.ai iOS app
8. Re-authenticate through Drive integration

**Step 4: Verify document accessibility**
1. Open drive.google.com in mobile browser
2. Navigate to "ShadowTag-v2_Phase_Docs" folder
3. Open a specific document
4. Verify it's Google Docs format (not .docx or other)
5. Copy the document's full URL
6. In Claude iOS app, use "+" → "Add from Google Drive"
7. **Paste the direct document URL** instead of searching
8. If document appears, the connection works - issue is search limitation

**Step 5: Check for account restrictions**
1. If using work/school Google Workspace account:
   - Contact IT administrator
   - Ask if third-party app access is enabled for Drive
   - Request approval for "Claude for Google Drive" if blocked
   - Admin controls: Google Admin Console → Security → API controls
2. For personal accounts, this typically isn't an issue

**Step 6: Test with different document**
1. Create a new Google Doc in your Drive root (not in folder)
2. Title it "Claude Test Document"
3. Add some text content
4. Open the doc and copy URL
5. In Claude, add this document via URL paste
6. If successful, confirms integration works
7. Issue is specifically with folder-based access, not overall connectivity

**Step 7: Verify subscription status**
1. Confirm you have active paid subscription:
   - Claude Pro ($20/month)
   - Claude Team
   - Claude Enterprise
2. Free plans do not have Drive integration access
3. Check billing/subscription in Settings

### Known issues affecting Drive search (November 2025)

**Recent platform incidents**: Anthropic's status page documented connector issues in October 2025, including elevated errors with claude.ai connectors and MCP tools. While these were marked resolved, residual effects may persist.

**GitHub sync regression**: A platform-wide regression affecting GitHub repository connectors was reported October 30, 2025, where connectors showed "Connected" but files weren't accessible. This may affect other integrations including Drive.

**Search tool reliability**: Multiple user reports document ~50% failure rates with search functionality across Claude Code and other search tools, with issues particularly affecting file enumeration and pattern matching.

**If troubleshooting steps don't resolve the issue**, the problem may be:
- Platform-wide technical issue (check status.anthropic.com)
- Beta integration limitation rather than configuration error
- Fundamental design constraint requiring workflow adaptation

---

## Verifying OAuth scope includes file enumeration capabilities

### How to check what permissions Claude actually has

**Step 1: Access Google Account connections**
1. Visit **myaccount.google.com/connections** in any browser
2. Sign in with the Google Account connected to Claude
3. Navigate to **"Have access to your Google Account"** section
4. Look for "Claude for Google Drive" in the app list

**Step 2: Review granted permissions**
1. Click on "Claude for Google Drive" entry
2. View the permissions details panel showing:
   - **Access granted date**: When you authorized the app
   - **Last used**: Recent activity timestamp
   - **Has access to**: Specific Google services (Drive, Docs)
   - **Can see and download**: Specific data types accessible

**Step 3: Analyze OAuth scopes**

While Google's consumer interface doesn't display raw OAuth scope URLs, you can infer capabilities:

**If permissions show**: "See and download all your Google Drive files"
- Likely scope: `drive.readonly` (full read access)
- **Should support**: File enumeration, folder browsing, Drive-wide search
- **Your situation**: If Claude had this scope but still returns 0 results, indicates technical bug

**If permissions show**: "See, edit, create, and delete only the specific Google Drive files you use with this app"
- Likely scope: `drive.file` (per-file access)
- **Limitation**: Cannot enumerate files, cannot search Drive, cannot browse folders
- **Your situation**: This explains 0 search results - integration lacks enumeration capabilities by design

**Based on Claude's interface design** (requiring explicit document URLs or selection from recent list), the integration almost certainly uses the **`drive.file` scope**, which inherently **does not include file enumeration or search capabilities**.

### The technical reality of OAuth scopes

**What `drive.file` scope allows:**
- Access files created by the app
- Access files explicitly opened through the app via Google Picker
- Access files when user provides direct URL
- Read file content and metadata for authorized files

**What `drive.file` scope does NOT allow:**
- List all files in Drive
- Search Drive by filename, content, or folder
- Enumerate folder contents
- Browse Drive file tree
- Access files not explicitly authorized

**What `drive.readonly` scope allows:**
- All of the above restrictions removed
- Full read-only access to entire Drive
- File enumeration and search capabilities
- Folder browsing and recursive access

**Why Claude likely uses `drive.file`:**
1. **Security and privacy**: Least-privilege principle - only access what users explicitly share
2. **Google verification requirements**: `drive.readonly` requires extensive security assessment
3. **User trust**: Per-file authorization provides clear user control
4. **OAuth verification status**: Restricted scopes face lengthy approval process

### Testing enumeration capabilities

**Practical test to verify scope limitations:**

1. **Create a test document** in your Drive root:
   - New Google Doc titled "Claude OAuth Test"
   - Add unique text: "Testing OAuth enumeration capabilities"

2. **Without adding to Claude**, try these searches in Claude's Drive interface:
   - Search for "OAuth Test"
   - Search for "Testing OAuth"
   - Search for filename

3. **Expected results with `drive.file` scope**:
   - 0 results for all searches
   - Document won't appear in any list
   - No way to discover the file exists

4. **Now explicitly add the document**:
   - Copy document URL
   - Add via "+" → "Add from Google Drive" → paste URL
   - Document becomes accessible

5. **Conclusion**:
   - If you cannot find files via search until explicitly added, confirms `drive.file` scope
   - Enumeration and search are not supported by the granted OAuth permissions
   - This is by design, not a bug or misconfiguration

---

## Recommended workflow for your "ShadowTag-v2_Phase_Docs" folder

Given the technical constraints identified, here's the most efficient approach:

### One-time setup process

**Step 1: Document inventory**
1. Open your "ShadowTag-v2_Phase_Docs" folder at drive.google.com
2. Create a list of all important documents you want Claude to access
3. Verify each is Google Docs format (convert if needed)
4. Check file sizes are under 10MB

**Step 2: Gather document URLs**
1. Open each document from your list
2. Copy the full URL (format: `docs.google.com/document/d/[DOCUMENT_ID]/edit`)
3. Save URLs in a temporary note or document for reference
4. Alternatively, create a Google Doc with links to all other docs in the folder

**Step 3: Create a Claude Project for this folder's content**
1. Go to claude.ai (web or app)
2. Create a new private project: "ShadowTag-v2 Phase Documentation"
3. Add description indicating it contains docs from your Drive folder
4. This becomes your permanent workspace for these documents

**Step 4: Bulk add documents to project**
1. In project knowledge, click "Add Content" → "Google Drive"
2. Paste first document URL → add to project
3. Repeat for each document from your folder
4. All documents now form a unified knowledge base
5. Any chat in this project can reference all these documents

### Ongoing usage

**For daily work:**
- Start chats within your "ShadowTag-v2 Phase Documentation" project
- All documents from the folder are automatically available as context
- Claude can reference and analyze content across all added documents
- Updates to Drive documents sync automatically

**When adding new documents to the folder:**
1. Create/add the new Google Doc in Drive
2. Copy its URL
3. Add to your Claude Project knowledge base
4. Now accessible in all future project chats

**For quick one-off questions:**
- In any chat, use "+" → paste document URL directly
- Don't need to use the project if only referencing one document

### Alternative: Master index document

If you prefer not to use Projects:

1. Create a new Google Doc: "Claude Access Index"
2. Add links to all documents in your "ShadowTag-v2_Phase_Docs" folder
3. Add this index document to Claude once via URL
4. When you need a specific document, ask Claude to reference the index
5. Manually add the specific document URL for that conversation

This provides a searchable catalog within Claude while working around the folder access limitation.

---

## Summary of key findings

**The core issue is architectural, not configurational.** Claude.ai's Google Drive integration uses OAuth scopes that prioritize security and user control over convenience. The `drive.file` scope (or equivalent restricted scope) prevents file enumeration and folder searching, requiring explicit per-document authorization through direct URLs or recent file selection.

**Your "ShadowTag-v2_Phase_Docs" folder returns 0 results because:**
1. Claude cannot search folder names or enumerate folder contents
2. OAuth scope lacks Drive-wide search capabilities
3. The integration is document-centric by design, not folder-aware
4. This is consistent across iOS, desktop, and web platforms

**No configuration changes will enable folder browsing.** The limitation is fundamental to the OAuth permission model Claude uses. Instead, adapt your workflow to explicitly add individual documents through:
- Direct URL pasting (most reliable)
- Selection from recently accessed documents
- Building a Project knowledge base with all folder documents

**The integration works correctly** - it's operating as designed within OAuth security constraints. Your folder is accessible, but only by authorizing documents individually rather than through folder-level discovery. This design choice prioritizes data privacy and user control over automated convenience.