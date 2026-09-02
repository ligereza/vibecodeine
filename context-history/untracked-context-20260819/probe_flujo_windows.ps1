[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$Root = "",

    [Parameter(Mandatory = $false)]
    [string]$OutDir = "",

    [Parameter(Mandatory = $false)]
    [switch]$SkipPipFreeze
)

# Read-only diagnostic probe for the real Windows FLUJO environment.
# It does not install packages, start a server, call HTTP routes, or modify
# the source tree. It writes only a small report directory.

$ErrorActionPreference = "Stop"
$StartedAt = Get-Date

function Write-Utf8Text {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text
    )

    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Text, $encoding)
}

if ([string]::IsNullOrWhiteSpace($Root)) {
    # The normal location is <repo>\tools\probe_flujo_windows.ps1.
    $Root = Split-Path -Parent $PSScriptRoot
}

$Root = (Resolve-Path -LiteralPath $Root).Path

if ([string]::IsNullOrWhiteSpace($OutDir)) {
    $OutDir = Join-Path $Root "flujo_windows_probe"
}

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

$srcRoot = Join-Path $Root "src"
$oldPythonPath = $env:PYTHONPATH
$pythonPathParts = @()
if (Test-Path -LiteralPath $srcRoot) {
    $pythonPathParts += $srcRoot
}
$pythonPathParts += $Root
if (-not [string]::IsNullOrWhiteSpace($oldPythonPath)) {
    $pythonPathParts += $oldPythonPath
}
$env:PYTHONPATH = $pythonPathParts -join [System.IO.Path]::PathSeparator

$results = New-Object System.Collections.Generic.List[object]

function Invoke-Captured {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $false)][string[]]$ArgumentList = @()
    )

    $outputLines = @()
    $exitCode = 0

    try {
        Push-Location -LiteralPath $Root
        $outputLines = @(& $FilePath @ArgumentList 2>&1 | ForEach-Object {
            $_.ToString()
        })
        if ($null -ne $LASTEXITCODE) {
            $exitCode = [int]$LASTEXITCODE
        }
    }
    catch {
        $outputLines = @($_.Exception.Message)
        $exitCode = -1
    }
    finally {
        Pop-Location
    }

    $result = [PSCustomObject]@{
        name      = $Name
        exit_code = $exitCode
        ok        = ($exitCode -eq 0)
        output    = ($outputLines -join [Environment]::NewLine).Trim()
    }
    $results.Add($result)
    return $result
}

$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
$pyOnPath = Get-Command python -ErrorAction SilentlyContinue

if ($null -ne $pyLauncher) {
    $PythonCommand = $pyLauncher.Path
    $PythonPrefix = @("-3")
}
elseif ($null -ne $pyOnPath) {
    $PythonCommand = $pyOnPath.Path
    $PythonPrefix = @()
}
else {
    throw "No Python launcher was found. Try again with Python or the py launcher installed."
}

function Invoke-PythonCaptured {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $false)][string[]]$Arguments = @()
    )

    $combinedArguments = @($PythonPrefix) + @($Arguments)
    return Invoke-Captured -Name $Name -FilePath $PythonCommand -ArgumentList $combinedArguments
}

