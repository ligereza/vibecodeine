#!/usr/bin/env python3
"""Crea un Issue fixture y prueba una vez el puente Issue -> render -> comentario."""
from __future__ import annotations
import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path

ROOT=Path.cwd(); REPO="ligereza/vibecodeine"
def run(args, **kw): return subprocess.run(args,capture_output=True,text=True,encoding="utf-8",errors="replace",**kw)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--url',required=True); ap.add_argument('--output',default='issue_render_e2e.md'); a=ap.parse_args()
    stamp=dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    body=f"<!-- E2E_FIXTURE: no es pedido real -->\n\nURL de prueba:\n{a.url}\n"
    create=run(['gh','issue','create','--repo',REPO,'--title',f'[E2E] issue-render {stamp}','--label','instagram','--body',body])
    lines=['# E2E issue-render',f'Generated: `{dt.datetime.now().astimezone().isoformat(timespec="seconds")}`','']
    if create.returncode:
        lines += ['## CREATE FAIL','```text',create.stderr.strip(),'```']; Path(a.output).write_text('\n'.join(lines),encoding='utf-8'); return 1
    url=create.stdout.strip(); number=url.rstrip('/').split('/')[-1]
    lines += [f'Issue: {url}','', '## BRIDGE OUTPUT','```text']
    bridge=run([sys.executable,str(ROOT/'tools'/'bridge_issue_render.py'),'--once','--issue',number],cwd=ROOT)
    lines += [bridge.stdout.strip(),bridge.stderr.strip(),'```','', '## ISSUE STATE','```text']
    view=run(['gh','issue','view',number,'--repo',REPO,'--json','state,url,comments'])
    lines += [view.stdout.strip() or view.stderr.strip(),'```']
    Path(a.output).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Written: {Path(a.output).resolve()} issue=#{number}')
    return bridge.returncode
if __name__=='__main__': raise SystemExit(main())
