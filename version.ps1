# Version management script for Windows
# Usage: .\version.ps1 [command] [options]

param(
    [string]$Command = "show",
    [string]$Argument = ""
)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VersionFile = Join-Path $ProjectRoot "app" "__version__.py"
$DockerComposeFile = Join-Path $ProjectRoot "docker-compose.yml"

# Helper functions
function Get-CurrentVersion {
    $content = Get-Content $VersionFile | Select-String '__version__ = "([^"]+)"'
    $version = $content.Matches[0].Groups[1].Value
    return $version
}

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
    param([string]$Version)
    if ($Version -notmatch '^\d+\.\d+\.\d+$') {
        Write-Error "Invalid version format: $Version"
        Write-Host "Expected format: X.Y.Z (e.g., 1.0.1)"
        return $false
    }
    return $true
}

function Show-Version {
    $version = Get-CurrentVersion
    Write-Host "Immich Google Photos Mirroring - Version " -NoNewline
    Write-Host $version -ForegroundColor Green
}

function Update-VersionFile {
    param([string]$NewVersion)
    
    $major, $minor, $patch = $NewVersion.Split('.')
    $content = Get-Content $VersionFile -Raw
    
    # Update __version__
    $content = $content -replace '__version__ = "[^"]*"', "__version__ = `"$NewVersion`""
    
    # Update __version_info__
    $content = $content -replace '__version_info__ = \([^)]*\)', "__version_info__ = ($major, $minor, $patch)"
    
    Set-Content -Path $VersionFile -Value $content -Encoding UTF8
    Write-Success "Updated $VersionFile"
}

function Update-DockerCompose {
    param([string]$NewVersion)
    
    $content = Get-Content $DockerComposeFile -Raw
    $content = $content -replace 'VERSION: \d+\.\d+\.\d+', "VERSION: $NewVersion"
    Set-Content -Path $DockerComposeFile -Value $content -Encoding UTF8
    
    Write-Success "Updated $DockerComposeFile"
}

function Invoke-SetVersion {
    param([string]$NewVersion)
    
    if (-not (Validate-Version $NewVersion)) {
        return
    }
    
    $current = Get-CurrentVersion
    if ($current -eq $NewVersion) {
        Write-Warning "Version is already $NewVersion"
        return
    }
    
    Write-Info "Updating version from $current to $NewVersion"
    Update-VersionFile $NewVersion
    Update-DockerCompose $NewVersion
    Write-Success "Version updated to $NewVersion"
}

function Invoke-BumpVersion {
    param([string]$BumpType)
    
    $current = Get-CurrentVersion
    $parts = $current.Split('.')
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    $patch = [int]$parts[2]
    
    switch ($BumpType.ToLower()) {
        "major" {
            $major++
            $minor = 0
            $patch = 0
        }
        "minor" {
            $minor++
            $patch = 0
        }
        "patch" {
            $patch++
        }
        default {
            Write-Error "Unknown bump type: $BumpType"
            Write-Host "Use: major, minor, or patch"
            return
        }
    }
    
    $newVersion = "$major.$minor.$patch"
    Invoke-SetVersion $newVersion
}

function Show-Help {
    Write-Host "Usage: .\version.ps1 [command] [options]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  show              Show current version"
    Write-Host "  bump <type>       Bump version (major|minor|patch)"
    Write-Host "  set <version>     Set specific version (X.Y.Z)"
    Write-Host "  release <version> Create a release"
    Write-Host "  help              Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\version.ps1 show"
    Write-Host "  .\version.ps1 bump patch"
    Write-Host "  .\version.ps1 set 1.1.0"
    Write-Host "  .\version.ps1 release 1.0.1"
}

# Main logic
switch ($Command.ToLower()) {
    "show" {
        Show-Version
    }
    "bump" {
        if ([string]::IsNullOrEmpty($Argument)) {
            Write-Error "Bump type not specified"
            Show-Help
            exit 1
        }
        Invoke-BumpVersion $Argument
    }
    "set" {
        if ([string]::IsNullOrEmpty($Argument)) {
            Write-Error "Version not specified"
            Show-Help
            exit 1
        }
        Invoke-SetVersion $Argument
    }
    "release" {
        if ([string]::IsNullOrEmpty($Argument)) {
            Write-Error "Version not specified"
            Show-Help
            exit 1
        }
        Invoke-SetVersion $Argument
        Write-Info "Please manually create git tag: git tag -a v$Argument -m 'Release version $Argument'"
    }
    "help" {
        Show-Help
    }
    default {
        Write-Error "Unknown command: $Command"
        Show-Help
        exit 1
    }
}
