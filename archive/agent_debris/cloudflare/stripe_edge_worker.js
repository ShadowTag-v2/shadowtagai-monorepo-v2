// cloudflare/stripe_edge_worker.js
// ⏺ ///▙▖▙▖▞ CLOUDFLARE EDGE WORKER: STRIPE HMAC VALIDATION
// Drops invalid payloads at the CDN Edge. Never touches GCP Billing.

export default {
  async fetch(request, env, ctx) {
    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405 })
    }

    const signatureHeader = request.headers.get('Stripe-Signature')
    if (!signatureHeader) {
      return new Response('Forbidden: Missing Signature', { status: 403 })
    }

    const payload = await request.text()
    // STRIPE_WEBHOOK_SECRET injected via Cloudflare Environment Variables
    const secret = env.STRIPE_WEBHOOK_SECRET 

    if (!secret) {
      return new Response('Internal Server Error: Secret config missing', { status: 500 })
    }

    const sigs = parseSignatureHeader(signatureHeader)
    const timestamp = sigs.t
    const expectedSignature = sigs.v1

    if (!timestamp || !expectedSignature) {
      return new Response('Forbidden: Invalid Signature Format', { status: 403 })
    }

    // Web Crypto API check
    const encoder = new TextEncoder()
    const key = await crypto.subtle.importKey(
      'raw',
      encoder.encode(secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['verify', 'sign']
    )

    const data = encoder.encode(`${timestamp}.${payload}`)
    const signature = await crypto.subtle.sign('HMAC', key, data)
    
    const hexSignature = Array.from(new Uint8Array(signature))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('')

    if (hexSignature !== expectedSignature) {
      return new Response('Forbidden: Signature Mismatch', { status: 403 })
    }

    // Cryptography holds. Forward the request to the upstream Origin via Cloudflare Tunnel.
    const originUrl = new URL(request.url)
    
    const upstreamRequest = new Request(originUrl.toString(), {
      method: request.method,
      headers: request.headers,
      body: payload
    })
    
    return fetch(upstreamRequest)
  }
}

function parseSignatureHeader(header) {
  const pairs = header.split(',').map(s => s.split('='))
  const parsed = {}
  for (const [key, value] of pairs) {
    parsed[key] = value
  }
  return parsed
}
