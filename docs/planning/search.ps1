$ErrorActionPreference = 'Stop'

$repoRoot = (& git -C $PSScriptRoot rev-parse --show-toplevel)
if ($LASTEXITCODE -ne 0) {
    throw 'Unable to locate the Git repository root.'
}

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$outputPath = Join-Path $PSScriptRoot "search_$timestamp.txt"
$results = New-Object 'System.Collections.Generic.List[string]'

function Add-GitGrepResults {
    param(
        [System.Collections.Generic.List[string]]$Results,
        [string]$Pattern,
        [string[]]$Pathspec
    )

    $grepOutput = & git grep --break -n -E $Pattern -- $Pathspec
    $exitCode = $LASTEXITCODE
    if ($exitCode -gt 1) {
        throw "git grep failed with exit code $exitCode for pattern: $Pattern"
    }

    foreach ($line in $grepOutput) {
        [void]$Results.Add([string]$line)
    }
}

Push-Location $repoRoot
try {
    $results.Add('--- Python imports and generated path ---')
    Add-GitGrepResults $results 'from src import|from src\.generated_files|GENERATED_PATH' @('*.py')

    $results.Add('')
    $results.Add('--- Multi-line and plain src imports ---')
    Add-GitGrepResults $results 'from src import \(|^\s*import src\b|from src\.[a-z_.]+ import \(' @('*.py')

    $results.Add('')
    $results.Add('--- String-based mock patch targets ---')
    Add-GitGrepResults $results 'patch(\.object|\.dict)?\(' @('tests/*.py')

    $results.Add('')
    $results.Add('--- Generated resources and paths ---')
    Add-GitGrepResults $results 'generated_files|icon_files|licenses|RESOURCES_PATH' @(
        '.',
        ':(exclude)docs/planning',
        ':(exclude)docs/command_lines',
        ':(exclude)docs/scripts'
    )
}
finally {
    Pop-Location
}

Set-Content -Path $outputPath -Value $results.ToArray() -Encoding utf8
Write-Output "Wrote $outputPath"
