# Deployment Guide

## Docker Deployment (Recommended)

### Using Docker Compose

1. **Clone the repository**:
```bash
git clone https://github.com/your-username/immich-google-mirroring.git
cd immich-google-mirroring
```

2. **Configure environment**:
```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

3. **Generate secure secret key**:
```bash
python3 generate_key.py
```

4. **Start the service**:
```bash
docker-compose up -d
```

5. **Check logs**:
```bash
docker-compose logs -f
```

6. **Access the UI**:
Open `http://your-server:8080` in your browser

### Using Docker directly

```bash
# Build image
docker build -t immich-google-sync .

# Run container
docker run -d \
  --name immich-google-sync \
  -p 8080:8080 \
  -v ./data:/data \
  -e APP_SECRET_KEY=your-secret-key \
  -e GOOGLE_CLIENT_ID=your-client-id \
  -e GOOGLE_CLIENT_SECRET=your-client-secret \
  -e BASE_URL=http://localhost:8080 \
  immich-google-sync
```

## Manual Deployment

### Prerequisites

- Python 3.12+
- pip

### Installation

1. **Clone and setup**:
```bash
git clone https://github.com/your-username/immich-google-mirroring.git
cd immich-google-mirroring
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Create data directory**:
```bash
mkdir -p data/logs
```

4. **Run the application**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### Systemd Service (Linux)

Create `/etc/systemd/system/immich-google-sync.service`:

```ini
[Unit]
Description=Immich Google Photos Sync
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/immich-google-mirroring
Environment="PATH=/path/to/immich-google-mirroring/venv/bin"
EnvironmentFile=/path/to/immich-google-mirroring/.env
ExecStart=/path/to/immich-google-mirroring/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable immich-google-sync
sudo systemctl start immich-google-sync
sudo systemctl status immich-google-sync
```

## Reverse Proxy Setup

### Nginx

```nginx
server {
    listen 80;
    server_name sync.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

For HTTPS with Let's Encrypt:
```bash
sudo certbot --nginx -d sync.example.com
```

### Traefik (Docker)

Add labels to docker-compose.yml:

```yaml
services:
  immich-gphotos-sync:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.sync.rule=Host(`sync.example.com`)"
      - "traefik.http.routers.sync.entrypoints=websecure"
      - "traefik.http.routers.sync.tls.certresolver=letsencrypt"
      - "traefik.http.services.sync.loadbalancer.server.port=8080"
```

## Cloud Deployment

### DigitalOcean App Platform

1. Fork the repository
2. Create new App in DigitalOcean
3. Select your GitHub repository
4. Configure environment variables
5. Deploy

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create immich-google-sync

# Set environment variables
heroku config:set APP_SECRET_KEY=your-secret-key
heroku config:set GOOGLE_CLIENT_ID=your-client-id
heroku config:set GOOGLE_CLIENT_SECRET=your-client-secret
heroku config:set BASE_URL=https://your-app.herokuapp.com

# Deploy
git push heroku main
```

### Railway

1. Click "Deploy on Railway"
2. Connect GitHub repository
3. Add environment variables
4. Deploy

## Production Considerations

### Security

1. **Use HTTPS**: Always use HTTPS in production
2. **Strong Secret Key**: Generate a secure random key
3. **Basic Auth**: Consider adding basic authentication
4. **Firewall**: Restrict access to trusted networks

### Performance

1. **Database Backups**: Regularly backup `/data/app.db`
2. **Log Rotation**: Configure log rotation for `/data/logs`
3. **Resource Limits**: Set appropriate Docker memory/CPU limits

### Monitoring

1. **Health Checks**: Use `/health` endpoint
2. **Logs**: Monitor application logs
3. **Alerts**: Set up alerts for failed syncs

### Backups

```bash
# Backup database
docker-compose exec immich-gphotos-sync cp /data/app.db /data/app.db.backup

# Or from host
cp data/app.db data/app.db.backup.$(date +%Y%m%d)
```

### Updates

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker-compose logs
```

Verify environment variables:
```bash
docker-compose config
```

### Permission errors

Fix data directory permissions:
```bash
sudo chown -R 1000:1000 data/
```

### Database locked

Ensure only one instance is running:
```bash
docker-compose ps
```

### OAuth redirect issues

Update `BASE_URL` to match your domain and update Google Cloud Console redirect URI.
