# Encryption Implementation Guide

**Standard:** AES-256-GCM for all encrypted data at rest
**Key Rotation:** Every 90 days (automated via Google Cloud KMS)

---

## TypeScript/Node.js Implementation

### Basic AES-256-GCM Encryption

```typescript
import crypto from 'crypto';

const ALGORITHM = 'aes-256-gcm';
const KEY_LENGTH = 32; // 256 bits
const IV_LENGTH = 12; // 96 bits (recommended for GCM)
const AUTH_TAG_LENGTH = 16; // 128 bits

export interface EncryptedData {
  encrypted: string; // Base64-encoded ciphertext
  iv: string; // Base64-encoded initialization vector
  authTag: string; // Base64-encoded authentication tag
}

export async function encrypt(plaintext: string, key: Buffer): Promise<EncryptedData> {
  const iv = crypto.randomBytes(IV_LENGTH);
  const cipher = crypto.createCipheriv(ALGORITHM, key, iv);

  let encrypted = cipher.update(plaintext, 'utf8', 'base64');
  encrypted += cipher.final('base64');

  const authTag = cipher.getAuthTag();

  return {
    encrypted,
    iv: iv.toString('base64'),
    authTag: authTag.toString('base64')
  };
}

export async function decrypt(data: EncryptedData, key: Buffer): Promise<string> {
  const iv = Buffer.from(data.iv, 'base64');
  const authTag = Buffer.from(data.authTag, 'base64');

  const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
  decipher.setAuthTag(authTag);

  let decrypted = decipher.update(data.encrypted, 'base64', 'utf8');
  decrypted += decipher.final('utf8');

  return decrypted;
}

// Example usage
const encryptionKey = crypto.randomBytes(KEY_LENGTH); // Store securely!
const secret = 'my-secret-password';
const encrypted = await encrypt(secret, encryptionKey);
const decrypted = await decrypt(encrypted, encryptionKey);
```

### Key Management with Google Cloud KMS

```typescript
import { KeyManagementServiceClient } from '@google-cloud/kms';

const kmsClient = new KeyManagementServiceClient();

export async function getEncryptionKey(): Promise<Buffer> {
  const keyName = `projects/${process.env.GCP_PROJECT}/locations/global/keyRings/pnkln-keys/cryptoKeys/data-encryption-key`;

  // Generate a data encryption key (DEK) using KMS
  const [result] = await kmsClient.generateRandomBytes({
    location: keyName,
    lengthBytes: KEY_LENGTH
  });

  return Buffer.from(result.data);
}

export async function encryptWithKMS(plaintext: string): Promise<string> {
  const keyName = `projects/${process.env.GCP_PROJECT}/locations/global/keyRings/pnkln-keys/cryptoKeys/envelope-key`;

  const [result] = await kmsClient.encrypt({
    name: keyName,
    plaintext: Buffer.from(plaintext)
  });

  return Buffer.from(result.ciphertext).toString('base64');
}

export async function decryptWithKMS(ciphertext: string): Promise<string> {
  const keyName = `projects/${process.env.GCP_PROJECT}/locations/global/keyRings/pnkln-keys/cryptoKeys/envelope-key`;

  const [result] = await kmsClient.decrypt({
    name: keyName,
    ciphertext: Buffer.from(ciphertext, 'base64')
  });

  return Buffer.from(result.plaintext).toString('utf8');
}
```

---

## Python Implementation

### Basic AES-256-GCM Encryption

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

def encrypt_aes_256_gcm(plaintext: str, key: bytes) -> dict:
    """Encrypt plaintext using AES-256-GCM"""
    iv = os.urandom(12)  # 96-bit IV for GCM

    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    )

    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

    return {
        'encrypted': base64.b64encode(ciphertext).decode('utf-8'),
        'iv': base64.b64encode(iv).decode('utf-8'),
        'auth_tag': base64.b64encode(encryptor.tag).decode('utf-8')
    }

def decrypt_aes_256_gcm(encrypted_data: dict, key: bytes) -> str:
    """Decrypt ciphertext using AES-256-GCM"""
    ciphertext = base64.b64decode(encrypted_data['encrypted'])
    iv = base64.b64decode(encrypted_data['iv'])
    auth_tag = base64.b64decode(encrypted_data['auth_tag'])

    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, auth_tag),
        backend=default_backend()
    )

    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    return plaintext.decode('utf-8')

# Example usage
key = os.urandom(32)  # 256-bit key
secret = "my-secret-password"
encrypted = encrypt_aes_256_gcm(secret, key)
decrypted = decrypt_aes_256_gcm(encrypted, key)
```

---

## Database Field Encryption

### Prisma Middleware for Auto-Encryption

```typescript
import { PrismaClient } from '@prisma/client';
import { encrypt, decrypt, EncryptedData } from './crypto';

const prisma = new PrismaClient();

// Get encryption key from environment
const ENCRYPTION_KEY = Buffer.from(process.env.ENCRYPTION_KEY!, 'base64');

// Fields that should be encrypted
const ENCRYPTED_FIELDS = ['ssn', 'creditCard', 'apiKey', 'secret'];

