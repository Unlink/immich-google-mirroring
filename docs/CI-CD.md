# GitHub Actions CI/CD

Projekt má automatizované GitHub Actions workflows pre:
- Docker image build a push
- Testovanie Docker image
- Automatické releases

## Workflows

### 1. docker-test.yml

**Spustí sa pri:**
- Pull request na `main`
- Manuálne spustenie (`workflow_dispatch`)

**Čo robí:**
- Build Docker image (test)
- Spustí container a testuje zdravotný check
- Testuje Python syntax

**Doba trvania:** ~3-5 minút

### 2. docker-publish.yml

**Spustí sa pri:**
- Push na `main` branch
- Push Git tagu `v*`
- Pull request na `main`
- Manuálne spustenie (`workflow_dispatch`)

**Čo robí:**
- Vyčíta verziu z `app/__version__.py`
- Build Docker image pre `linux/amd64` a `linux/arm64`
- Push na GitHub Container Registry (ghcr.io)

**Tagy pre images:**
- `latest` (len na main branch)
- `main` (na main branch)
- `pr-<number>` (na pull requests)
- `v1.0.0` (pre tagged releases)
- `sha-<commit>` (commit hash)

**Doba trvania:** ~10-15 minút

**Príklad:**
```bash
# Keď pushnete na main:
docker pull ghcr.io/<owner>/immich-google-sync:latest
docker pull ghcr.io/<owner>/immich-google-sync:main

# Keď pushnete tag v1.0.0:
docker pull ghcr.io/<owner>/immich-google-sync:1.0.0
docker pull ghcr.io/<owner>/immich-google-sync:latest
```

### 3. release.yml

**Spustí sa pri:**
- Push Git tagu `v*` (automaticky)

**Čo robí:**
1. Vyčíta verziu z tagu
2. Extrahuje changelog pre danú verziu
3. Vytvorí GitHub Release s descriptionom
4. Build a push Docker image s taggom verzie

**Doba trvania:** ~15-20 minút

## Ako funguje release

### Automatický proces

```bash
# 1. Aktualizovať CHANGELOG.md a verziu
./release.ps1 1.0.1

# Alebo manuálne:
./version.ps1 set 1.0.1
# (editovať CHANGELOG.md)
git add app/__version__.py CHANGELOG.md docker-compose.yml
git commit -m "chore(release): v1.0.1"
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin main
git push origin v1.0.1

# GitHub Actions automaticky:
# - Vytvorí Release na GitHube
# - Build Docker image
# - Push image na registry
```

### What each workflow does:

1. **release.yml** spustí sa prvá (keď je tag pushnený)
   - Vytvorí GitHub Release
   - Spustí `docker-publish.yml` workflow

2. **docker-publish.yml** spustí sa
   - Build Docker image pre obe platformy
   - Push na registry s taggom verzie

## Monitoring workflow progress

### GitHub UI

1. Prejdite na https://github.com/<owner>/immich-google-mirroring/actions
2. Vyberte workflow na ľavej strane
3. Kliknite na príslušný run
4. Vidíte progress a logov

### Logov

Kliknutie na konkrétny krok zobrazí detailné logy.

## Troubleshooting

### Docker build zlyhá

**Príčiny:**
- `Dockerfile` syntax error
- Chýbajúci súbor
- Build arg problém

**Riešenie:**
1. Skontrolujte Dockerfile
2. Skontrolujte workflow logy
3. Testujte build lokálne: `docker build .`

### Push na registry zlyhá

**Príčiny:**
- `GITHUB_TOKEN` nemá permissions
- Nie ste v GitHub Actions environment

**Riešenie:**
- `GITHUB_TOKEN` by mal byť automaticky dostupný
- Skontrolujte `permissions` sekciu vo workflow

### Release nie je vytvorený

**Príčiny:**
- Tag nebol pushnený (`git push origin v1.0.0`)
- Tag nie je vo formáte `v*`
- Workflow má error

**Riešenie:**
1. Skontrolujte či bol tag pushnený: `git push origin v1.0.0`
2. Skontrolujte logy workflow
3. Skontrolujte format tagu (musí byť `v1.0.0`)

## Docker Image Tags Explained

Workflow automaticky vytváva nasledujúce tagy:

| Tag Pattern | Prípad použitia | Príklad |
|---|---|---|
| `latest` | Default tag (main branch) | `latest` |
| `main` | Main branch | `main` |
| `pr-<number>` | Pull request | `pr-123` |
| `v<version>` | Git tag | `v1.0.0` |
| `<version>` | Semantic version | `1.0.0` |
| `<major>.<minor>` | Minor version | `1.0` |
| `<major>` | Major version | `1` |
| `sha-<short>` | Commit hash | `sha-abc1234` |

## Build Arguments

Docker image je buildovaný s nasledujúcimi argumentmi:

- `BUILD_DATE` - Timestamp build-u (z git commit)
- `VCS_REF` - Git commit SHA
- `VERSION` - Verzia z `app/__version__.py` alebo tagu

Tieto sú uložené ako `LABEL` v image pre metadata.

## Performance

### Build cache

Workflow používa GitHub Actions cache pre:
- Docker layers (type=gha)
- Python packages (ak by boli)

To znižuje čas buildu na ďalšie pushe.

### Multi-platform builds

- `linux/amd64` - x86_64 (väčšina serverov)
- `linux/arm64` - ARM64 (Apple Silicon, AWS Graviton)

Build trvá dlhšie pre multi-platform, ale image funguje na oboch platformách.

## Integration with versioning

Workflow automaticky vyčítava verziu z `app/__version__.py`:

```python
__version__ = "1.0.0"
```

To zabezpečuje, že:
- Image tag vždy zodpovedá verzii v kóde
- Release changelog je pre správnu verziu
- Nie je riziká nesúladu verzií
