#!/usr/bin/env python3
"""Resource gate and conservative cleanup for detached recursive scans."""
import argparse
import os
import shutil
import signal
import time

LOAD_MAX = 6.0
MEM_MIN_MB = 2048
DISCO_MIN_GB = 5.0
STALE_SCAN_MINUTES = 15
SCAN_EXECUTABLES = frozenset(("grep", "rg", "find"))
SCAN_ROOTS = ("/home/mak", "/etc/systemd")
SHELL_NAMES = frozenset(("bash", "dash", "sh", "zsh"))


def recursos_ok():
    """Return ``(ok, reason)`` for a potentially heavy job."""
    load1 = os.getloadavg()[0]
    if load1 > LOAD_MAX:
        return False, "load %.1f > %.1f" % (load1, LOAD_MAX)
    mem = -1
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    mem = int(line.split()[1]) // 1024
                    break
    except OSError:
        pass
    if 0 <= mem < MEM_MIN_MB:
        return False, "available memory %dMB < %dMB" % (mem, MEM_MIN_MB)
    libre_gb = shutil.disk_usage("/").free / 1e9
    if libre_gb < DISCO_MIN_GB:
        return False, "free disk %.1fGB < %.1fGB" % (libre_gb, DISCO_MIN_GB)
    return True, "ok"


def esperar_recursos(max_espera=300, paso=10):
    """Wait until resources are available or the deadline expires."""
    inicio = time.time()
    while True:
        ok, motivo = recursos_ok()
        if ok:
            return True
        if time.time() - inicio > max_espera:
            print("STATUS: resource wait expired (%s)" % motivo, flush=True)
            return False
        print("STATUS: waiting for resources (%s)" % motivo, flush=True)
        time.sleep(paso)


def _command_name(command):
    """Extract an executable basename without invoking a shell."""
    parts = (command or "").split(None, 1)
    if not parts:
        return ""
    first = parts[0]
    return os.path.basename(first)


def is_stale_scan(command, age_seconds, parent_pid, parent_command):
    """Return True only for an old recursive scan detached from its owner.

    This deliberately does not classify Python workers, Ollama, systemd, or
    any managed MAK service.  A scan is eligible only when it targets a MAK or
    systemd tree, has run for the age threshold, and its parent is PID 1 or a
    shell holding a ``-c`` command.  The latter is the failure mode produced
    by a remote inspection shell that outlives its SSH session.
    """
    text = (command or "").lower()
    executable = _command_name(text)
    if executable not in SCAN_EXECUTABLES:
        return False
    if age_seconds < STALE_SCAN_MINUTES * 60:
        return False
    if not any(root in text for root in SCAN_ROOTS):
        return False
    if executable == "grep" and not any(
        flag in text for flag in (" -r", " -R", " --recursive")
    ):
        return False
    parent = (parent_command or "").lower()
    parent_name = _command_name(parent)
    detached_shell = parent_name in SHELL_NAMES and "-c" in parent
    return parent_pid == 1 or detached_shell


def _boot_time():
    """Read Linux boot time; return None on non-Linux hosts."""
    try:
        with open("/proc/stat", encoding="ascii") as stream:
            for line in stream:
                if line.startswith("btime "):
                    return float(line.split()[1])
    except (OSError, ValueError, IndexError):
        return None
    return None


def _process_table():
    """Read the process table from /proc without spawning ps or grep."""
    boot = _boot_time()
    if boot is None:
        return {}
    ticks = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
    processes = {}
    try:
        entries = os.listdir("/proc")
    except OSError:
        return processes
    for entry in entries:
        if not entry.isdigit():
            continue
        pid = int(entry)
        try:
            with open("/proc/%d/cmdline" % pid, "rb") as stream:
                command = stream.read().replace(b"\0", b" ").decode(
                    "utf-8", "replace"
                ).strip()
            with open("/proc/%d/stat" % pid, encoding="ascii") as stream:
                stat = stream.read()
            close = stat.rfind(")")
            fields = stat[close + 2 :].split()
            parent_pid = int(fields[1])
            start_ticks = int(fields[19])
            started = boot + start_ticks / ticks
            processes[pid] = {
                "pid": pid,
                "ppid": parent_pid,
                "command": command,
                "started": started,
            }
        except (OSError, ValueError, IndexError, ZeroDivisionError):
            continue
    return processes


def stale_scan_candidates(now=None):
    """Return old detached scan records, without changing process state."""
    now = time.time() if now is None else now
    processes = _process_table()
    candidates = []
    for process in processes.values():
        parent = processes.get(process["ppid"], {})
        age = max(0.0, now - process["started"])
        if is_stale_scan(
            process["command"], age, process["ppid"], parent.get("command", "")
        ):
            candidates.append({
                "pid": process["pid"],
                "ppid": process["ppid"],
                "age_seconds": int(age),
                "command": process["command"],
            })
    return sorted(candidates, key=lambda item: item["pid"])


def reap_stale_scans(dry_run=False):
    """Terminate only candidates returned by the narrow stale-scan filter."""
    candidates = stale_scan_candidates()
    for item in candidates:
        action = "would terminate" if dry_run else "terminate"
        if not dry_run:
            try:
                os.kill(item["pid"], signal.SIGTERM)
            except ProcessLookupError:
                action = "already gone"
            except PermissionError:
                action = "permission denied"
        print(
            "PROCESS_GUARD: %s pid=%d age=%dm ppid=%d cmd=%s"
            % (
                action,
                item["pid"],
                item["age_seconds"] // 60,
                item["ppid"],
                item["command"][:240],
            ),
            flush=True,
        )
    if not candidates:
        print("PROCESS_GUARD: no stale detached scans", flush=True)
    return len(candidates)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reap-stale-scans",
        action="store_true",
        help="terminate old detached recursive scans only",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="report candidates without signals"
    )
    args = parser.parse_args()
    if args.reap_stale_scans:
        raise SystemExit(0 if reap_stale_scans(args.dry_run) >= 0 else 1)
    ok, reason = recursos_ok()
    print("resources_ok=%s (%s)" % (ok, reason))
    raise SystemExit(0 if ok else 1)
