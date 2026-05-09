/**
 * Active Google Drive API Polling — V25 Pinnacle
 * Allows Opus 4.6 to proactively fetch PRDs and workspace documents on demand.
 * MCP Server: google-drive-api
 */
import { google } from 'googleapis';

const auth = new google.auth.GoogleAuth({
  keyFile: process.env.GOOGLE_APPLICATION_CREDENTIALS,
  scopes: ['https://www.googleapis.com/auth/drive.readonly'],
});
const drive = google.drive({ version: 'v3', auth });

/**
 * Actively fetches a Google Drive document by file ID and returns its text content.
 */
export async function fetchDocumentActively(fileId: string): Promise<string> {
  console.log(`🔍 Active API Fetch: Retrieving Document ${fileId}...`);
  const res = await drive.files.export({ fileId, mimeType: 'text/plain' });
  const content = res.data as string;
  console.log(`✅ Document fetched: ${content.length} chars`);
  return content;
}

/**
 * Lists recent files modified in the last N days.
 */
export async function listRecentFiles(days: number = 7): Promise<Array<{ id: string; name: string; modifiedTime: string }>> {
  const cutoff = new Date(Date.now() - days * 86400000).toISOString();
  const res = await drive.files.list({
    q: `modifiedTime > '${cutoff}' and trashed = false`,
    fields: 'files(id, name, modifiedTime, mimeType)',
    orderBy: 'modifiedTime desc',
    pageSize: 25,
  });
  return (res.data.files || []).map(f => ({
    id: f.id!,
    name: f.name!,
    modifiedTime: f.modifiedTime!,
  }));
}

/**
 * Searches Drive by query string.
 */
export async function searchDrive(query: string): Promise<Array<{ id: string; name: string }>> {
  const res = await drive.files.list({
    q: `fullText contains '${query.replace(/'/g, "\\'")}' and trashed = false`,
    fields: 'files(id, name, mimeType)',
    pageSize: 10,
  });
  return (res.data.files || []).map(f => ({ id: f.id!, name: f.name! }));
}

// MCP stdio server bootstrap
if (import.meta.main) {
  console.log('📂 Google Drive API MCP Server Active (V25 Pinnacle)');
  // MCP protocol handler — reads JSON-RPC from stdin
  const decoder = new TextDecoder();
  for await (const chunk of Bun.stdin.stream()) {
    try {
      const text = decoder.decode(chunk);
      const lines = text.split('\n').filter(Boolean);
      for (const line of lines) {
        const msg = JSON.parse(line);
        if (msg.method === 'fetch_document') {
          const result = await fetchDocumentActively(msg.params.fileId);
          console.log(JSON.stringify({ id: msg.id, result }));
        } else if (msg.method === 'list_files') {
          const result = await listRecentFiles(msg.params?.days ?? 7);
          console.log(JSON.stringify({ id: msg.id, result }));
        } else if (msg.method === 'search_drive') {
          const result = await searchDrive(msg.params.query);
          console.log(JSON.stringify({ id: msg.id, result }));
        }
      }
    } catch {
      // Non-JSON input, skip
    }
  }
}
