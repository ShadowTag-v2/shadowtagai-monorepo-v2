# TLS 1.3 Configuration Guide

**Standard:** TLS 1.3 ONLY (no TLS 1.2, no TLS 1.1, no TLS 1.0)
**Cipher Suites:** AES-256-GCM and ChaCha20-Poly1305 only

---

## Why TLS 1.3?

TLS 1.3 provides:
- Faster handshakes (1-RTT vs 2-RTT)
- Forward secrecy by default
- Removed weak/outdated ciphers
- Encrypted Server Hello (better privacy)
- Resistance to downgrade attacks

**Security:** TLS 1.2 has known vulnerabilities (BEAST, POODLE, Heartbleed). TLS 1.3 removes these attack vectors.

---

## Node.js/Express Configuration

### HTTPS Server with TLS 1.3

```typescript
import https from 'https';
import express from 'express';
import fs from 'fs';

const app = express();

const httpsOptions: https.ServerOptions = {
  key: fs.readFileSync('/path/to/private-key.pem'),
  cert: fs.readFileSync('/path/to/certificate.pem'),
  ca: fs.readFileSync('/path/to/ca-bundle.pem'), // Optional: CA bundle

  // TLS 1.3 ONLY
  minVersion: 'TLSv1.3',
  maxVersion: 'TLSv1.3',

  // Approved cipher suites (TLS 1.3)
  ciphers: [
    'TLS_AES_256_GCM_SHA384',
    'TLS_CHACHA20_POLY1305_SHA256'
  ].join(':'),

  // Security headers
  honorCipherOrder: true, // Prefer server cipher order
  requestCert: false, // Set to true for mTLS
  rejectUnauthorized: true // Reject invalid certificates
};

const server = https.createServer(httpsOptions, app);

server.listen(443, () => {
  console.log('HTTPS server running on port 443 with TLS 1.3');
});
```

### Outgoing HTTPS Requests with TLS 1.3

```typescript
import https from 'https';
import fetch from 'node-fetch';

const httpsAgent = new https.Agent({
  minVersion: 'TLSv1.3',
  maxVersion: 'TLSv1.3',
  ciphers: 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256',
  rejectUnauthorized: true // Fail if certificate invalid
});

// Using fetch
const response = await fetch('https://api.example.com/data', {
  agent: httpsAgent
});

// Using axios
import axios from 'axios';

const client = axios.create({
  httpsAgent: httpsAgent
});

const result = await client.get('https://api.example.com/data');
```

---

## Python Configuration

### Flask/Gunicorn with TLS 1.3

```python
# gunicorn_config.py
import ssl

# TLS 1.3 configuration
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3

# Load certificates
ssl_context.load_cert_chain(
    certfile='/path/to/certificate.pem',
    keyfile='/path/to/private-key.pem'
)

# Cipher suites (TLS 1.3)
ssl_context.set_ciphers('TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256')

# Gunicorn settings
bind = '0.0.0.0:443'
workers = 4
certfile = '/path/to/certificate.pem'
keyfile = '/path/to/private-key.pem'
ssl_version = ssl.PROTOCOL_TLS_SERVER
ciphers = 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256'
```

### Requests Library with TLS 1.3

```python
import requests
from urllib3.util.ssl_ import create_urllib3_context

class TLS13Adapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        ctx.maximum_version = ssl.TLSVersion.TLSv1_3
        ctx.set_ciphers('TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256')
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

# Usage
session = requests.Session()
session.mount('https://', TLS13Adapter())

response = session.get('https://api.example.com/data')
```

---

## Nginx Reverse Proxy Configuration

### nginx.conf (TLS 1.3)

```nginx
server {
    listen 443 ssl http2;
    server_name api.pnkln.com;

    # TLS 1.3 ONLY
    ssl_protocols TLSv1.3;

    # Certificates
    ssl_certificate /etc/nginx/ssl/certificate.pem;
    ssl_certificate_key /etc/nginx/ssl/private-key.pem;

    # Cipher suites (TLS 1.3)
    ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256';
    ssl_prefer_server_ciphers on;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/nginx/ssl/ca-bundle.pem;

    # Session settings
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off; # Disable for perfect forward secrecy

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to backend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.pnkln.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Certificate Management

### Let's Encrypt (Automated Renewal)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.pnkln.com -d www.pnkln.com

# Auto-renewal (runs twice daily)
sudo certbot renew --dry-run

# Cron job for renewal
0 0,12 * * * certbot renew --quiet
```

### Google Cloud Certificate Manager

```bash
# Create SSL certificate
gcloud compute ssl-certificates create pnkln-cert \
  --certificate=/path/to/certificate.pem \
  --private-key=/path/to/private-key.pem

# Create load balancer with TLS 1.3
gcloud compute target-https-proxies create pnkln-https-proxy \
  --ssl-certificates=pnkln-cert \
  --url-map=pnkln-url-map \
  --ssl-policy=tls13-only

# Create SSL policy (TLS 1.3 only)
gcloud compute ssl-policies create tls13-only \
  --profile=MODERN \
  --min-tls-version=1.3
```

---

## Testing TLS Configuration

### OpenSSL Test