try {
    $pythonInfo = Invoke-PythonCaptured -Name "python interpreter" -Arguments @(
        "-c",
        "import sys; print(sys.executable); print(sys.version.replace(chr(10), ' '))"
    )

    $pipInfo = Invoke-PythonCaptured -Name "python -m pip --version" -Arguments @(
        "-m", "pip", "--version"
    )

    $versionInfo = Invoke-PythonCaptured -Name "python -m flujo --version" -Arguments @(
        "-m", "flujo", "--version"
    )

    $helpInfo = Invoke-PythonCaptured -Name "python -m flujo --help" -Arguments @(
        "-m", "flujo", "--help"
    )

    $flowCommand = Get-Command flujo -ErrorAction SilentlyContinue
    if ($null -ne $flowCommand -and -not [string]::IsNullOrWhiteSpace($flowCommand.Path)) {
        $flowHelp = Invoke-Captured -Name "flujo --help" -FilePath $flowCommand.Path -ArgumentList @(
            "--help"
        )
    }
    else {
        $results.Add([PSCustomObject]@{
            name = "flujo --help"
            exit_code = -2
            ok = $false
            output = "The flujo executable was not found on PATH; the module probe was still attempted."
        })
    }

    $anchorModules = @(
        "flujo",
        "flujo.cli",
        "flujo.web.hub",
        "flujo.serve.server"
    )

    foreach ($moduleName in $anchorModules) {
        $moduleCode = "import importlib; importlib.import_module('$moduleName'); print('IMPORT_OK:$moduleName')"
        Invoke-PythonCaptured -Name ("import " + $moduleName) -Arguments @(
            "-c", $moduleCode
        ) | Out-Null
    }

    if (-not $SkipPipFreeze) {
        $freezeInfo = Invoke-PythonCaptured -Name "python -m pip freeze" -Arguments @(
            "-m", "pip", "freeze"
        )
        Write-Utf8Text -Path (Join-Path $OutDir "pip-freeze.txt") -Text $freezeInfo.output
    }

    # Bounded AST scan. It follows the migration surface, not the whole disk.
    $scanRoots = New-Object System.Collections.Generic.List[string]
    $candidateRoots = @(
        (Join-Path $Root "src\flujo"),
        (Join-Path $Root "cultura"),
        (Join-Path $Root "iskvw"),
        (Join-Path $Root "projects\cultura"),
        (Join-Path $Root "tools\mak"),
        (Join-Path $Root "tools\mak_ops")
    )
    foreach ($candidateRoot in $candidateRoots) {
        if (Test-Path -LiteralPath $candidateRoot) {
            $scanRoots.Add((Resolve-Path -LiteralPath $candidateRoot).Path)
        }
    }

    $scanCode = @'
import ast
import importlib.metadata as metadata
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
roots = [Path(value).resolve() for value in sys.argv[2:]]
skip_parts = {".git", ".venv", "venv", "node_modules", "__pycache__"}

try:
    stdlib = set(sys.stdlib_module_names)
except AttributeError:
    stdlib = set(sys.builtin_module_names)

def top_name(value):
    return value.split(".", 1)[0]

local_tops = set()
for base in [root / "src", root, root / "cultura", root / "iskvw", root / "projects", root / "tools"]:
    if not base.is_dir():
        continue
    for child in base.iterdir():
        if child.name.startswith("."):
            continue
        if child.is_dir() or child.suffix == ".py":
            local_tops.add(child.stem if child.suffix == ".py" else child.name)

files = []
for scan_root in roots:
    if scan_root.is_file() and scan_root.suffix == ".py":
        files.append(scan_root)
        continue
    if not scan_root.is_dir():
        continue
    for path in scan_root.rglob("*.py"):
        if any(part in skip_parts for part in path.parts):
            continue
        files.append(path)

files = sorted(set(files))
imports = {}
per_file = []
syntax_errors = []
dynamic_sites = []

for path in files:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        syntax_errors.append({"file": str(path), "line": exc.lineno, "error": str(exc)})
        continue
    except Exception as exc:
        syntax_errors.append({"file": str(path), "line": None, "error": str(exc)})
        continue

    file_imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                file_imports.add(top_name(alias.name))
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            file_imports.add(top_name(node.module))
        elif isinstance(node, ast.Call):
            function_name = ""
            if isinstance(node.func, ast.Name):
                function_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                function_name = node.func.attr
            if function_name in {"__import__", "import_module", "find_spec"}:
                dynamic_sites.append({"file": str(path), "line": node.lineno, "call": function_name})

    relative_file = str(path)
    try:
        relative_file = str(path.relative_to(root))
    except ValueError:
        pass
    per_file.append({"file": relative_file, "imports": sorted(file_imports)})
    for name in file_imports:
        imports.setdefault(name, set()).add(relative_file)

try:
    package_map = metadata.packages_distributions()
except Exception:
    package_map = {}

external = {}
unresolved = []
classified = {}
for name, files_using in sorted(imports.items()):
    if name in stdlib:
        classified[name] = "stdlib"
        continue
    if name in local_tops:
        classified[name] = "local"
        continue
    distributions = sorted(set(package_map.get(name, [])))
    if distributions:
        classified[name] = "external"
        for distribution in distributions:
            try:
                version = metadata.version(distribution)
            except Exception:
                version = None
            record = external.setdefault(distribution, {"distribution": distribution, "version": version, "imports": set()})
            record["imports"].add(name)
    else:
        classified[name] = "unresolved"
        unresolved.append({"import": name, "files": sorted(files_using)})

external_list = []
for record in sorted(external.values(), key=lambda value: value["distribution"].lower()):
    external_list.append({
        "distribution": record["distribution"],
        "version": record["version"],
        "imports": sorted(record["imports"]),
    })

print(json.dumps({
    "root": str(root),
    "files_scanned": len(files),
    "scan_roots": [str(value) for value in roots],
    "imports": sorted(imports),
    "classified_imports": classified,
    "external_distributions": external_list,
    "unresolved_external_imports": unresolved,
    "dynamic_import_sites": dynamic_sites,
    "syntax_or_read_errors": syntax_errors,
    "per_file": per_file,
}, indent=2, ensure_ascii=True))
'@

    $scanArguments = @("-c", $scanCode, $Root) + @($scanRoots)
    $scanInfo = Invoke-PythonCaptured -Name "AST import scan (bounded migration surface)" -Arguments $scanArguments
    Write-Utf8Text -Path (Join-Path $OutDir "imports.json") -Text $scanInfo.output

    $scanData = $null
    try {
        $scanData = $scanInfo.output | ConvertFrom-Json
    }
    catch {
        $scanData = [PSCustomObject]@{
            external_distributions = @()
            unresolved_external_imports = @()
        }
    }

    $requirementsLines = New-Object System.Collections.Generic.List[string]
    $requirementsLines.Add("# Provisional candidates from the real Windows FLUJO tree.")
    $requirementsLines.Add("# Evidence only: do not replace an existing requirements file with this list.")
    $requirementsLines.Add("# Generated by probe_flujo_windows.ps1 on $($StartedAt.ToString('o')).")
    $requirementsLines.Add("")

    foreach ($distribution in @($scanData.external_distributions)) {
        $packageName = [string]$distribution.distribution
        $packageVersion = [string]$distribution.version
        $importNames = (@($distribution.imports) -join ", ")
        if ([string]::IsNullOrWhiteSpace($packageVersion) -or $packageVersion -eq "null") {
            $requirementsLines.Add("$packageName  # imports: $importNames; version unresolved")
        }
        else {
            $requirementsLines.Add("$packageName==$packageVersion  # imports: $importNames")
        }
    }

    $requirementsLines.Add("")
    $requirementsLines.Add("# Unresolved imports require manual review:")
    foreach ($unresolved in @($scanData.unresolved_external_imports)) {
        $requirementsLines.Add("# $($unresolved.import)  <- $(@($unresolved.files) -join ', ')")
    }
    Write-Utf8Text -Path (Join-Path $OutDir "requirements-candidates.txt") -Text ($requirementsLines -join [Environment]::NewLine)

    $environment = [ordered]@{
        generated_at = (Get-Date).ToString("o")
        started_at = $StartedAt.ToString("o")
        host = $env:COMPUTERNAME
        os_caption = (Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue).Caption
        root = $Root
        output_directory = $OutDir
        python_command = $PythonCommand
        python_prefix = $PythonPrefix
        python_path_for_probe = $env:PYTHONPATH
        python_interpreter_output = $pythonInfo.output
        pip_output = $pipInfo.output
        module_version_exit_code = $versionInfo.exit_code
        module_help_exit_code = $helpInfo.exit_code
        pip_freeze_collected = (-not $SkipPipFreeze)
        safety = @(
            "No package installation",
            "No source deletion or rewrite",
            "No flujo serve start",
            "No HTTP/API route calls",
            "No credentials or environment-variable dump"
        )
    }

    $environmentJson = ConvertTo-Json -InputObject $environment -Depth 12
    Write-Utf8Text -Path (Join-Path $OutDir "environment.json") -Text $environmentJson
    $resultsArray = $results.ToArray()
    $commandResultsJson = ConvertTo-Json -InputObject $resultsArray -Depth 12
    Write-Utf8Text -Path (Join-Path $OutDir "command-results.json") -Text $commandResultsJson

    $readme = @"
FLUJO WINDOWS PROBE

This directory is diagnostic evidence from the real Windows FLUJO environment.
It does not represent a final requirements file.

Files:
  environment.json          Python, host and probe metadata.
  command-results.json       Safe command/import results and exit codes.
  imports.json               Bounded AST import scan for the migration surface.
  requirements-candidates.txt
                             Provisional external package candidates.
  pip-freeze.txt             Installed packages, if collection was not skipped.

The probe did not install packages, start a server, call HTTP routes, or modify
the source tree. Review imports.json and command-results.json together.
"@
    Write-Utf8Text -Path (Join-Path $OutDir "README.txt") -Text $readme.Trim()

    Write-Host "FLUJO Windows probe complete."
    Write-Host ("Root: " + $Root)
    Write-Host ("Reports: " + $OutDir)
    Write-Host "Send the report files, not the source tree."
}
finally {
    if ($null -eq $oldPythonPath) {
        Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    }
    else {
        $env:PYTHONPATH = $oldPythonPath
    }
}
