# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Fixed
- Fixed autosync not starting when enabled - scheduler is now properly updated when sync settings are changed

### Changed

### Removed

## [1.0.1] - 2026-01-11

### Added
- Version management system with semantic versioning
- GitHub Actions workflows for automated releases
- CLI tools for version management (`version.ps1`, `version.sh`, `version_cli.py`)
- API endpoint `/api/version` to get application version information
- Release documentation in `docs/RELEASE.md` and `docs/VERSIONING.md`

## [1.0.0] - 2026-01-10

### Added
- Initial release
- FastAPI-based web application
- Immich API client integration
- Google Photos API integration with OAuth2
- SQLite database for configuration and sync tracking
- Encrypted storage for API keys and tokens
- Web UI with dashboard, settings, and sync control
- Background scheduler for automatic sync
- Deduplication based on fingerprint (checksum/timestamp)
- Sync history and logging
- Docker containerization
- Comprehensive documentation

### Features
- Album selection from Immich
- Manual and scheduled sync
- Real-time sync status
- Log viewer
- OAuth2 web flow for Google Photos
- Automatic album creation in Google Photos
- Streaming uploads to minimize memory usage
- Detailed sync statistics

### Security
- Fernet encryption for sensitive data
- OAuth2 state parameter for CSRF protection
- Secure token storage
- No sensitive data in logs
