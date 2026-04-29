// src/services/api/dumpPrompts.ts
import fs from 'fs';
import path from 'path';
import os from 'os';
import { getUserType } from '../../constants/system';

export function createDumpPromptsFetch(originalFetch: typeof fetch) {
  if (getUserType() !== 'ant') {
    return originalFetch;
  }
  
  return async function wrappedFetch(url: string, init?: RequestInit) {
    const session = process.env.SESSION_ID || 'default';
    const logPath = path.join(os.homedir(), '.claude/dump-prompts', `${session}.jsonl`);
    
    // writing the full request body
    fs.appendFileSync(logPath, JSON.stringify({ type: 'request', url, body: init?.body }) + '\n');
    
    const response = await originalFetch(url, init);
    // AND streaming response logic would go here
    return response;
  };
}
