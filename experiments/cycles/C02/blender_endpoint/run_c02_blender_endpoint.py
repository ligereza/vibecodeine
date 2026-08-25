#!/usr/bin/env python3
"""LUNA A / C02: bounded, read-only native Blender observation.

The only input this adapter opens is the frozen RAYU.blend path.  It delegates
the Blender invocation to the existing ``tools/blender_scene_probe.py`` and
never invokes a render or save operation.  The temporary probe JSON is made
inside this endpoint and removed after parsing; the delivered JSON is
sanitised evidence, not a copy of the source document.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping


ENDPOINT_DIR = Path(__file__).resolve().parent
FLUJO_ROOT = Path("/home/mak/flujo")
PROBE = FLUJO_ROOT / "tools/blender_scene_probe.py"
SOURCE = Path("/home/mak/curatoria_inbox/ARICA/RAYU.blend")
EXPECTED_SHA256 = "acafc1db0088016139921b1ea2c9d7a5310247658117fa7021662e13e907ce86"
CONTRACT = "luna-a-c02-blender-native-observation-v1"
EXTRACTOR_VERSION = "luna-a-c02-blender-endpoint-v1"
UPSTREAM_CONTRACT = "mak-blender-scene-snapshot-run-v1"
TIMEOUT_SECONDS = 120


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _tail(value: str | bytes | None, limit: int = 4000) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    return value[-limit:]


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


def _sanitise_native_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Remove absolute locators while retaining observed native state."""
    result = copy.deepcopy(dict(snapshot))
    provenance = result.get("provenance")
    if isinstance(provenance, dict):
        provenance.pop("source_path", None)
        provenance["source_locator"] = "ARICA/RAYU.blend"
        provenance["sanitisation"] = {
            "absolute_paths": "removed",
            "dependency_path_values": "retained_as_declared_by_blender",
            "filesystem_status_fields": "retained",
        }
    native = result.get("native")
    if isinstance(native, dict):
        for dependency in native.get("dependencies", []):
            if isinstance(dependency, dict):
                dependency.pop("absolute_path", None)
    return result


def _blender_executable() -> Path:
    explicit = os.environ.get("BLENDER_EXE")
    candidates = [Path(explicit).expanduser()] if explicit else []
    candidates.append(Path("/home/mak/blender/blender"))
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
    found = shutil_which("blender")
    if found:
        return Path(found).resolve()
    raise FileNotFoundError("blender_executable_not_found")


def shutil_which(name: str) -> str | None:
    # Kept local so the runner has no dependency beyond the standard library.
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def _probe_command(blender: Path, temporary_output: Path) -> list[str]:
    return [
        sys.executable,
        str(PROBE),
        "--snapshot",
        "--input",
        str(SOURCE),
        "--output",
        str(temporary_output),
        "--timeout",
        str(TIMEOUT_SECONDS),
    ]


def _effective_blender_command(blender: Path) -> str:
    return shlex.join([
        str(blender),
        "--background",
        "--factory-startup",
        "--disable-autoexec",
        str(SOURCE),
        "--python-expr",
        "<SNAPSHOT_EXPRESSION from tools/blender_scene_probe.py>",
    ])


