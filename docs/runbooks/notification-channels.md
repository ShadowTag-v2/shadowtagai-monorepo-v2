# Cloud Monitoring Notification Channels

## Active Channels
| Channel | Type | Status |
|---------|------|--------|
| PagerDuty Email Integration | email | ✅ Enabled |
| Ops Alerts (founder) | email | ✅ Enabled |
| Founder | email | ✅ Enabled |
| CounselConduit Admin Email | email | ✅ Enabled |

## Adding PagerDuty Integration (Future)

### Step 1: Get PagerDuty Integration Key
```bash
# From PagerDuty: Service → Integrations → Add → Google Cloud Monitoring
```

### Step 2: Create Channel
```bash
gcloud alpha monitoring channels create \
  --display-name="PagerDuty Production" \
  --type=pagerduty \
  --channel-labels=service_key=YOUR_PAGERDUTY_KEY
```

### Step 3: Link to Alert Policies
```bash
CHANNEL_ID=$(gcloud alpha monitoring channels list \
  --filter="displayName='PagerDuty Production'" \
  --format="value(name)")

gcloud alpha monitoring policies update POLICY_ID \
  --add-notification-channels=$CHANNEL_ID
```

## Adding Slack Integration

### Step 1: Create Slack App
1. Go to [Slack API](https://api.slack.com/apps)
2. Create app → Add OAuth → Grant `chat:write`
3. Install to workspace

### Step 2: Create Channel
```bash
gcloud alpha monitoring channels create \
  --display-name="Slack #incidents" \
  --type=slack \
  --channel-labels=channel_name=#incidents,auth_token=xoxb-...
```

## Adding FCM Push Notifications
See `docs/runbooks/fcm-admin-notifications.md`
