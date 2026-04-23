/**
 * WebCrypto BYOK Encryption Client
 *
 * Sprint Item #13: Client-side key encryption before transmission.
 *
 * Uses Web Crypto API (AES-256-GCM) to encrypt API keys in the
 * browser BEFORE sending to our server. We never see the plaintext.
 *
 * Flow:
 * 1. User pastes API key in browser
 * 2. This library encrypts it with a derived key (PBKDF2)
 * 3. Encrypted blob + IV sent to /api/tokens/byok
 * 4. Server stores encrypted blob in GCP Secret Manager
 * 5. Key is ONLY decryptable by the client-side passphrase
 *
 * @see lib/auth/seu-token.ts — S.E.U. binding
 * @see Cor.30 Pillar 2 — Secrets & Supply Chain
 */

// ─── Types ──────────────────────────────────────────────────────────

export interface EncryptedPayload {
  encryptedKey: string; // Base64 encoded ciphertext
  iv: string; // Base64 encoded initialization vector
  salt: string; // Base64 encoded PBKDF2 salt
  algorithm: 'AES-256-GCM';
  keyDerivation: 'PBKDF2-SHA256';
  iterations: number;
}

export interface DecryptedResult {
  key: string;
  provider: string;
}

// ─── Configuration ──────────────────────────────────────────────────

const PBKDF2_ITERATIONS = 600_000; // OWASP recommendation 2024
const AES_KEY_LENGTH = 256;
const IV_LENGTH = 12; // 96 bits for GCM
const SALT_LENGTH = 32; // 256 bits

// ─── Key Derivation ─────────────────────────────────────────────────

/**
 * Derives an AES-256 key from a passphrase using PBKDF2.
 */
async function deriveKey(passphrase: string, salt: Uint8Array): Promise<CryptoKey> {
  const encoder = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(passphrase),
    'PBKDF2',
    false,
    ['deriveKey'],
  );

  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt,
      iterations: PBKDF2_ITERATIONS,
      hash: 'SHA-256',
    },
    keyMaterial,
    { name: 'AES-GCM', length: AES_KEY_LENGTH },
    false,
    ['encrypt', 'decrypt'],
  );
}

// ─── Encryption ─────────────────────────────────────────────────────

/**
 * Encrypts an API key client-side for BYOK registration.
 *
 * The passphrase is NEVER transmitted. Only the encrypted
 * payload (ciphertext + IV + salt) is sent to the server.
 */
export async function encryptAPIKey(apiKey: string, passphrase: string): Promise<EncryptedPayload> {
  const encoder = new TextEncoder();

  // Generate random salt and IV
  const salt = crypto.getRandomValues(new Uint8Array(SALT_LENGTH));
  const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH));

  // Derive encryption key from passphrase
  const key = await deriveKey(passphrase, salt);

  // Encrypt
  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    key,
    encoder.encode(apiKey),
  );

  return {
    encryptedKey: arrayBufferToBase64(ciphertext),
    iv: arrayBufferToBase64(iv),
    salt: arrayBufferToBase64(salt),
    algorithm: 'AES-256-GCM',
    keyDerivation: 'PBKDF2-SHA256',
    iterations: PBKDF2_ITERATIONS,
  };
}

// ─── Decryption ─────────────────────────────────────────────────────

/**
 * Decrypts an API key client-side.
 *
 * This runs ONLY in the browser, ONLY when the key is needed
 * for an API call. The decrypted key is held in memory briefly
 * and then discarded.
 */
export async function decryptAPIKey(
  payload: EncryptedPayload,
  passphrase: string,
): Promise<string> {
  const salt = base64ToUint8Array(payload.salt);
  const iv = base64ToUint8Array(payload.iv);
  const ciphertext = base64ToArrayBuffer(payload.encryptedKey);

  const key = await deriveKey(passphrase, salt);

  const plaintext = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, ciphertext);

  return new TextDecoder().decode(plaintext);
}

// ─── BYOK Registration Flow ────────────────────────────────────────

/**
 * Full BYOK registration flow:
 * 1. Encrypt the API key client-side
 * 2. Send encrypted payload to server
 * 3. Server stores in GCP Secret Manager
 */
export async function registerBYOK(
  apiKey: string,
  passphrase: string,
  provider: 'anthropic' | 'google-vertex' | 'openai',
  firmId: string,
  seuToken: string,
): Promise<{ status: string; secretId: string }> {
  // Step 1: Encrypt locally
  const encrypted = await encryptAPIKey(apiKey, passphrase);

  // Step 2: Send to server
  const response = await fetch('/api/tokens/byok', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-SEU-Token': seuToken,
    },
    body: JSON.stringify({
      provider,
      encryptedKey: encrypted.encryptedKey,
      iv: encrypted.iv,
      firmId,
    }),
  });

  if (!response.ok) {
    throw new Error(`BYOK registration failed: ${response.status}`);
  }

  return response.json();
}

// ─── Helpers ────────────────────────────────────────────────────────

function arrayBufferToBase64(buffer: ArrayBuffer | Uint8Array): string {
  const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
  let binary = '';
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  return btoa(binary);
}

function base64ToUint8Array(base64: string): Uint8Array {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

function base64ToArrayBuffer(base64: string): ArrayBuffer {
  return base64ToUint8Array(base64).buffer;
}
