#!/usr/bin/env python3
"""Diagnostico read-only del mirror imginn usado por flyer_auto."""
from __future__ import annotations
import argparse, html, re, urllib.error, urllib.request
from datetime import datetime
from pathlib import Path
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
def get(url, referer=None):
    h={'User-Agent':UA};
    if referer: h['Referer']=referer
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=20) as r:
            return r.status,r.geturl(),r.read(300000),''
    except urllib.error.HTTPError as e: return e.code,e.geturl(),e.read(500).decode('utf8','replace').encode(),str(e)
    except Exception as e: return 0,'',b'',str(e)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--url',required=True); ap.add_argument('--output',default='mirror_diagnosis.md'); a=ap.parse_args()
    m=re.search(r'/(?:p|reel)/([^/?#]+)',a.url); shortcode=m.group(1) if m else ''
    lines=['# Mirror diagnosis',f'Generated: `{datetime.now().astimezone().isoformat(timespec="seconds")}`',f'Shortcode: `{shortcode or "INVALID"}`']
    if not shortcode: Path(a.output).write_text('\n'.join(lines)+'\n'); return 2
    status,final,page,err=get(f'https://imginn.com/p/{shortcode}/')
    lines += [f'Page status: `{status}`',f'Page final URL: `{final}`',f'Page error: `{err or "none"}`']
    text=page.decode('utf8','replace')
    urls=re.findall(r'(?:data-src|src)="(https://[^\"]+(?:imginn|scontent|cdninstagram)[^\"]+)"',text)
    urls=[html.unescape(u) for u in urls if '.jpg' in u or '.webp' in u]
    candidate=urls[0] if urls else ''
    lines += [f'Image candidates: `{len(urls)}`']
    if candidate:
        s2,f2,_,e2=get(candidate,'https://imginn.com/')
        lines += [f'Image status: `{s2}`',f'Image final URL: `{f2}`',f'Image error: `{e2 or "none"}`']
    Path(a.output).write_text('\n'.join(lines)+'\n',encoding='utf8'); print(f'Written: {Path(a.output).resolve()}')
    return 0
if __name__=='__main__': raise SystemExit(main())
