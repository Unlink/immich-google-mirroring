# Version Management

Tento dokument popisuje systém správy verzií pre projekt Immich Google Photos Mirroring.

## Súčasná verzia

Súčasná verzia aplikácie: **1.0.0**

## Systém verziovania

Projekt používa [Semantic Versioning](https://semver.org/) s formátom `MAJOR.MINOR.PATCH`:

- **MAJOR** - Zvýšiť pri nepáratných zmenách (breaking changes)
- **MINOR** - Zvýšiť pri pridaní nových funkcii (backward compatible)
- **PATCH** - Zvýšiť pri opravách chýb (bug fixes)

## Umiestnenie verzie

Verzia je centrálne spravovaná v súbore `app/__version__.py`:

```python
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__title__ = "Immich Google Photos Mirroring"
__description__ = "Dockerized Python FastAPI application..."
```

Táto verzia je automaticky použitá v:
- API dokumentácii FastAPI (`/docs`)
- Logoch pri spustení aplikácie
- API endpoint `/api/version`
- Docker image tagoch

## Aktualizácia verzie

### Manuálna aktualizácia

1. Upravte súbor `app/__version__.py`:
```python
__version__ = "1.1.0"  # Nová verzia
__version_info__ = (1, 1, 0)
```

2. Aktualizujte `CHANGELOG.md` s informáciami o zmenách

3. Odovzdajte zmeny do Git repozitára s správou:
```bash
git add app/__version__.py CHANGELOG.md
git commit -m "chore(release): v1.1.0"
git tag -a v1.1.0 -m "Release version 1.1.0"
```

### Automatická aktualizácia cez CLI

```bash
# Zobraziť súčasnú verziu
python -m app.version_cli

# Aktualizovať na novú verziu
python -m app.version_cli update 1.1.0
```

## Prístup k verzii v kóde

### V Pythone

```python
from app import __version__, __title__, __description__

print(f"Running {__title__} v{__version__}")
```

### V API

Požiadajte endpoint `/api/version`:

```bash
curl http://localhost:8080/api/version
```

Odpoveď:
```json
{
  "version": "1.0.0",
  "name": "Immich Google Photos Mirroring",
  "description": "Dockerized Python FastAPI application..."
}
```

## Docker

### Build s verziotágom

```bash
docker build -t immich-google-mirroring:1.0.0 .
docker build -t immich-google-mirroring:latest .
```

### Docker Compose

V `docker-compose.yml` je verzia vrátená z API:

```bash
docker-compose ps
curl http://localhost:8080/api/version
```

## Maintenance

Verzia sa aktualizuje pri každom vydaní:

1. Pri pridaní nových funkcií → zvýšiť MINOR verziu
2. Pri oprave chýb → zvýšiť PATCH verziu
3. Pri breaking changes → zvýšiť MAJOR verziu

Vždy aktualizujte `CHANGELOG.md` s detailmi zmien.
