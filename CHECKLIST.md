# Setup Checklist

Use this checklist to ensure proper setup and configuration.

## Pre-Deployment

### Google Cloud Console Setup
- [ ] Created Google Cloud project
- [ ] Enabled "Photos Library API"
- [ ] Created OAuth 2.0 credentials (Web application type)
- [ ] Added redirect URI: `{YOUR_BASE_URL}/auth/google/callback`
- [ ] Copied Client ID to `.env`
- [ ] Copied Client Secret to `.env`

### Environment Configuration
- [ ] Copied `.env.example` to `.env`
- [ ] Generated secret key: `python3 generate_key.py`
- [ ] Set `APP_SECRET_KEY` in `.env`
- [ ] Set `BASE_URL` to match your actual URL
- [ ] Set `GOOGLE_CLIENT_ID` in `.env`
- [ ] Set `GOOGLE_CLIENT_SECRET` in `.env`
- [ ] Verified all required variables are set

### Immich Preparation
- [ ] Immich instance is running and accessible
- [ ] Created API key in Immich (Account Settings → API Keys)
- [ ] Noted Immich URL
- [ ] Selected album to sync

## Deployment

### Docker Deployment (Recommended)
- [ ] Docker is installed and running
- [ ] Docker Compose is installed
- [ ] Ran `docker-compose up -d`
- [ ] Verified container is running: `docker-compose ps`
- [ ] Checked logs: `docker-compose logs -f`
- [ ] Accessed UI at `http://localhost:8080` (or your URL)

### Manual Deployment
- [ ] Python 3.12+ is installed
- [ ] Created virtual environment
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Created data directories: `mkdir -p data/logs`
- [ ] Started application: `uvicorn app.main:app --host 0.0.0.0 --port 8080`

## Initial Configuration

### Step 1: Immich Configuration
- [ ] Opened web UI
- [ ] Navigated to Settings page
- [ ] Entered Immich URL
- [ ] Entered Immich API key
- [ ] Clicked "Test Connection" - verified success
- [ ] Clicked "Save Configuration"

### Step 2: Album Selection
- [ ] Navigated to Albums page
- [ ] Verified albums loaded from Immich
- [ ] Selected desired album
- [ ] Verified selection was saved

### Step 3: Google Authentication
- [ ] Navigated to Google Auth page
- [ ] Clicked "Connect Google Photos"
- [ ] Completed OAuth consent flow
- [ ] Granted required permissions
- [ ] Verified "Connected" status shows
- [ ] Verified email/account name displays

### Step 4: First Sync
- [ ] Navigated to Sync page
- [ ] Clicked "Run Sync Now"
- [ ] Verified sync started
- [ ] Monitored progress in real-time
- [ ] Checked sync completed successfully
- [ ] Verified assets appeared in Google Photos

## Post-Deployment

### Verification
- [ ] Checked dashboard shows correct stats
- [ ] Verified sync history appears
- [ ] Checked logs for any errors
- [ ] Tested manual sync again
- [ ] Verified deduplication (same items not re-uploaded)

### Scheduling (Optional)
- [ ] Enabled "Auto Sync" on Sync page
- [ ] Set desired interval (default: 60 minutes)
- [ ] Verified scheduled sync runs automatically
- [ ] Monitored a few automatic runs

### Security
- [ ] Changed default `APP_SECRET_KEY` to strong random value
- [ ] Verified `.env` file is not in version control
- [ ] Set appropriate file permissions on `data/` directory
- [ ] Configured firewall if needed
- [ ] Set up HTTPS if exposing to internet

### Backup
- [ ] Created backup of `data/app.db`
- [ ] Saved `.env` file securely
- [ ] Documented backup location
- [ ] Set up automated backup schedule (optional)

## Troubleshooting Checks

If something doesn't work, verify:

### Container Issues
- [ ] Container is running: `docker-compose ps`
- [ ] No errors in logs: `docker-compose logs`
- [ ] Ports are not in use: `netstat -an | grep 8080`
- [ ] Volume permissions are correct

### Immich Connection
- [ ] Immich URL is correct (no trailing slash)
- [ ] API key is valid
- [ ] Immich server is accessible from container
- [ ] Network connectivity is working

### Google OAuth
- [ ] `BASE_URL` exactly matches actual URL
- [ ] Redirect URI in Google Console matches
- [ ] Photos Library API is enabled
- [ ] OAuth credentials are correct
- [ ] Browser allows cookies/redirects

### Sync Issues
- [ ] All previous steps completed
- [ ] Album has assets
- [ ] No sync currently running
- [ ] Check logs for specific errors
- [ ] Verify disk space available

## Maintenance

### Regular Tasks
- [ ] Monitor sync runs weekly
- [ ] Check logs for errors
- [ ] Backup database monthly
- [ ] Update to latest version when available

### When Adding New Albums
- [ ] Select new album in Albums page
- [ ] Run manual sync first
- [ ] Verify sync completes
- [ ] Re-enable auto sync if needed

### When Changing Immich
- [ ] Update URL/API key in Settings
- [ ] Test connection
- [ ] Re-select album if needed
- [ ] Run test sync

## Success Criteria

You're all set when:
- ✅ Web UI is accessible
- ✅ Immich connection works
- ✅ Google authentication successful
- ✅ Manual sync completes successfully
- ✅ Assets appear in Google Photos
- ✅ No errors in logs
- ✅ Auto sync running (if enabled)

## Getting Help

If you encounter issues:

1. **Check logs**: `docker-compose logs -f` or `data/logs/app.log`
2. **Review documentation**:
   - [README.md](README.md) - Main docs
   - [QUICKSTART.md](QUICKSTART.md) - Quick reference
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
3. **Common issues**: See Troubleshooting section in README.md
4. **GitHub Issues**: Search or create new issue

## Notes

- Keep your `.env` file secure
- Regular backups recommended
- Monitor Google Photos storage quota
- Check Immich server health
- Review sync logs periodically

---

**Last Updated**: 2026-01-10
