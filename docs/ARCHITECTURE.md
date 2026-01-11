# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Web Browser (User)                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ HTTP/HTTPS
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                      FastAPI Application                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Web UI     │  │  API Routes  │  │ Auth Routes  │             │
│  │  (Jinja2)    │  │   (REST)     │  │  (OAuth2)    │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                  │                  │                     │
│  ┌──────▼──────────────────▼──────────────────▼───────┐            │
│  │           Business Logic Layer                      │            │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────┐ │            │
│  │  │Config Mgr  │  │ Sync Engine│  │  Scheduler   │ │            │
│  │  └──────┬─────┘  └─────┬──────┘  └──────┬───────┘ │            │
│  └─────────┼──────────────┼─────────────────┼─────────┘            │
│            │              │                  │                      │
│  ┌─────────▼──────────────▼──────────────────▼─────────┐           │
│  │            Database Layer (SQLAlchemy)               │           │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────┐     │           │
│  │  │AppConfig │  │ SyncItems │  │  SyncRuns    │     │           │
│  │  └──────────┘  └───────────┘  └──────────────┘     │           │
│  └────────────────────────┬──────────────────────────────┘          │
│                           │                                         │
│  ┌────────────────────────▼──────────────────────────────┐         │
│  │         SQLite Database (/data/app.db)                │         │
│  │  • Encrypted credentials                              │         │
│  │  • Sync history                                       │         │
│  │  • Item tracking                                      │         │
│  └───────────────────────────────────────────────────────┘         │
│                                                                     │
│  ┌──────────────────────────────────────────────────────┐          │
│  │            External API Clients                       │          │
│  │  ┌─────────────────┐      ┌──────────────────┐      │          │
│  │  │ Immich Client   │      │ Google Photos    │      │          │
│  │  │ (httpx)         │      │ Client (OAuth2)  │      │          │
│  │  └────────┬────────┘      └────────┬─────────┘      │          │
│  └───────────┼──────────────────────────┼────────────────┘          │
└──────────────┼──────────────────────────┼───────────────────────────┘
               │                          │
               │                          │
       ┌───────▼────────┐        ┌────────▼────────┐
       │  Immich Server │        │ Google Photos   │
       │                │        │     API         │
       │  • Albums      │        │  • OAuth2       │
       │  • Assets      │        │  • Upload       │
       │  • Download    │        │  • Albums       │
       └────────────────┘        └─────────────────┘
```

## Data Flow

### Setup Flow

```
1. User → Settings → Configure Immich (URL + API Key)
                  ↓
2. User → Albums → Select Album to Sync
                  ↓
3. User → Google Auth → OAuth2 Flow → Refresh Token Stored
                  ↓
4. User → Sync → Enable Auto Sync / Run Manual Sync
```

### Sync Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Trigger (Manual / Scheduled)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 2. Initialize Sync Run                                      │
│    • Create SyncRun record (status: RUNNING)                │
│    • Load config (Immich + Google credentials)              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 3. Ensure Google Photos Album                               │
│    • Create if not exists                                   │
│    • Store album_id in config                               │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 4. Fetch Assets from Immich Album                           │
│    • GET /api/album/{id}                                    │
│    • Get list of all assets                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 5. For Each Asset:                                          │
│    ┌─────────────────────────────────────────────────────┐  │
│    │ a. Calculate Fingerprint                            │  │
│    │    (checksum OR timestamp+filename)                 │  │
│    └────────┬────────────────────────────────────────────┘  │
│             │                                                │
│    ┌────────▼────────────────────────────────────────────┐  │
│    │ b. Check SyncItems table                            │  │
│    │    • Exists + same fingerprint? → SKIP              │  │
│    │    • New or changed? → Continue                     │  │
│    └────────┬────────────────────────────────────────────┘  │
│             │                                                │
│    ┌────────▼────────────────────────────────────────────┐  │
│    │ c. Download from Immich (streaming)                 │  │
│    │    GET /api/asset/file/{id}                         │  │
│    └────────┬────────────────────────────────────────────┘  │
│             │                                                │
│    ┌────────▼────────────────────────────────────────────┐  │
│    │ d. Upload to Google Photos                          │  │
│    │    POST /v1/uploads → uploadToken                   │  │
│    └────────┬────────────────────────────────────────────┘  │
│             │                                                │
│    ┌────────▼────────────────────────────────────────────┐  │
│    │ e. Create Media Item                                │  │
│    │    POST /v1/mediaItems:batchCreate                  │  │
│    │    (with uploadToken + albumId)                     │  │
│    └────────┬────────────────────────────────────────────┘  │
│             │                                                │
│    ┌────────▼────────────────────────────────────────────┐  │
│    │ f. Update SyncItems table                           │  │
│    │    • status = OK                                    │  │
│    │    • google_media_item_id                           │  │
│    │    • last_synced_at = now                           │  │
│    └─────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ 6. Complete Sync Run                                        │
│    • Update SyncRun (status: OK/FAILED)                     │
│    • Record: uploaded, skipped, failed counts               │
│    • Store log excerpt                                      │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Web UI (Jinja2 Templates)
- **dashboard.html**: Overview, stats, quick actions
- **settings.html**: Immich configuration, test connection
- **albums.html**: Browse and select Immich albums
- **google.html**: OAuth flow, connection status
- **sync.html**: Sync control, run history, logs

### API Routes (FastAPI)
- **/api/config**: Configuration management
- **/api/immich**: Immich operations (list albums)
- **/auth/google**: OAuth flow (start, callback, status)
- **/api/sync**: Sync operations (run, status, history)

### Clients
- **ImmichClient**: HTTP client for Immich API
  - test_connection()
  - list_albums()
  - get_album_assets()
  - download_original() (streaming)

- **GooglePhotosClient**: OAuth2 + Photos API
  - OAuth refresh token management
  - ensure_album()
  - upload_bytes() (streaming)
  - batch_create()

### Database Models
- **AppConfig**: Single row with all app configuration
- **SyncItem**: One row per asset, tracks sync status
- **SyncRun**: One row per sync execution

### Scheduler (APScheduler)
- Interval-based job
- Checks sync_enabled config
- Prevents concurrent runs
- Updates schedule dynamically

### Security
- **Encryption**: Fernet (symmetric) for API keys/tokens
- **OAuth2**: Standard web flow with state parameter
- **Storage**: All secrets encrypted at rest in DB

## Deployment Architecture

### Docker Container
```
┌─────────────────────────────────────────────┐
│  Docker Container                           │
│  ┌───────────────────────────────────────┐  │
│  │  FastAPI App (uvicorn)                │  │
│  │  Port 8080                            │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Volume Mounts:                             │
│  /data → ./data (persistent)                │
│    ├── app.db (SQLite)                      │
│    └── logs/ (application logs)             │
└─────────────────────────────────────────────┘
```

### Production with Reverse Proxy
```
Internet → Traefik/Nginx (HTTPS) → FastAPI (8080) → Data Volume
              ↓
          Let's Encrypt (SSL)
```
