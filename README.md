# OneSignal API Server

A FastAPI backend server for OneSignal demo applications. Provides API endpoints for:
- OTP authentication
- Parcel delivery tracking with push notifications
- Coupon code generation and validation
- Flight update Live Activities
- Calendar event generation
- **Webhook event storage for notification inbox**

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/cbenedikter/onesignal-api-server.git
   cd onesignal-api-server
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run the server**
   ```bash
   python run.py
   ```

   Server runs at `http://localhost:8000`

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Deployment on Railway

### Step 1: Deploy the App

1. Connect your GitHub repository to Railway
2. Railway will auto-detect the Python app and deploy

### Step 2: Add Postgres Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway automatically sets the `DATABASE_URL` environment variable

### Step 3: Configure Environment Variables

In Railway's **Variables** tab, add:

```
# OneSignal App Credentials
signal_post_app_id=your-app-id
signal_post_api_key=your-api-key

# Add other OneSignal apps as needed
emea_se_demo_app_id=...
emea_se_demo_api_key=...

# Optional: Vercel KV (for OTP storage)
KV_REST_API_URL=...
KV_REST_API_TOKEN=...
```

> **Note:** `DATABASE_URL` is automatically provided by Railway when you add Postgres.

### Step 4: Configure OneSignal Webhooks

In each OneSignal app dashboard:

1. Go to **Settings** → **Webhooks**
2. Add a new webhook with URL:
   ```
   https://your-railway-app.railway.app/webhooks/onesignal
   ```
3. Select events to receive:
   - `notification.sent`
   - `notification.delivered`
   - `notification.clicked`
   - `notification.dismissed`

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/otp` | Generate OTP code |
| POST | `/auth/verify` | Verify OTP code |

### Delivery Tracking
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/delivery` | Start delivery notification sequence |

### Webhooks & Message Inbox
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhooks/onesignal` | Receive OneSignal webhook events |
| GET | `/messages/{app_id}/{external_id}` | Get user's notification inbox |
| DELETE | `/messages/{app_id}/{external_id}` | Delete user's messages |
| GET | `/webhooks/health` | Check webhook system health |

### Other
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/coupon/request` | Generate coupon code |
| POST | `/coupon/validate` | Validate coupon code |
| POST | `/flight-update` | Update Live Activity |
| POST | `/calendar-data` | Generate calendar event |

---

## Notification Inbox Feature

The webhook system enables a **notification inbox** in your mobile app by:

1. **Storing events**: All OneSignal webhook events are stored in Postgres
2. **Multi-app support**: Events are tagged with `app_id` for separation
3. **User isolation**: Messages are retrieved by `external_id` (from `OneSignal.login()`)
4. **90-day retention**: Events are stored for 90 days

### How It Works

```
┌─────────────┐     webhook      ┌─────────────┐
│  OneSignal  │ ───────────────► │  API Server │
│   Cloud     │                  │  (Railway)  │
└─────────────┘                  └──────┬──────┘
                                        │
                                        ▼
                                 ┌─────────────┐
                                 │  Postgres   │
                                 │  Database   │
                                 └──────┬──────┘
                                        │
                                        ▼
┌─────────────┐   GET /messages  ┌─────────────┐
│  iOS App    │ ◄─────────────── │  API Server │
│  (Inbox)    │                  │             │
└─────────────┘                  └─────────────┘
```

### iOS App Integration

```swift
// Fetch notification inbox
func fetchInbox() async throws -> [NotificationMessage] {
    let appId = "your-onesignal-app-id"
    let externalId = "user-external-id"
    let url = URL(string: "https://your-api.railway.app/messages/\(appId)/\(externalId)")!

    let (data, _) = try await URLSession.shared.data(from: url)
    let response = try JSONDecoder().decode(MessagesResponse.self, from: data)
    return response.messages
}
```

---

## Database Schema

```sql
CREATE TABLE message_events (
    id UUID PRIMARY KEY,
    app_id VARCHAR(36) NOT NULL,        -- OneSignal App ID
    external_id VARCHAR(255) NOT NULL,  -- User identity
    event_type VARCHAR(50) NOT NULL,    -- notification.sent, .delivered, etc.
    notification_id VARCHAR(36),        -- Links related events
    message_contents JSONB,             -- Title, body, image, data
    event_payload JSONB,                -- Full webhook payload
    created_at TIMESTAMP WITH TIME ZONE
);

-- Index for fast user lookups
CREATE INDEX idx_user_lookup ON message_events (app_id, external_id, created_at DESC);
```

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | For webhooks | Postgres connection string (auto-set by Railway) |
| `signal_post_app_id` | Yes | Signal Post OneSignal App ID |
| `signal_post_api_key` | Yes | Signal Post OneSignal API Key |
| `KV_REST_API_URL` | For OTP | Vercel KV URL |
| `KV_REST_API_TOKEN` | For OTP | Vercel KV Token |
| `ENVIRONMENT` | No | `development` or `production` |

---

## Version History

- **2.1.0** - Added webhook storage and notification inbox endpoints
- **2.0.2** - Added demo mode with configurable notification intervals
- **2.0.0** - Major refactor with improved structure
- **1.0.0** - Initial release