def observe() -> dict[str, Any]:
    """Observe the frozen source, returning evidence or a blocking result."""
    evidence: dict[str, Any] = {
        "contract": CONTRACT,
        "extractor": {
            "id": EXTRACTOR_VERSION,
            "upstream_probe": str(PROBE),
            "upstream_contract": UPSTREAM_CONTRACT,
            "method": "existing_probe_snapshot_api_via_cli",
            "factory_startup": True,
            "disable_autoexec": True,
            "renders": False,
            "saves": False,
        },
        "source": {
            "locator": "ARICA/RAYU.blend",
            "path": str(SOURCE),
            "expected_sha256": EXPECTED_SHA256,
        },
        "status": "blocked",
        "observation": None,
        "probe": {},
        "integrity": {},
    }
    if not SOURCE.is_file():
        evidence["status"] = "blocked_source_not_file"
        evidence["probe"] = {"alternative": "provide the frozen source file at the declared path"}
        return evidence

    before = sha256(SOURCE)
    evidence["integrity"]["sha256_before"] = before
    evidence["integrity"]["expected_match_before"] = before == EXPECTED_SHA256
    if before != EXPECTED_SHA256:
        evidence["status"] = "blocked_source_digest_mismatch"
        evidence["integrity"]["sha256_after"] = sha256(SOURCE)
        evidence["integrity"]["unchanged"] = (
            evidence["integrity"]["sha256_after"] == before
        )
        evidence["probe"] = {
            "alternative": "stop and re-freeze the declared source; no snapshot was fabricated",
        }
        return evidence

    try:
        blender = _blender_executable()
    except (FileNotFoundError, OSError) as exc:
        after = sha256(SOURCE)
        evidence["status"] = "blocked_blender_unavailable"
        evidence["integrity"].update({
            "sha256_after": after,
            "unchanged": after == before,
        })
        evidence["probe"] = {
            "command": "blender --background --factory-startup --disable-autoexec RAYU.blend --python-expr <snapshot>",
            "exit_code": None,
            "error": str(exc),
            "alternative": "install or expose a Blender executable through BLENDER_EXE; do not fabricate a snapshot",
        }
        return evidence

    evidence["extractor"]["blender"] = str(blender)
    evidence["extractor"]["blender_version"] = _blender_version(blender)
    evidence["probe"]["effective_blender_command"] = _effective_blender_command(blender)

    temporary_output: Path | None = None
    completed: subprocess.CompletedProcess[str] | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", dir=ENDPOINT_DIR,
            delete=False,
        ) as handle:
            temporary_output = Path(handle.name)
        command = _probe_command(blender, temporary_output)
        env = os.environ.copy()
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = os.pathsep.join(
            item for item in (str(FLUJO_ROOT / "src"), existing_pythonpath) if item
        )
        completed = subprocess.run(
            command,
            cwd=str(FLUJO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=TIMEOUT_SECONDS + 30,
            check=False,
        )
        evidence["probe"].update({
            "wrapper_command": shlex.join(command),
            "exit_code": completed.returncode,
            "stdout_tail": _tail(completed.stdout),
            "stderr_tail": _tail(completed.stderr),
        })
        payload = json.loads(temporary_output.read_text(encoding="utf-8"))
    except subprocess.TimeoutExpired as exc:
        evidence["probe"].update({
            "wrapper_command": shlex.join(command) if "command" in locals() else None,
            "exit_code": None,
            "error": f"timeout_seconds:{TIMEOUT_SECONDS + 30}",
            "stdout_tail": _tail(exc.stdout),
            "stderr_tail": _tail(exc.stderr),
        })
        payload = None
    except (OSError, json.JSONDecodeError) as exc:
        evidence["probe"].update({
            "wrapper_command": shlex.join(command) if "command" in locals() else None,
            "exit_code": completed.returncode if completed else None,
            "error": str(exc)[:400],
        })
        payload = None
    finally:
        if temporary_output and temporary_output.exists():
            temporary_output.unlink()

    after = sha256(SOURCE)
    evidence["integrity"].update({
        "sha256_after": after,
        "unchanged": after == before,
        "expected_match_after": after == EXPECTED_SHA256,
    })
    if after != before:
        evidence["status"] = "blocked_source_changed_during_observation"
        evidence["probe"]["alternative"] = "discard this observation and repeat against a re-frozen source"
        return evidence
    if completed is None or completed.returncode != 0 or not isinstance(payload, dict):
        evidence["status"] = "blocked_probe_failure"
        evidence["probe"]["alternative"] = "inspect the recorded command and stderr; do not fabricate a snapshot"
        return evidence
    rows = payload.get("files") or []
    row = rows[0] if rows else {}
    if row.get("status") != "ok" or not isinstance(row.get("snapshot"), dict):
        evidence["status"] = "blocked_probe_decoder_limit"
        evidence["probe"]["row"] = row
        evidence["probe"]["alternative"] = "use a compatible Blender/probe version or document the decoder limit"
        return evidence

    evidence["status"] = "observed"
    evidence["observation"] = _sanitise_native_snapshot(row["snapshot"])
    return evidence


def _blender_version(blender: Path) -> str:
    try:
        result = subprocess.run(
            [str(blender), "--version"], capture_output=True, text=True,
            errors="replace", timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"unavailable:{exc}"
    first = next((line.strip() for line in result.stdout.splitlines() if line.strip()), "")
    return first[:200] or f"exit:{result.returncode}"


def _native(evidence: Mapping[str, Any]) -> Mapping[str, Any]:
    observation = evidence.get("observation")
    return observation.get("native", {}) if isinstance(observation, Mapping) else {}


def render_report(evidence: Mapping[str, Any]) -> str:
    native = _native(evidence)
    scenes = native.get("scenes", []) if isinstance(native, Mapping) else []
    dependencies = native.get("dependencies", []) if isinstance(native, Mapping) else []
    lines = [
        "# C02 Blender endpoint — LUNA A",
        "",
        f"- Contrato: `{CONTRACT}`",
        f"- Extractor: `{EXTRACTOR_VERSION}`; upstream `{UPSTREAM_CONTRACT}`",
        f"- Estado: **{evidence.get('status', 'unknown')}**",
        "- Alcance: observación nativa read-only; no render, no save, no copia ni reempaquetado del `.blend`.",
        "",
        "## Contrato de evidencia",
        "",
        "Cada hecho observado debe corresponder al snapshot nativo y a su digest de estado. "
        "El digest del archivo fuente se comprueba antes y después. Las rutas absolutas "
        "se eliminan del JSON entregado; los valores de ruta declarados por Blender se "
        "conservan como texto observado. `negative_is_evidence=false`: la ausencia en este "
        "probe no demuestra ausencia en el archivo.",
        "",
        "## Integridad y ejecución",
        "",
        f"- Fuente: `{evidence.get('source', {}).get('path', SOURCE)}`",
        f"- SHA-256 esperado: `{EXPECTED_SHA256}`",
        f"- SHA-256 antes: `{evidence.get('integrity', {}).get('sha256_before', 'NO OBSERVADO')}`",
        f"- SHA-256 después: `{evidence.get('integrity', {}).get('sha256_after', 'NO OBSERVADO')}`",
        f"- Igualdad antes/después: `{evidence.get('integrity', {}).get('unchanged', 'NO OBSERVADO')}`",
        f"- Exit code del wrapper: `{evidence.get('probe', {}).get('exit_code', 'NO OBSERVADO')}`",
        f"- Blender: `{evidence.get('extractor', {}).get('blender_version', 'NO OBSERVADO')}`",
        "",
        "## Hechos observados",
        "",
    ]
    if evidence.get("status") != "observed":
        lines += [
            "No hay snapshot observado porque la ejecución quedó bloqueada. Se conserva el "
            "comando, exit code y alternativa en la evidencia JSON.",
            "",
        ]
    else:
        lines += [
            f"- El probe devolvió `{len(scenes)}` escena(s).",
        ]
        for scene in scenes:
            render = scene.get("render", {})
            camera = scene.get("camera", {})
            objects = scene.get("objects", [])
            lines += [
                f"- Escena `{scene.get('name')}`: frames `{scene.get('frame_start')}`–`{scene.get('frame_end')}`, "
                f"frame actual `{scene.get('frame_current')}`, objetos `{len(objects)}`, "
                f"colecciones `{scene.get('collections', [])}`, view layer(s) `{scene.get('view_layers', [])}`.",
                f"- Cámara observada: `{camera.get('name')}` (`present={camera.get('present')}`, tipo `{camera.get('type')}`).",
                f"- Settings observados: engine `{render.get('engine')}`, resolución `{render.get('resolution_x')}x{render.get('resolution_y')}` "
                f"al `{render.get('resolution_percentage')}%`, formato `{render.get('file_format')}`, "
                f"`film_transparent={render.get('film_transparent')}`, filepath declarado `{render.get('filepath')}`.",
                f"- Estado nativo reportado por Blender: `dirty={native.get('dirty')}`; esto es estado de la sesión de lectura, "
                "no evidencia de que este endpoint haya guardado o modificado el archivo.",
            ]
            for obj in objects:
                lines.append(
                    f"- Objeto observado `{obj.get('name')}`: tipo `{obj.get('type')}`, "
                    f"materiales `{obj.get('materials', [])}`, datos `{obj.get('data', {})}`."
                )
        lines.append(f"- Dependencias expuestas por el probe: `{len(dependencies)}`.")
        for dependency in dependencies:
            lines.append(
                f"- Dependencia observada: tipo `{dependency.get('kind')}`, "
                f"ruta declarada `{dependency.get('path')}`, exists=`{dependency.get('exists')}`, "
                f"packed=`{dependency.get('packed')}`; su ruta absoluta fue sanitizada del JSON."
            )
    lines += [
        "",
        "## Candidatos (no confirmados)",
        "",
        "- El `render.filepath` observado es un candidato a destino configurado de render; "
        "no prueba que se haya renderizado allí ningún archivo.",
        "- `RAYU.blend` es un candidato a archivo de authoring nativo observado; este endpoint "
        "no declara una obra final, entregable ni autoría.",
        "- Las dos referencias de imagen son candidatas a recursos externos declarados por el "
        "documento. `packed=true` y `exists=false` se mantienen como hechos separados; no se "
        "declara automáticamente una textura faltante.",
        "",
        "## Unknown",
        "",
        "- No se puede determinar desde este snapshot si existe un MP4, si fue generado por "
        "este `.blend`, o si cualquier archivo de la carpeta es un entregable. La mera "
        "coexistencia de un MP4 no sería evidencia de salida del `.blend`.",
        "- No se puede determinar la intención artística, la obra final, la versión aprobada, "
        "la calidad visual ni la relación con un catálogo público.",
        "- El probe no expone una validación semántica completa de materiales, nodos o calidad "
        "visual; `exists=false` de una ruta externa no equivale por sí solo a recurso no disponible "
        "cuando `packed=true`.",
        "",
        "## Reproducción",
        "",
        f"El comando efectivo de Blender está registrado en `evidence.probe.effective_blender_command` "
        f"del JSON. El wrapper usado fue `"+
        f"{_sanitised_command(str(evidence.get('probe', {}).get('wrapper_command', 'NO EJECUTADO')))}"+
        "`.",
        "",
    ]
    if evidence.get("status") != "observed":
        lines += [
            f"Alternativa registrada: {evidence.get('probe', {}).get('alternative', 'documentar el bloqueo y no fabricar snapshot')}.",
            "",
        ]
    return "\n".join(lines)


def write_outputs(evidence: Mapping[str, Any], snapshot_path: Path, report_path: Path) -> None:
    source = copy.deepcopy(dict(evidence.get("source") or {}))
    source.pop("path", None)
    extractor = copy.deepcopy(dict(evidence.get("extractor") or {}))
    if "upstream_probe" in extractor:
        extractor["upstream_probe"] = "tools/blender_scene_probe.py"
    if "blender" in extractor:
        extractor["blender"] = "blender"
    probe = copy.deepcopy(dict(evidence.get("probe") or {}))
    for key in ("effective_blender_command", "wrapper_command"):
        if key in probe:
            probe[key] = _sanitised_command(str(probe[key]))
    output = {
        "schema": CONTRACT,
        "extractor": extractor,
        "source": source,
        "integrity": evidence.get("integrity"),
        "status": evidence.get("status"),
        "probe": probe,
        "snapshot": evidence.get("observation"),
    }
    snapshot_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render_report(evidence), encoding="utf-8")


def _sanitised_command(command: str) -> str:
    """Keep command shape in JSON without absolute host locators."""
    replacements = {
        str(FLUJO_ROOT / "tools/blender_scene_probe.py"): "tools/blender_scene_probe.py",
        str(SOURCE): "ARICA/RAYU.blend",
        str(ENDPOINT_DIR): "blender_endpoint",
        "/home/mak/blender/blender": "blender",
        str(FLUJO_ROOT / ".venv/bin/python"): "python",
        str(Path(sys.executable)): "python",
    }
    for original, replacement in replacements.items():
        command = command.replace(original, replacement)
    return command


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=ENDPOINT_DIR / "snapshot.json")
    parser.add_argument("--report", type=Path, default=ENDPOINT_DIR / "REPORT.md")
    args = parser.parse_args(argv)
    for path in (args.snapshot, args.report):
        if ENDPOINT_DIR not in path.resolve().parents and path.resolve() != ENDPOINT_DIR:
            parser.error(f"output_outside_endpoint:{path}")
    evidence = observe()
    write_outputs(evidence, args.snapshot.resolve(), args.report.resolve())
    print(json.dumps({
        "status": evidence["status"],
        "sha256_before": evidence.get("integrity", {}).get("sha256_before"),
        "sha256_after": evidence.get("integrity", {}).get("sha256_after"),
        "probe_exit_code": evidence.get("probe", {}).get("exit_code"),
        "snapshot": str(args.snapshot.resolve()),
        "report": str(args.report.resolve()),
    }, ensure_ascii=False, sort_keys=True))
    return 0 if evidence["status"] == "observed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
