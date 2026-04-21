# FCM Admin Push Notifications

## Setup (Frontend)

### 1. Install Firebase Messaging SDK
```bash
npm install firebase
```

### 2. Initialize FCM in admin dashboard
```typescript
import { getMessaging, getToken, onMessage } from "firebase/messaging";

const messaging = getMessaging();

// Request permission and get token
const token = await getToken(messaging, {
  vapidKey: process.env.NEXT_PUBLIC_FIREBASE_VAPID_KEY
});

// Subscribe to admin topic
await fetch('/api/subscribe-admin', {
  method: 'POST',
  body: JSON.stringify({ token })
});
```

### 3. Service Worker (firebase-messaging-sw.js)
```javascript
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js');

firebase.initializeApp({ /* config */ });
const messaging = firebase.messaging();
```

## Topic Subscription (Backend)
```python
from firebase_admin import messaging

def subscribe_to_admin_topic(tokens: list[str]):
    response = messaging.subscribe_to_topic(tokens, "admin-alerts")
    print(f"Successfully subscribed: {response.success_count}")
```

## Sending Alerts
Use Firebase MCP:
```
mcp_firebase-mcp-server_messaging_send_message(
    topic="admin-alerts",
    title="Circuit Breaker OPEN",
    body="Model gemini-flash has tripped circuit breaker"
)
```
