param(
    [switch]$Json,
    [string]$Branch
)

function Get-RepoRoot {
    if ((git rev-parse --show-toplevel 2>$null) -ne $null) {
        git rev-parse --show-toplevel
    } else {
        # Fallback to script location for non-git repos
        $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
        (Resolve-Path "$scriptDir/../../..").Path
    }
}

function Get-CurrentBranch {
    param([string]$ProvidedBranch)

    if (-not [string]::IsNullOrEmpty($ProvidedBranch)) {
        return $ProvidedBranch
    }
    $specifyFeature = $env:SPECIFY_FEATURE
    if (-not [string]::IsNullOrEmpty($specifyFeature)) {
        return $specifyFeature
    }

    if ((git rev-parse --abbrev-ref HEAD 2>$null) -ne $null) {
        return git rev-parse --abbrev-ref HEAD
    }

    $repoRoot = Get-RepoRoot
    $specsDir = Join-Path $repoRoot "specs"

    if (Test-Path $specsDir -PathType Container) {
        $latestFeature = ""
        $highest = 0

        Get-ChildItem -Path $specsDir -Directory | ForEach-Object {
            $dirname = $_.Name
            if ($dirname -match '^(\d{3})-') {
                $number = [int]$matches[1]
                if ($number -gt $highest) {
                    $highest = $number
                    $latestFeature = $dirname
                }
            }
        }
        if (-not [string]::IsNullOrEmpty($latestFeature)) {
            return $latestFeature
        }
    }
    return "main" # Final fallback
}

function Test-HasGit {
    return (git rev-parse --show-toplevel 2>$null) -ne $null
}

function Check-FeatureBranch {
    param(
        [string]$Branch,
        [bool]$HasGitRepo
    )

    if (-not $HasGitRepo) {
        Write-Host "[specify] Warning: Git repository not detected; skipped branch validation" -ForegroundColor Yellow
        return $true
    }

    if (-not ($Branch -match '^\d{3}-')) {
        Write-Error "ERROR: Not on a feature branch. Current branch: $Branch"
        Write-Error "Feature branches should be named like: 001-feature-name"
        return $false
    }
    return $true
}

function Find-FeatureDirByPrefix {
    param(
        [string]$RepoRoot,
        [string]$BranchName
    )

    $specsDir = Join-Path $RepoRoot "specs"
    if ($BranchName -match '^(\d{3})-') {
        $prefix = $matches[1]
        $foundDirs = @(Get-ChildItem -Path $specsDir -Directory -Filter "$prefix-*" | Select-Object -ExpandProperty Name) # Explicitly capture as array

        if ($foundDirs.Count -eq 0) {
            return (Join-Path $specsDir $BranchName) # Explicitly return
        } elseif ($foundDirs.Count -eq 1) {
            return (Join-Path $specsDir $foundDirs[0]) # Explicitly return
        } else {
            Write-Error "ERROR: Multiple spec directories found with prefix '$prefix': $($foundDirs -join ', ')"
            Write-Error "Please ensure only one spec directory exists per numeric prefix."
            return (Join-Path $specsDir $BranchName) # Return something to avoid breaking the script
        }
    } else {
        return (Join-Path $specsDir $BranchName) # Explicitly return
    }
}

# --- Main Logic ---
$repoRoot = Get-RepoRoot
$currentBranch = Get-CurrentBranch -ProvidedBranch $Branch
$hasGit = Test-HasGit

if (-not (Check-FeatureBranch -Branch $currentBranch -HasGitRepo $hasGit)) {
    exit 1
}

$featureDir = Find-FeatureDirByPrefix -RepoRoot $repoRoot -BranchName $currentBranch
$featureSpec = Join-Path $featureDir "spec.md"
$implPlan = Join-Path $featureDir "plan.md"
$tasks = Join-Path $featureDir "tasks.md"
$research = Join-Path $featureDir "research.md"
$dataModel = Join-Path $featureDir "data-model.md"
$quickstart = Join-Path $featureDir "quickstart.md"
$contractsDir = Join-Path $featureDir "contracts"

# Ensure the feature directory exists
if (-not (Test-Path $featureDir -PathType Container)) {
    New-Item -Path $featureDir -ItemType Directory | Out-Null
}

# Copy plan template if it exists
$templatePath = Join-Path $repoRoot ".specify/templates/plan-template.md"
if (Test-Path $templatePath -PathType Leaf) {
    Copy-Item -Path $templatePath -Destination $implPlan -Force | Out-Null
    Write-Host "Copied plan template to $implPlan"
} else {
    Write-Host "Warning: Plan template not found at $templatePath" -ForegroundColor Yellow
    New-Item -Path $implPlan -ItemType File | Out-Null # Create a basic plan file if template doesn't exist
}

# Output results
if ($Json) {
    $result = @{
        FEATURE_SPEC = $featureSpec
        IMPL_PLAN = $implPlan
        SPECS_DIR = $featureDir
        BRANCH = $currentBranch
        HAS_GIT = $hasGit
    }
    ConvertTo-Json -InputObject $result -Compress
} else {
    Write-Host "FEATURE_SPEC: $featureSpec"
    Write-Host "IMPL_PLAN: $implPlan"
    Write-Host "SPECS_DIR: $featureDir"
    Write-Host "BRANCH: $currentBranch"
    Write-Host "HAS_GIT: $hasGit"
}