```bash
# Test TLS 1.3 connection
openssl s_client -connect api.pnkln.com:443 -tls1_3

# Expected output:
# Protocol  : TLSv1.3
# Cipher    : TLS_AES_256_GCM_SHA384

# Test that TLS 1.2 is rejected
openssl s_client -connect api.pnkln.com:443 -tls1_2
# Should fail with: "SSL handshake failed"
```

### SSL Labs Test

```bash
# Test your domain
curl -s "https://api.ssllabs.com/api/v3/analyze?host=api.pnkln.com" | jq

# Expected grade: A+ with TLS 1.3
```

### Automated Testing Script

```typescript
import https from 'https';
import tls from 'tls';

export async function testTlsVersion(hostname: string, port: number = 443): Promise<void> {
  return new Promise((resolve, reject) => {
    const socket = tls.connect(port, hostname, {
      minVersion: 'TLSv1.3',
      maxVersion: 'TLSv1.3'
    }, () => {
      const protocol = socket.getProtocol();
      const cipher = socket.getCipher();

      console.log(`✓ TLS Version: ${protocol}`);
      console.log(`✓ Cipher: ${cipher.name}`);

      if (protocol !== 'TLSv1.3') {
        reject(new Error(`Expected TLS 1.3, got ${protocol}`));
      }

      if (!['TLS_AES_256_GCM_SHA384', 'TLS_CHACHA20_POLY1305_SHA256'].includes(cipher.name)) {
        reject(new Error(`Weak cipher: ${cipher.name}`));
      }

      socket.end();
      resolve();
    });

    socket.on('error', (error) => {
      reject(error);
    });
  });
}

// Run test
await testTlsVersion('api.pnkln.com');
```

---

## Mutual TLS (mTLS) for Service-to-Service

### Server Configuration (Require Client Certificate)

```typescript
const httpsOptions: https.ServerOptions = {
  key: fs.readFileSync('/path/to/server-key.pem'),
  cert: fs.readFileSync('/path/to/server-cert.pem'),
  ca: fs.readFileSync('/path/to/ca-cert.pem'),

  // Require client certificate
  requestCert: true,
  rejectUnauthorized: true,

  // TLS 1.3
  minVersion: 'TLSv1.3',
  maxVersion: 'TLSv1.3'
};

app.use((req, res, next) => {
  const cert = (req as any).socket.getPeerCertificate();

  if (!cert || !cert.subject) {
    return res.status(401).json({ error: 'Client certificate required' });
  }

  console.log(`Authenticated client: ${cert.subject.CN}`);
  next();
});
```

### Client Configuration (Provide Certificate)

```typescript
const httpsAgent = new https.Agent({
  cert: fs.readFileSync('/path/to/client-cert.pem'),
  key: fs.readFileSync('/path/to/client-key.pem'),
  ca: fs.readFileSync('/path/to/ca-cert.pem'),
  minVersion: 'TLSv1.3',
  maxVersion: 'TLSv1.3'
});

const response = await fetch('https://internal-service.pnkln.com/api', {
  agent: httpsAgent
});
```

---

## Common Issues & Fixes

### Issue: "unsupported protocol" Error

```typescript
// ❌ Wrong: No TLS version specified
const agent = new https.Agent({});

// ✅ Fix: Explicitly set TLS 1.3
const agent = new https.Agent({
  minVersion: 'TLSv1.3',
  maxVersion: 'TLSv1.3'
});
```

### Issue: Certificate Verification Failed

```typescript
// ❌ Wrong: Disabling certificate verification (insecure!)
const agent = new https.Agent({
  rejectUnauthorized: false // NEVER DO THIS IN PRODUCTION
});

// ✅ Fix: Add CA certificate
const agent = new https.Agent({
  ca: fs.readFileSync('/path/to/ca-bundle.pem'),
  rejectUnauthorized: true
});
```

### Issue: "no shared cipher" Error

```bash
# Check supported ciphers
openssl ciphers -v 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256'

# Expected output:
# TLS_AES_256_GCM_SHA384  TLSv1.3
# TLS_CHACHA20_POLY1305_SHA256 TLSv1.3
```

---

## Security Checklist

- [ ] TLS 1.3 enforced (no fallback to 1.2)
- [ ] Only approved ciphers enabled (AES-256-GCM, ChaCha20-Poly1305)
- [ ] Valid SSL certificate installed (not self-signed in production)
- [ ] Certificate auto-renewal configured
- [ ] OCSP stapling enabled (Nginx)
- [ ] HTTP redirects to HTTPS
- [ ] HSTS header enabled (max-age=31536000)
- [ ] Certificate expiry monitoring configured
- [ ] mTLS enabled for service-to-service communication
- [ ] SSL Labs test score: A+

---

**Best Practices:**
- Use TLS 1.3 exclusively (no backward compatibility)
- Automate certificate renewal (Let's Encrypt or Cloud provider)
- Monitor certificate expiration (alert 30 days before)
- Test TLS config with SSL Labs
- Enable OCSP stapling for performance
- Use mTLS for internal services
- Rotate certificates annually (even if not expired)

**Last Updated:** 2025-11-15
