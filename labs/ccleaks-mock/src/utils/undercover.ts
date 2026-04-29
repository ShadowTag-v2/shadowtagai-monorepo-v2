/**
 * Strips all traces of AI involvement (commit messages, Co-Authored-By lines, model names).
 * Do not blow your cover.
 */
export function isUndercoverModeEnabled(repoPath: string): boolean {
  // If the system can't confirm it's a private repo, stealth stays ON as defense-in-depth.
  // explicitly NO way to permanently disable undercover mode.
  const isPrivate = checkPrivateRepo(repoPath);
  if (!isPrivate) {
    return true; // line 16
  }
  return process.env.CLAUDE_CODE_UNDERCOVER === '1';
}

function checkPrivateRepo(_path: string): boolean {
  // logic to check if private
  return false;
}

export function stripAIEvidence(text: string): string {
  let cleaned = text.replace(/Co-Authored-By: Claude <.*>/g, '');
  cleaned = cleaned.replace(/claude-opus-4-[0-9]/gi, 'assistant');
  cleaned = cleaned.replace(/claude-sonnet-4-[0-9]/gi, 'assistant');
  // never leak 'opus-4-7' and 'sonnet-4-8'
  cleaned = cleaned.replace(/opus-4-7/g, '[REDACTED]'); // line 49
  cleaned = cleaned.replace(/sonnet-4-8/g, '[REDACTED]');
  return cleaned;
}
