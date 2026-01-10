# Quick Reference Guide

## 🚀 Quick Start (5 minutes)

```bash
# 1. Clone and setup
git clone <repo-url>
cd immich-google-mirroring
cp .env.example .env

# 2. Generate secret key
python3 generate_key.py
# Copy the generated key to .env

# 3. Add Google OAuth credentials to .env
# GOOGLE_CLIENT_ID=...
# GOOGLE_CLIENT_SECRET=...

# 4. Start the app
docker-compose up -d

# 5. Open browser
# http://localhost:8080
```

## 📋 Essential Commands

### Docker Commands
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Rebuild after code changes
docker-compose build
docker-compose up -d
```

### Development Commands
```bash
# Local development
./dev-start.sh

# Run tests
python3 test_basic.py

# Generate secret key
python3 generate_key.py
```

### Database Commands
```bash
# Backup database
docker-compose exec immich-gphotos-sync cp /data/app.db /data/backup.db

# From host
cp data/app.db data/backup-$(date +%Y%m%d).db

# Restore database
cp data/backup.db data/app.db
docker-compose restart
```

## 🔧 Configuration

### Required Environment Variables
```env
APP_SECRET_KEY=<generate-with-generate_key.py>
GOOGLE_CLIENT_ID=<from-google-cloud-console>
GOOGLE_CLIENT_SECRET=<from-google-cloud-console>
BASE_URL=http://localhost:8080
```

### Google Cloud Console Setup
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create project → Enable Photos Library API
3. Create OAuth credentials (Web application)
4. Add redirect URI: `http://your-url:8080/auth/google/callback`
5. Copy Client ID and Secret to `.env`

## 📊 API Quick Reference

### Health Check
```bash
curl http://localhost:8080/health
```

### Trigger Sync
```bash
curl -X POST http://localhost:8080/api/sync/run
```

### Get Status
```bash
curl http://localhost:8080/api/sync/status
```

### List Sync Runs
```bash
curl http://localhost:8080/api/sync/runs
```

### Get Config Status
```bash
curl http://localhost:8080/api/config/status
```

## 🐛 Troubleshooting

### Container won't start
```bash
docker-compose logs
docker-compose ps
```

### Database locked
```bash
# Stop container
docker-compose down

# Check for other processes
lsof data/app.db

# Restart
docker-compose up -d
```

### OAuth errors
- Verify `BASE_URL` matches your actual URL
- Check Google Cloud Console redirect URI matches
- Ensure Photos Library API is enabled

### Sync not running
- Check config status: `http://localhost:8080/api/config/status`
- Verify Immich connection in Settings
- Check Google auth in Google Auth page
- Review logs: `docker-compose logs -f`

## 📁 File Locations

### Important Files
- **Configuration**: `data/app.db` (SQLite)
- **Logs**: `data/logs/app.log`
- **Environment**: `.env`

### Backup These Files
```bash
data/app.db          # Database with all config and history
.env                 # Environment configuration
```

## 🔐 Security Checklist

- [ ] Generated strong `APP_SECRET_KEY` (32+ chars)
- [ ] Using HTTPS in production
- [ ] Restricted network access (firewall)
- [ ] Regular database backups
- [ ] OAuth credentials secured
- [ ] Logs monitored for errors
- [ ] Updated to latest version

## 📱 Web UI Pages

- `/` - Dashboard (overview)
- `/settings` - Immich configuration
- `/albums` - Select album to sync
- `/google` - Google OAuth
- `/sync` - Sync control and history

## 💡 Tips

### Reduce Memory Usage
Set smaller sync intervals or process fewer items at once.

### Speed Up Sync
Increase concurrency in `sync/engine.py` (be careful with rate limits).

### Monitor Performance
```bash
# Watch logs in real-time
docker-compose logs -f | grep "Sync"

# Check container resources
docker stats immich-gphotos-sync
```

### Schedule Backup
```bash
# Add to crontab
0 2 * * * cp /path/to/data/app.db /path/to/backups/app-$(date +\%Y\%m\%d).db
```

## 🆘 Support

- **Documentation**: [README.md](README.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: GitHub Issues
- **Logs**: Check `data/logs/app.log`

## 🔄 Update Process

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs -f
```
