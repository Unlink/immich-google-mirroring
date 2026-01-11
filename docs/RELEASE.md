# Release Process

Tento dokument popisuje ako vytvoriť nové releases projektu Immich Google Photos Mirroring.

## Automatizovaný proces (Recommended)

Projekt má GitHub Actions workflows na automatizáciu:
- **docker-publish.yml** - Build a push Docker image na zmeny v main a tagy
- **release.yml** - Automaticky vytvorí GitHub Release a naklikuje tagg

### Krok 1: Aktualizujte verziu

```bash
# Aktualizovať verziu v kóde (podľa typu zmien)
./version.ps1 bump patch    # alebo: minor, major
# alebo
./version.sh bump patch
```

Alebo manuálne:
```bash
./version.ps1 set 1.1.0
./version.sh set 1.1.0
```

### Krok 2: Aktualizujte CHANGELOG.md

Pridajte položky pre novú verziu na začiatok súboru:

```markdown
## [1.1.0] - 2026-01-11

### Added
- Nová funkcia X
- Nová funkcia Y

### Fixed
- Opravená chyba A
- Opravená chyba B

### Changed
- Zmenená funkcionalita C

### Removed
- Odstránená zastaraná funkcia D

## [1.0.0] - 2025-12-20
...
```

### Krok 3: Commitnite zmeny

```bash
git add app/__version__.py CHANGELOG.md docker-compose.yml
git commit -m "chore(release): v1.1.0"
```

### Krok 4: Vytvorte Git tag

```bash
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin main
git push origin v1.1.0
```

## Čo sa stane automaticky

Keď pushnete tag `v*`:

1. ✅ **docker-publish workflow** spustí build Docker image
   - Build pre `linux/amd64` a `linux/arm64`
   - Push na `ghcr.io/<owner>/immich-google-sync:1.1.0`
   - Push na `ghcr.io/<owner>/immich-google-sync:latest`

2. ✅ **release workflow** spustí:
   - Extrahuje verziu z tagu (`v1.1.0` → `1.1.0`)
   - Extrahuje changelog z `CHANGELOG.md`
   - Vytvorí GitHub Release s descriptionom
   - Pushne Docker image s konkrétnym tagom

## Štruktúra CHANGELOG.md

Projekt používa [Keep a Changelog](https://keepachangelog.com/) formát:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-01-11

### Added
- Nový feature

### Fixed
- Bug fix

## [1.0.0] - 2025-12-20
...
```

## Príklad kompletného release procesu

```bash
# 1. Aktualizovať verziu
.\version.ps1 set 1.1.0

# 2. Aktualizovať CHANGELOG.md
# (manuálne editovať súbor)

# 3. Commit
git add app/__version__.py CHANGELOG.md docker-compose.yml
git commit -m "chore(release): v1.1.0"

# 4. Tag a push
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin main
git push origin v1.1.0

# GitHub Actions potom automaticky:
# - Build Docker image
# - Push na registry
# - Vytvorí GitHub Release
```

## Aktuálne releases

Všetky releases sú dostupné na:
- GitHub: https://github.com/Unlink/immich-google-mirroring/releases
- Docker: https://ghcr.io/unlink/immich-google-sync

## CI/CD Workflows

### docker-publish.yml

Spustí sa pri:
- Push na `main` branch
- Push Git tagu `v*`
- Pull request na `main`
- Manuálne spustenie (`workflow_dispatch`)

### release.yml

Spustí sa len pri:
- Push Git tagu `v*` (automaticky vytvára Release)

## Troubleshooting

### GitHub Actions zlyhali

Skontrolujte:
1. Logs na https://github.com/<owner>/immich-google-mirroring/actions
2. Či ste pushli tag správne: `git push origin v1.1.0`
3. Či je `GITHUB_TOKEN` dostupný (mal by byť defaultne)

### Docker image sa nepushnul

Skontrolujte:
1. Máte dostup k `ghcr.io`
2. Dockerfile je správny
3. Build argumenty sú dostupné

### Release na GitHube nie je vytvorený

1. Skontrolujte či bol tag pushnený
2. Skontrolujte `release.yml` workflow logs
3. Overitie, že máte `GITHUB_TOKEN` s `contents: write` permissiami
