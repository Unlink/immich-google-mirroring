# Immich → Google Photos Sync

Dockerized Python FastAPI application that synchronizes Immich albums to Google Photos with automatic deduplication and scheduling.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment options
- **[Architecture](ARCHITECTURE.md)** - System design and data flow
- **[Contributing](CONTRIBUTING.md)** - How to contribute
- **[Changelog](CHANGELOG.md)** - Version history

## Features

- 🔄 **Automatic Sync**: Schedule periodic synchronization from Immich to Google Photos
- 🎯 **Album Mirroring**: Select specific Immich album to sync to Google Photos
- 🔐 **Secure**: Encrypted storage of API keys and tokens using Fernet encryption
- 📊 **Web Dashboard**: Monitor sync status, view logs, and control synchronization
- 🚫 **Deduplication**: Smart fingerprint-based deduplication (checksum + timestamp)
- 📝 **Sync History**: Track all sync runs with detailed statistics and logs
- 🔑 **OAuth2**: Secure Google Photos authentication with refresh token support

## Architecture

- **Backend**: Python 3.12 + FastAPI
- **Database**: SQLite with SQLAlchemy (async)
- **OAuth**: Google OAuth2 web flow with append-only scope
- **Scheduler**: APScheduler for background jobs
- **UI**: Server-rendered templates with Jinja2
- **Containerization**: Docker + docker-compose

## Quick Start

### Prerequisites

1. **Immich Instance** with API access
2. **Google Cloud Project** with Photos Library API enabled:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing
   - Enable "Photos Library API"
   - Create OAuth 2.0 credentials (Web application)
   - Add authorized redirect URI: `http://your-server:8080/auth/google/callback`

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd immich-google-mirroring
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Edit `.env` and set your configuration:
```env
APP_SECRET_KEY=your-secret-key-at-least-32-chars-long
BASE_URL=http://localhost:8080
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
DATABASE_PATH=/data/app.db
LOG_PATH=/data/logs
```

4. Start with Docker Compose:
```bash
docker-compose up -d
```

5. Access the web UI at `http://localhost:8080`

## Setup Guide

### Step 1: Configure Immich Connection

1. Navigate to **Settings** page
2. Enter your Immich URL (e.g., `https://immich.example.com`)
3. Enter your Immich API Key (create in Immich → Account Settings → API Keys)
4. Click "Test Connection" to verify
5. Click "Save Configuration"

### Step 2: Select Album

1. Navigate to **Albums** page
2. Browse your Immich albums
3. Click "Select" on the album you want to sync

### Step 3: Connect Google Photos

1. Navigate to **Google Auth** page
2. Click "Connect Google Photos"
3. Complete OAuth consent flow
4. Grant permissions for Photos Library API

### Step 4: Configure Sync

1. Navigate to **Sync** page
2. Click "▶ Run Sync Now" to test manual sync
3. Enable "Auto Sync" for scheduled synchronization
4. Set sync interval (default: 60 minutes)

## Database Schema

### Tables

**app_config** - Application configuration
- Immich URL, API key (encrypted)
- Selected album information
- Google refresh token (encrypted)
- Sync schedule settings

**sync_items** - Individual asset tracking
- Immich asset ID, checksum, metadata
- Google media item ID
- Sync status (OK/FAILED/PENDING/ORPHANED)
- Last sync timestamp

**sync_runs** - Sync execution history
- Start/finish timestamps
- Status (RUNNING/OK/FAILED/CANCELLED)
- Counters: total, uploaded, skipped, failed
- Log excerpts

## API Endpoints

### Configuration
- `POST /api/config/immich` - Update Immich settings
- `POST /api/config/immich/test` - Test Immich connection
- `POST /api/config/album` - Select album
- `POST /api/config/sync` - Update sync settings
- `GET /api/config/status` - Get config status

### Authentication
- `GET /auth/google/start` - Start OAuth flow
- `GET /auth/google/callback` - OAuth callback
- `GET /auth/google/status` - Check auth status
- `POST /auth/google/disconnect` - Disconnect Google

### Sync Operations
- `POST /api/sync/run` - Trigger sync now
- `GET /api/sync/runs` - List recent runs
- `GET /api/sync/runs/{id}` - Get run details
- `GET /api/sync/status` - Get current status
- `GET /api/sync/items` - List sync items

### Immich
- `GET /api/immich/albums` - List Immich albums

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_SECRET_KEY` | Encryption key for secrets | `changeme-generate-random-key` |
| `BASE_URL` | Application base URL | `http://localhost:8080` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | - |
| `DATABASE_PATH` | SQLite database path | `/data/app.db` |
| `LOG_PATH` | Log files directory | `/data/logs` |

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export APP_SECRET_KEY="your-secret-key"
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export BASE_URL="http://localhost:8080"
export DATABASE_PATH="./data/app.db"

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── config.py              # Application settings
│   ├── main.py                # FastAPI application
│   ├── database.py            # Database connection
│   ├── models.py              # SQLAlchemy models
│   ├── scheduler.py           # APScheduler integration
│   ├── clients/               # API clients
│   │   ├── immich.py          # Immich API client
│   │   └── google.py          # Google Photos client
│   ├── routes/                # FastAPI routes
│   │   ├── pages.py           # Web UI pages
│   │   ├── config.py          # Config API
│   │   ├── auth.py            # OAuth endpoints
│   │   ├── sync.py            # Sync API
│   │   └── immich.py          # Immich API
│   ├── sync/                  # Sync engine
│   │   └── engine.py          # Sync logic
│   ├── templates/             # Jinja2 templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── settings.html
│   │   ├── albums.html
│   │   ├── google.html
│   │   └── sync.html
│   └── utils/                 # Utilities
│       ├── encryption.py      # Fernet encryption
│       └── config.py          # Config manager
├── data/                      # Persistent data (volume)
│   ├── app.db                 # SQLite database
│   └── logs/                  # Application logs
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Sync Algorithm

1. **Initialize**: Load configuration and authenticate clients
2. **Ensure Album**: Create or find Google Photos album
3. **Fetch Assets**: Get all assets from Immich album
4. **Process Each Asset**:
   - Calculate fingerprint (checksum or timestamp+filename)
   - Check sync_items table for existing entry
   - If fingerprint matches → skip (already synced)
   - If new/changed:
     - Download from Immich (streaming)
     - Upload to Google Photos
     - Create media item in album
     - Update sync_items table
5. **Track Progress**: Update counters and logs
6. **Complete**: Mark run as OK/FAILED

## Security Considerations

- ✅ API keys and tokens encrypted at rest (Fernet)
- ✅ OAuth2 with state parameter for CSRF protection
- ✅ Refresh tokens stored securely
- ✅ No sensitive data in logs
- ⚠️ Consider adding basic auth for web UI in production
- ⚠️ Use strong `APP_SECRET_KEY` (at least 32 characters)
- ⚠️ HTTPS recommended for production deployment

## Troubleshooting

### Sync Failed - Authentication Error
- Check if Google OAuth token is still valid
- Try disconnecting and reconnecting Google Photos

### Assets Not Uploading
- Verify Google Photos API quotas
- Check Immich asset accessibility
- Review sync run logs for specific errors

### Database Locked Errors
- Ensure only one instance is running
- Check file permissions on `/data` volume

### OAuth Redirect Mismatch
- Verify `BASE_URL` matches your actual URL
- Update redirect URI in Google Cloud Console

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.