prisma.$use(async (params, next) => {
  // Encrypt on write
  if (['create', 'update'].includes(params.action) && params.args.data) {
    for (const field of ENCRYPTED_FIELDS) {
      if (params.args.data[field]) {
        const encrypted = await encrypt(params.args.data[field], ENCRYPTION_KEY);
        params.args.data[field] = JSON.stringify(encrypted);
      }
    }
  }

  const result = await next(params);

  // Decrypt on read
  if (['findUnique', 'findFirst', 'findMany'].includes(params.action)) {
    const decrypt_record = async (record: any) => {
      for (const field of ENCRYPTED_FIELDS) {
        if (record[field]) {
          try {
            const encrypted: EncryptedData = JSON.parse(record[field]);
            record[field] = await decrypt(encrypted, ENCRYPTION_KEY);
          } catch (error) {
            console.error(`Failed to decrypt field ${field}:`, error);
          }
        }
      }
      return record;
    };

    if (Array.isArray(result)) {
      return Promise.all(result.map(decrypt_record));
    } else if (result) {
      return decrypt_record(result);
    }
  }

  return result;
});

export default prisma;
```

---

## File Encryption

### Encrypt Files Before Upload

```typescript
import fs from 'fs/promises';
import { createReadStream, createWriteStream } from 'fs';
import { pipeline } from 'stream/promises';
import crypto from 'crypto';

export async function encryptFile(
  inputPath: string,
  outputPath: string,
  key: Buffer
): Promise<{ iv: string; authTag: string }> {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);

  await pipeline(
    createReadStream(inputPath),
    cipher,
    createWriteStream(outputPath)
  );

  const authTag = cipher.getAuthTag();

  return {
    iv: iv.toString('base64'),
    authTag: authTag.toString('base64')
  };
}

export async function decryptFile(
  inputPath: string,
  outputPath: string,
  key: Buffer,
  iv: string,
  authTag: string
): Promise<void> {
  const decipher = crypto.createDecipheriv(
    'aes-256-gcm',
    key,
    Buffer.from(iv, 'base64')
  );
  decipher.setAuthTag(Buffer.from(authTag, 'base64'));

  await pipeline(
    createReadStream(inputPath),
    decipher,
    createWriteStream(outputPath)
  );
}
```

---

## Key Rotation Strategy

### Automated Key Rotation (Every 90 Days)

```typescript
import { PrismaClient } from '@prisma/client';

interface KeyVersion {
  version: number;
  key: Buffer;
  createdAt: Date;
  expiresAt: Date;
}

export class KeyRotationManager {
  private currentKey: KeyVersion;
  private previousKeys: KeyVersion[] = [];

  constructor(private prisma: PrismaClient) {}

  async rotateKeys(): Promise<void> {
    // Generate new key
    const newVersion = this.currentKey.version + 1;
    const newKey = crypto.randomBytes(32);
    const newKeyVersion: KeyVersion = {
      version: newVersion,
      key: newKey,
      createdAt: new Date(),
      expiresAt: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000) // 90 days
    };

    // Store previous key for decryption
    this.previousKeys.push(this.currentKey);
    this.currentKey = newKeyVersion;

    // Re-encrypt all data with new key
    await this.reEncryptAllData();

    // Clean up keys older than 180 days
    this.previousKeys = this.previousKeys.filter(
      k => k.createdAt.getTime() > Date.now() - 180 * 24 * 60 * 60 * 1000
    );
  }

  private async reEncryptAllData(): Promise<void> {
    // Implement re-encryption logic for your data model
    // This is resource-intensive, run during low-traffic periods
  }
}
```

---

## Testing Encryption

```typescript
import { describe, it, expect } from '@jest/globals';

describe('AES-256-GCM Encryption', () => {
  it('should encrypt and decrypt correctly', async () => {
    const key = crypto.randomBytes(32);
    const plaintext = 'sensitive-data-12345';

    const encrypted = await encrypt(plaintext, key);
    expect(encrypted.encrypted).not.toBe(plaintext);

    const decrypted = await decrypt(encrypted, key);
    expect(decrypted).toBe(plaintext);
  });

  it('should fail with wrong key', async () => {
    const key1 = crypto.randomBytes(32);
    const key2 = crypto.randomBytes(32);
    const plaintext = 'sensitive-data-12345';

    const encrypted = await encrypt(plaintext, key1);

    await expect(decrypt(encrypted, key2)).rejects.toThrow();
  });

  it('should fail with tampered ciphertext', async () => {
    const key = crypto.randomBytes(32);
    const plaintext = 'sensitive-data-12345';

    const encrypted = await encrypt(plaintext, key);
    encrypted.encrypted = 'tampered-data';

    await expect(decrypt(encrypted, key)).rejects.toThrow();
  });
});
```

---

**Best Practices:**
- Always use AES-256-GCM (not CBC/ECB)
- Never reuse IVs with the same key
- Rotate keys every 90 days
- Use Google Cloud KMS for key management
- Test encryption/decryption in CI/CD pipeline
- Monitor key expiration dates
- Have key recovery process documented

**Last Updated:** 2025-11-15
