# GitHub Actions & Release Automation - Summary

Úspešne som nakonfiguroval kompletnú automatizáciu GitHub Actions a release management pre váš projekt.

## 🎉 Čo bolo implementované

### 1. GitHub Actions Workflows

#### **release.yml** (Nový)
- ✅ Automaticky spustí sa keď pushnete tag `v*`
- ✅ Extrahuje verziu a changelog z `CHANGELOG.md`
- ✅ Vytvorí GitHub Release s popis
- ✅ Build Docker image a pushne na registry

#### **docker-publish.yml** (Vylepšený)
- ✅ Vyčítava verziu z `app/__version__.py`
- ✅ Build pre `linux/amd64` a `linux/arm64`
- ✅ Viacero image tagov (latest, verzia, sha, atď.)
- ✅ Integrovaná verzia z aplikácie

#### **docker-test.yml** (Existujúci)
- ✅ Testuje Docker image na PR
- ✅ Spustí health check

### 2. Release Skripty

#### **release.ps1** (Windows)
```powershell
# Vytvorí kompletný release
.\release.ps1 1.0.1

# Dry-run test
.\release.ps1 1.0.1 -DryRun
```

#### **release.sh** (Linux/Mac)
```bash
# Vytvorí kompletný release
./release.sh 1.0.1

# Dry-run test
./release.sh 1.0.1 --dry-run
```

**Čo robí:**
1. Otvorí `CHANGELOG.md` na editáciu
2. Aktualizuje verziu v kóde
3. Commitne zmeny
4. Vytvorí git tag
5. Pushne na GitHub
6. Spustí GitHub Actions workflows

### 3. Dokumentácia

#### **docs/RELEASE.md**
- Kompletný guide na vytvorenie releases
- Krok za krokom inštrukcie
- Príklady a troubleshooting

#### **docs/CI-CD.md**
- Popis všetkých workflows
- Tagy pre Docker images
- Performance notes
- Troubleshooting

#### **docs/VERSIONING.md**
- Semantic Versioning format
- Ako aktualizovať verziu
- API endpoint `/api/version`

#### **docs/GITHUB-CONFIG.md**
- GitHub repository setup
- Permissions configuration
- Secrets setup
- Release checklist

### 4. Vylepšená Dokumentácia

- ✅ README.md - Added versioning a release sekcie
- ✅ CHANGELOG.md - Updated s novými changes

## 🚀 Ako sa to používa

### Vytvorenie novej verzie

**Metóda 1: One-command release (Recommended)**

```powershell
# Windows
.\release.ps1 1.0.1

# Linux/Mac
./release.sh 1.0.1
```

**Metóda 2: Step-by-step**

```bash
# 1. Aktualizovať verziu
./version.ps1 set 1.0.1

# 2. Editovať CHANGELOG.md

# 3. Commit
git add app/__version__.py CHANGELOG.md docker-compose.yml
git commit -m "chore(release): v1.0.1"

# 4. Tag a push
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin main
git push origin v1.0.1
```

### GitHub Actions Flow

```
git push origin v1.0.1
        ↓
release.yml spustí
  - Vytvorí GitHub Release
  - Spustí docker-publish.yml
        ↓
docker-publish.yml spustí
  - Build Docker image (linux/amd64, linux/arm64)
  - Push na ghcr.io/owner/immich-google-sync:1.0.1
  - Push na ghcr.io/owner/immich-google-sync:latest
        ↓
✅ Release completed!
```

## 📦 Docker Image Tags

Po release sú dostupné:

```bash
# Konkrétna verzia
docker pull ghcr.io/<owner>/immich-google-sync:1.0.1

# Latest
docker pull ghcr.io/<owner>/immich-google-sync:latest

# Major.minor
docker pull ghcr.io/<owner>/immich-google-sync:1.0

# Major
docker pull ghcr.io/<owner>/immich-google-sync:1
```

## ✅ Setup Checklist

### Na GitHube:

- [ ] Prejdite na Settings → Actions → General
- [ ] Nastavte "Read and write permissions"
- [ ] Prejdite na Settings → Branches
- [ ] (Opt) Přidajte branch protection na `main`

### Lokálne:

- [ ] Máte `version.ps1` alebo `version.sh`
- [ ] Máte `release.ps1` alebo `release.sh`
- [ ] Máte `.github/workflows/release.yml`
- [ ] Máte `.github/workflows/docker-publish.yml`
- [ ] CHANGELOG.md je v správnom formáte

## 📋 File Structure

```
.github/workflows/
  ├── docker-test.yml      (existujúci)
  ├── docker-publish.yml   (vylepšený)
  └── release.yml          (nový)

docs/
  ├── RELEASE.md           (nový)
  ├── CI-CD.md             (nový)
  ├── GITHUB-CONFIG.md     (nový)
  └── VERSIONING.md        (nový)

./
  ├── release.ps1          (nový - Windows)
  ├── release.sh           (nový - Linux/Mac)
  ├── version.ps1          (existujúci)
  └── version.sh           (existujúci)

app/
  ├── __version__.py       (existujúci - centrálna verzia)
  └── version_cli.py       (existujúci)
```

## 🔍 Monitoring

### Počas release-u:

1. Prejdite na https://github.com/Unlink/immich-google-mirroring/actions
2. Vidíte workflow progress v real-time
3. Skontrolujte release.yml a docker-publish.yml logs

### Po dokončení:

1. Prejdite na Releases tab
2. Vidíte novú release s changelogom
3. Docker image je dostupný na ghcr.io

## 🆘 Troubleshooting

### Workflow failed

**Príčiny:**
- Git tag nebol pushnený
- Permissions nie sú správne
- Workflow má syntax error

**Riešenie:**
- Skontrolujte workflow logy na Actions tab
- Skontrolujte format tagu (`v1.0.0`)
- Skontrolujte Settings → Actions permissions

### Docker image push failed

**Príčina:**
- GITHUB_TOKEN permissions

**Riešenie:**
- Settings → Actions → General → "Read and write permissions"

## 📚 Dokumentácia

Podrobná dokumentácia:
- [Release Guide](docs/RELEASE.md)
- [CI/CD Pipelines](docs/CI-CD.md)
- [GitHub Configuration](docs/GITHUB-CONFIG.md)
- [Version Management](docs/VERSIONING.md)

## ✨ Features

✅ Semantic Versioning (MAJOR.MINOR.PATCH)
✅ Automatické GitHub Releases
✅ Docker multi-platform builds (amd64, arm64)
✅ Automatické image tagy
✅ Changelog integration
✅ Git tag automation
✅ Dry-run testing
✅ One-command releases
✅ Detailná dokumentácia

## 🎯 Next Steps

1. **Skontrolujte GitHub Settings**
   - Settings → Actions → General
   - Nastavte "Read and write permissions"

2. **Test dry-run release**
   ```powershell
   .\release.ps1 1.1.0 -DryRun
   ```

3. **Vytvorte prvú release**
   ```powershell
   .\release.ps1 1.1.0
   ```

4. **Sledujte GitHub Actions**
   - Prejdite na Actions tab
   - Vidíte progress workflows

5. **Skontrolujte Docker image**
   ```bash
   docker pull ghcr.io/<owner>/immich-google-sync:1.1.0
   ```

---

**Gratulujeme! Máte plne automatizovanú release pipeline! 🚀**
