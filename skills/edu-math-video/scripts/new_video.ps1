param(
    [Parameter(Mandatory=$true)][string]$Workspace,
    [Parameter(Mandatory=$true)][string]$Name
)
$ErrorActionPreference = 'Stop'
if ($Name -notmatch '^[A-Za-z0-9_-]+$') { throw 'Name must contain only ASCII letters, digits, - or _' }
$workspacePath = (Resolve-Path -LiteralPath $Workspace).Path
$skillPath = Split-Path -Parent $PSScriptRoot
$destination = Join-Path $workspacePath $Name
if (Test-Path -LiteralPath $destination) { throw "Already exists: $destination. Never overwrite a finished video." }
New-Item -ItemType Directory -Path $destination | Out-Null
Get-ChildItem -LiteralPath (Join-Path $skillPath 'template') | Where-Object {
    $_.Name -notin @('build', 'node_modules', '__pycache__')
} | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $destination -Recurse }
New-Item -ItemType Directory -Path (Join-Path $destination 'build') | Out-Null
foreach ($fileName in @('pron.py', 'pron.json')) {
    $target = Join-Path $workspacePath $fileName
    if (-not (Test-Path -LiteralPath $target)) {
        Copy-Item -LiteralPath (Join-Path $skillPath "shared\$fileName") -Destination $target
    }
}
Write-Output "Created $destination"
Write-Output 'Dependencies at the workspace root: npm install playwright@1.49 ffmpeg-static'
Write-Output "Next: python `"$skillPath\scripts\setup_check.py`" `"$destination`""
