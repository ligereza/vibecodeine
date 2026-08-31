[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$Root = "",

    [Parameter(Mandatory = $false)]
    [string]$OutFile = ""
)

# Read-only NTFS metadata probe for the FLUJO migration anchors.
# It writes one JSON report and does not alter the source tree.

$ErrorActionPreference = "Stop"

function Write-Utf8Text {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text
    )

    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Text, $encoding)
}

if ([string]::IsNullOrWhiteSpace($Root)) {
    # Normal location: <repo>\tools\probe_flujo_windows_metadata.ps1.
    $Root = Split-Path -Parent $PSScriptRoot
}

$Root = (Resolve-Path -LiteralPath $Root).Path

if ([string]::IsNullOrWhiteSpace($OutFile)) {
    $reportDirectory = Join-Path $Root "flujo_windows_probe"
    New-Item -ItemType Directory -Path $reportDirectory -Force | Out-Null
    $OutFile = Join-Path $reportDirectory "anchors-metadata.json"
}
else {
    $outParent = Split-Path -Parent $OutFile
    if (-not [string]::IsNullOrWhiteSpace($outParent)) {
        New-Item -ItemType Directory -Path $outParent -Force | Out-Null
    }
}

$targets = @(
    "src\flujo\cli.py",
    "src\flujo\web\hub.py",
    "src\flujo\serve\server.py",
    "context\flujo_hub.html",
    "abrir_hub.bat",
    "src\flujo",
    "src\flujo\web",
    "src\flujo\serve",
    "context",
    "cultura",
    "cultura\mak_plataforma",
    "cultura\mak_research",
    "tools\mak",
    "tools\mak_ops",
    "iskvw"
)

$records = New-Object System.Collections.Generic.List[object]

foreach ($relativePath in $targets) {
    $fullPath = Join-Path $Root $relativePath
    $normalizedPath = $relativePath.Replace("\", "/")

    if (-not (Test-Path -LiteralPath $fullPath)) {
        $records.Add([PSCustomObject]@{
            path = $normalizedPath
            kind = "missing"
            status = "missing"
        })
        continue
    }

    try {
        $item = Get-Item -LiteralPath $fullPath -Force
        $isFile = -not $item.PSIsContainer
        $sha256 = $null
        $hashError = $null
        $childCount = $null

        if ($isFile) {
            try {
                $sha256 = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
            }
            catch {
                $hashError = $_.Exception.Message
            }
        }
        else {
            $childCount = @(Get-ChildItem -LiteralPath $item.FullName -Force -ErrorAction SilentlyContinue).Count
        }

        $records.Add([PSCustomObject]@{
            path = $normalizedPath
            full_path = $item.FullName
            kind = $(if ($isFile) { "file" } else { "directory" })
            status = "ok"
            size_bytes = $(if ($isFile) { [int64]$item.Length } else { $null })
            direct_child_count = $childCount
            created_local = $item.CreationTime.ToString("o")
            created_utc = $item.CreationTimeUtc.ToString("o")
            modified_local = $item.LastWriteTime.ToString("o")
            modified_utc = $item.LastWriteTimeUtc.ToString("o")
            accessed_utc = $item.LastAccessTimeUtc.ToString("o")
            attributes = [string]$item.Attributes
            sha256 = $sha256
            hash_error = $hashError
        })
    }
    catch {
        $records.Add([PSCustomObject]@{
            path = $normalizedPath
            kind = "error"
            status = "error"
            error = $_.Exception.Message
        })
    }
}

$report = [ordered]@{
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    root = $Root
    purpose = "Triangulate physical chronology and content identity for the WIN to MAK FLUJO migration anchors."
    caution = "Creation time can reflect copying; use it with modified time, SHA256, routes, consumers and Git history."
    records = $records.ToArray()
}

$json = ConvertTo-Json -InputObject $report -Depth 8
Write-Utf8Text -Path $OutFile -Text $json

Write-Host "Metadata probe complete."
Write-Host ("Report: " + $OutFile)
Write-Host ("Records: " + $records.Count)
