# Immich → Google Photos Sync

Dockerized Python FastAPI application that synchronizes Immich albums to Google Photos with automatic deduplication and scheduling.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Docker Build](https://github.com/Unlink/immich-google-mirroring/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/Unlink/immich-google-mirroring/actions/workflows/docker-publish.yml)

## Features

- 🔄 **Automatic Sync**: Schedule periodic synchronization from Immich to Google Photos
- 🎯 **Album Mirroring**: Select specific Immich album to sync to Google Photos
- 🔐 **Secure**: Encrypted storage of API keys and tokens using Fernet encryption
- 📊 **Web Dashboard**: Monitor sync status, view logs, and control synchronization
- 🚫 **Deduplication**: Smart fingerprint-based deduplication (checksum + timestamp)
- 📝 **Sync History**: Track all sync runs with detailed statistics and logs
- 🔑 **OAuth2**: Secure Google Photos authentication with refresh token support

## 🚀 Quick Start (5 minutes)

### Prerequisites

1. **Immich Instance** with API access
2. **Google Cloud Project** with Photos Library API enabled:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing
   - Enable "Photos Library API"
   - Create OAuth 2.0 credentials (Web application)
   - Add authorized redirect URI: `http://your-server:8080/auth/google/callback`

### Installation

```bash
# 1. Clone and setup
git clone https://github.com/Unlink/immich-google-mirroring.git
cd immich-google-mirroring

# 2. Create environment file
cp .env.example .env

# 3. Generate secret key
python3 generate_key.py
# Copy the generated key to .env as APP_SECRET_KEY

# 4. Add your Google OAuth credentials to .env
# GOOGLE_CLIENT_ID=...
# GOOGLE_CLIENT_SECRET=...
# BASE_URL=http://your-server:8080

# 5. Start the application
docker-compose up -d

# 6. Access the web UI
# Open http://localhost:8080 in your browser
```

### Initial Configuration

1. **Settings** → Configure your Immich URL and API Key
2. **Albums** → Select which album to sync
3. **Google Auth** → Connect your Google Photos account
4. **Sync** → Enable auto-sync or run manual sync

## 🔧 Common Commands

### Initial Configuration

1. **Settings** → Configure your Immich URL and API Key
2. **Albums** → Select which album to sync
3. **Google Auth** → Connect your Google Photos account
4. **Sync** → Enable auto-sync or run manual sync

## 🔧 Common Commands

### Docker Management
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Update to latest version
docker-compose pull
docker-compose up -d
```

### Backup & Restore
```bash
# Backup database
cp data/app.db data/backup-$(date +%Y%m%d).db

# Restore database
cp data/backup.db data/app.db
docker-compose restart
```

## 🐛 Troubleshooting

### Container won't start
```bash
docker-compose logs
docker-compose ps
```

### OAuth errors
- Verify `BASE_URL` in `.env` matches your actual URL
- Check Google Cloud Console redirect URI matches exactly
- Ensure Photos Library API is enabled in Google Cloud

### Sync not running
- Check `/settings` - verify Immich connection works
- Check `/google` - ensure Google is connected
- Review logs: `docker-compose logs -f`

## 📁 Important Files

- **Configuration**: `data/app.db` (SQLite database)
- **Logs**: `data/logs/app.log`
- **Environment**: `.env` (secrets and settings)
- **Backup**: Always backup `data/app.db` before updates

## 🔐 Security Tips

- ✅ Generate strong `APP_SECRET_KEY` (use `generate_key.py`)
- ✅ Use HTTPS in production
- ✅ Regular database backups
- ✅ Keep OAuth credentials secure
- ⚠️ Consider adding basic auth for web UI in production

## 📚 Advanced Documentation

For detailed information, see the [docs](docs/) directory:
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment options
- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [Contributing](docs/CONTRIBUTING.md) - How to contribute

## Technology Stack

- **Backend**: Python 3.12 + FastAPI
- **Database**: SQLite with SQLAlchemy (async)
- **OAuth**: Google OAuth2 web flow
- **Scheduler**: APScheduler for background jobs
- **UI**: Server-rendered templates with Jinja2
- **Container**: Docker + docker-compose

## License

MIT License - see [LICENSE](LICENSE) file for details.