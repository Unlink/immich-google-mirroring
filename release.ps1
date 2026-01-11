# Complete release automation script for Windows
# Usage: .\release.ps1 <version> [-DryRun]

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    
    [switch]$DryRun
)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Helper functions
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Blue
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Yellow
}

function Validate-Version {
    param([string]$VersionStr)
    if ($VersionStr -notmatch '^\d+\.\d+\.\d+$') {
        Write-Error "Invalid version format: $VersionStr"
        Write-Host "Expected format: X.Y.Z (e.g., 1.0.1)"
        return $false
    }
    return $true
}

function Check-GitStatus {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Error "git not found"
        return $false
    }
    
    $status = git status --porcelain 2>$null
    if ($status) {
        Write-Warning "Working directory has uncommitted changes:"
        git status
        return $false
    }
    
    return $true
}

function Edit-Changelog {
    $ChangelogPath = Join-Path $ProjectRoot "CHANGELOG.md"
    Write-Info "Opening CHANGELOG.md in default editor..."
    
    try {
        Invoke-Item $ChangelogPath
        Write-Host ""
        Write-Host "Please edit the file and press Enter when done:"
        Read-Host
        return $true
    }
    catch {
        Write-Warning "Could not open editor. Please manually edit CHANGELOG.md"
        return $true
    }
}

function Update-Version {
    param(
        [string]$VersionStr,
        [bool]$DryRunMode
    )
    
    if ($DryRunMode) {
        Write-Info "[DRY-RUN] Would update version to: $VersionStr"
        return $true
    }
    
    Write-Info "Updating version to $VersionStr..."
    & ".\version.ps1" set $VersionStr
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Version updated"
        return $true
    }
    return $false
}

function Commit-Changes {
    param(
        [string]$VersionStr,
        [bool]$DryRunMode
    )
    
    if ($DryRunMode) {
        Write-Info "[DRY-RUN] Would commit with message: chore(release): v$VersionStr"
        return $true
    }
    
    Write-Info "Committing changes..."
    git add app/__version__.py, CHANGELOG.md, docker-compose.yml
    git commit -m "chore(release): v$VersionStr"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Changes committed"
        return $true
    }
    return $false
}

function Create-GitTag {
    param(
        [string]$VersionStr,
        [bool]$DryRunMode
    )
    
    if ($DryRunMode) {
        Write-Info "[DRY-RUN] Would create tag: v$VersionStr"
        Write-Info "[DRY-RUN] Would push: git push origin main && git push origin v$VersionStr"
        return $true
    }
    
    Write-Info "Creating git tag..."
    git tag -a "v$VersionStr" -m "Release version $VersionStr"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Git tag created: v$VersionStr"
        return $true
    }
    return $false
}

function Push-Changes {
    param(
        [string]$VersionStr,
        [bool]$DryRunMode
    )
    
    if ($DryRunMode) {
        Write-Info "[DRY-RUN] Would push changes and tags"
        return $true
    }
    
    Write-Info "Pushing changes and tags to GitHub..."
    Write-Warning "This will trigger GitHub Actions workflows"
    
    git push origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to push main branch"
        return $false
    }
    
    git push origin "v$VersionStr"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to push tag"
        return $false
    }
    
    Write-Success "Pushed to GitHub"
    return $true
}

function Show-Summary {
    param(
        [string]$VersionStr,
        [bool]$DryRunMode
    )
    
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Blue
    
    if ($DryRunMode) {
        Write-Host "[DRY-RUN] Release Summary for v$VersionStr" -ForegroundColor Yellow
    }
    else {
        Write-Host "Release v$VersionStr completed!" -ForegroundColor Green
    }
    
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host ""
    Write-Host "What happened:"
    Write-Host "  1. Updated version to $VersionStr"
    Write-Host "  2. Updated CHANGELOG.md with release notes"
    Write-Host "  3. Committed changes"
    Write-Host "  4. Created git tag v$VersionStr"
    Write-Host "  5. Pushed to GitHub"
    Write-Host ""
    Write-Host "GitHub Actions will automatically:"
    Write-Host "  1. Build Docker image for linux/amd64 and linux/arm64"
    Write-Host "  2. Push image to ghcr.io/<owner>/immich-google-sync:$VersionStr"
    Write-Host "  3. Push image to ghcr.io/<owner>/immich-google-sync:latest"
    Write-Host "  4. Create GitHub Release with changelog"
    Write-Host ""
    Write-Host "Check progress at:"
    Write-Host "  - Actions: https://github.com/<owner>/immich-google-mirroring/actions"
    Write-Host "  - Releases: https://github.com/<owner>/immich-google-mirroring/releases"
    Write-Host "  - Packages: https://ghcr.io/<owner>/immich-google-sync"
    Write-Host ""
}

# Main script logic
if (-not (Validate-Version $Version)) {
    exit 1
}

if ($DryRun) {
    Write-Warning "Running in DRY-RUN mode (no changes will be made)"
    Write-Host ""
}

if (-not $DryRun) {
    if (-not (Check-GitStatus)) {
        Write-Error "Please commit all changes before releasing"
        exit 1
    }
}

Write-Info "Starting release process for v$Version..."
Write-Host ""

# Step 1: Edit changelog
if (-not $DryRun) {
    Write-Info "Step 1: Update CHANGELOG.md"
    if (-not (Edit-Changelog)) {
        Write-Error "Changelog edit cancelled"
        exit 1
    }
    Write-Success "Changelog updated"
    Write-Host ""
}

# Step 2: Update version
Write-Info "Step 2: Update version"
if (-not (Update-Version $Version $DryRun)) {
    Write-Error "Failed to update version"
    exit 1
}
Write-Host ""

# Step 3: Commit changes
Write-Info "Step 3: Commit changes"
if (-not (Commit-Changes $Version $DryRun)) {
    Write-Error "Failed to commit changes"
    exit 1
}
Write-Host ""

# Step 4: Create git tag
Write-Info "Step 4: Create git tag"
if (-not (Create-GitTag $Version $DryRun)) {
    Write-Error "Failed to create git tag"
    exit 1
}
Write-Host ""

# Step 5: Push changes
Write-Info "Step 5: Push to GitHub"
if (-not (Push-Changes $Version $DryRun)) {
    Write-Error "Failed to push changes"
    exit 1
}
Write-Host ""

# Summary
Show-Summary $Version $DryRun
