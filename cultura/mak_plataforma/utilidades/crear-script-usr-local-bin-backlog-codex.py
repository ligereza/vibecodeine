import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path

LOG_DIR = "/var/log/mak"
LOG_FILE = f"{LOG_DIR}/backlog_codex_run_now.log"
COMMAND = ["/usr/local/bin/backlog_codex", "--take", "4", "--parallel", "2", "--provider", "groq"]

def build_command() -> list[str]:
    return COMMAND[:]

def run_command(cmd: list[str], log_path: str, timeout: float | None = None) -> int:
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(log_path, 'a') as logfile:
        try:
            result = subprocess.run(cmd, stdout=logfile, stderr=subprocess.STDOUT, timeout=timeout)
            return result.returncode
        except subprocess.TimeoutExpired as e:
            with open(log_path, 'a') as logfile:
                logfile.write(f"TimeoutExpired: {e}\n")
            return 124
        except FileNotFoundError as e:
            with open(log_path, 'a') as logfile:
                logfile.write(f"FileNotFoundError: {e}\n")
            return 127

def self_tests(tmpdir: str | None = None) -> None:
    if tmpdir is None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pass
    else:
        os.makedirs(tmpdir, exist_ok=True)
    
    # Caso 1: ejecución exitosa
    script_path = Path(tmpdir) / "test_script.py"
    script_path.write_text("print('STDOUT_OK')\nprint('STDERR_WARN', file=sys.stderr)\nsys.exit(0)")
    os.chmod(str(script_path), 0o700)
    
    exit_code = run_command([str(script_path)], LOG_FILE)
    assert exit_code == 0, "Caso 1: Salida esperada es 0"
    with open(LOG_FILE, 'r') as logfile:
        logs = logfile.readlines()
        assert any("STDOUT_OK" in log for log in logs), "Salida estándar no encontrada en el log"
        assert any("STDERR_WARN" in log for log in logs), "Salida de error estándar no encontrada en el log"
    
    # Caso 2: ejecución con código de error distinto de cero
    script_path = Path(tmpdir) / "test_script.py"
    script_path.write_text('import sys\nprint("FAILED", file=sys.stderr)\nsys.exit(42)')
    os.chmod(str(script_path), 0o700)
    
    exit_code = run_command([str(script_path)], LOG_FILE)
    assert exit_code == 42, "Caso 2: Salida esperada es 42"
    with open(LOG_FILE, 'r') as logfile:
        logs = logfile.readlines()
        assert any("FAILED" in log for log in logs), "Salida de error encontrada en el log"
    
    # Caso 3: ejecutable ausente
    nonexistent_path = Path(tmpdir) / "nonexistent_script.py"
    exit_code = run_command([str(nonexistent_path)], LOG_FILE)
    assert exit_code == 127, "Caso 3: Salida esperada es 127"
    with open(LOG_FILE, 'r') as logfile:
        logs = logfile.readlines()
        assert any("FileNotFoundError" in str(log) for log in logs), "Error de archivo no encontrado en el log"

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ejecuta comandos y maneja logs.")
    parser.add_argument('--dry-run', action='store_true', help="Imprime el comando y sale 0 (no ejecuta).")
    parser.add_argument('--verify', action='store_true', help="Ejecuta self_tests() y sale 0 si pasan.")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print(" ".join(build_command()))
        sys.exit(0)
    elif args.verify:
        self_tests()
        print("PRUEBAS OK")
        sys.exit(0)
    else:
        exit_code = run_command(build_command(), LOG_FILE)
        sys.exit(exit_code)
