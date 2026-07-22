#!/usr/bin/env python3
"""Prueba read-only fuentes publicas y extrae candidatos de imagen Instagram."""
from __future__ import annotations
import argparse, html, re, urllib.error, urllib.request
from datetime import datetime
from pathlib import Path
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
def fetch(url,limit=250000):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA,'Accept-Language':'en-US,en;q=0.9'}),timeout=20) as r:return r.status,r.geturl(),r.read(limit).decode('utf8','replace'),'none'
 except urllib.error.HTTPError as e:return e.code,e.geturl(),e.read(500).decode('utf8','replace'),str(e)
 except Exception as e:return 0,'','',str(e)
def candidates(body):
 text=html.unescape(body).replace('\\/','/')
 found=[]
 for pat in (r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',r'https://scontent[^"\\\s]+'):
  found += re.findall(pat,text,re.I)
 return list(dict.fromkeys(x.replace('\\u0026','&') for x in found if 'http' in x))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--url',required=True);ap.add_argument('--output',default='instagram_sources.md');a=ap.parse_args()
 m=re.search(r'/(?:p|reel)/([^/?#]+)',a.url);code=m.group(1) if m else ''
 sources=[('instagram_post',f'https://www.instagram.com/p/{code}/'),('instagram_embed',f'https://www.instagram.com/p/{code}/embed/captioned/'),('imginn',f'https://imginn.com/p/{code}/')]
 lines=['# Instagram source probe',f'Generated: `{datetime.now().astimezone().isoformat(timespec="seconds")}`',f'Shortcode: `{code}`','']
 for name,url in sources:
  status,final,body,error=fetch(url); urls=candidates(body)
  lines += [f'## {name}',f'URL: `{url}`',f'Status: `{status}`',f'Final: `{final}`',f'Candidates: `{len(urls)}`',f'First candidate: `{urls[0] if urls else "none"}`',f'Error: `{error}`','']
 Path(a.output).write_text('\n'.join(lines),encoding='utf8');print(f'Written: {Path(a.output).resolve()}')
if __name__=='__main__':main()
