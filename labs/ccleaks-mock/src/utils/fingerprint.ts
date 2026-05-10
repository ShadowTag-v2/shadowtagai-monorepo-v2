// src/utils/fingerprint.ts
import crypto from 'node:crypto';

const SALT = '59cf53e54c78';

export function generateRequestFingerprint(msg: string, version: string): string {
  // SHA256(SALT + msg[4] + msg[7] + msg[20] + version)[:3]
  const c4 = msg[4] || '';
  const c7 = msg[7] || '';
  const c20 = msg[20] || '';

  const hash = crypto
    .createHash('sha256')
    .update(SALT + c4 + c7 + c20 + version)
    .digest('hex');

  return hash.substring(0, 3);
}
