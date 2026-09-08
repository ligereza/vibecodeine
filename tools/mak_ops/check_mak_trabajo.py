#!/usr/bin/env python3
"""Lectura acotada del ultimo estado/tick de trabajo.py en MAK."""
from __future__ import annotations
import argparse, datetime as dt, subprocess
from pathlib import Path

CMD = r'''echo '@@ STATE @@'; cat /home/mak/plataforma/.trabajo_state.json 2>/dev/null || echo MISSING
echo '@@ LOG @@'; tail -12 /home/mak/plataforma/logs/trabajo.log 2>/dev/null || echo MISSING
echo '@@ RESEARCH_EVENTS @@'; tail -3 /home/mak/research/eventos.jsonl 2>/dev/null || echo MISSING
echo '@@ CODEX_EVENTS @@'; tail -3 /home/mak/codex/eventos.jsonl 2>/dev/null || echo MISSING'''

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--output',default='mak_trabajo_check.md'); a=ap.parse_args()
    try:
        r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','mak@192.168.50.2',CMD],capture_output=True,text=True,timeout=30)
        out,err=r.stdout,r.stderr
    except Exception as e: out,err='',str(e); r=type('R',(),{'returncode':99})()
    md=f"# MAK trabajo check\n\nGenerated: `{dt.datetime.now().astimezone().isoformat(timespec='seconds')}`\nSSH exit: `{r.returncode}`\n\n```text\n{out.strip()}\n```\n\nSTDERR:\n```text\n{err.strip() or '(none)'}\n```\n"
    Path(a.output).write_text(md,encoding='utf-8'); print(f'Written: {Path(a.output).resolve()}')
    # Fixed 2026-08-31: this used to `return 0` unconditionally, so a caller
    # checking the exit code of this "check" tool saw success even when the
    # SSH leg was completely dead (e.g. exit 255, "Connection timed out") --
    # the same family of bug as `flujo doctor` reporting `airdrop pendiente:
    # OK` for a directory that never existed. The markdown always named the
    # SSH exit code, but the process exit code did not, so a script piping
    # `check_mak_trabajo.py && something` could not tell measurement failed.
    return 0 if r.returncode == 0 else 1
if __name__=='__main__': raise SystemExit(main())
