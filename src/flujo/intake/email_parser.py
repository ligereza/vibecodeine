from __future__ import annotations
import re
from typing import List, Dict
from pathlib import Path

def extract_instagram_links(text: str) -> List[str]:
    pattern = r'https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/[A-Za-z0-9_-]+/?'
    return re.findall(pattern, text)

def detect_private_account(text: str) -> bool:
    keywords = ['privado', 'private', 'no se puede descargar', 'requiere login', 'shadowban']
    return any(kw in text.lower() for kw in keywords)

def detect_video_in_carousel(text: str) -> bool:
    keywords = ['video', 'reel', 'mp4', 'primera imagen es video']
    return any(kw in text.lower() for kw in keywords)

def detect_project_type(text: str) -> str:
    text_lower = text.lower()
    if any(kw in text_lower for kw in ['etiqueta', 'label', 'suplemento']):
        return 'etiqueta'
    if any(kw in text_lower for kw in ['brief', 'briefing']):
        return 'brief'
    if any(kw in text_lower for kw in ['pendon', 'pendón', 'banner']):
        return 'pendon'
    return 'flyer'

def extract_sections(text: str) -> Dict[str, str]:
    sections = {}
    patterns = {
        'titulo': r'(?:título|titulo|title)[:\s]+(.+)',
        'fecha': r'(?:fecha|date)[:\s]+(.+)',
        'evento': r'(?:evento|event)[:\s]+(.+)',
        'productora': r'(?:productora|producer)[:\s]+(.+)',
        'lugar': r'(?:lugar|venue)[:\s]+(.+)',
        'medidas': r'(?:medidas|medida|size)[:\s]+(.+)',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            sections[key] = match.group(1).strip()
    return sections

def generate_warnings(result: Dict) -> List[str]:
    warnings = []
    if result.get('is_private'):
        warnings.append('⚠️ CUENTA PRIVADA')
    if result.get('has_video'):
        warnings.append('⚠️ VIDEO EN CARRUSEL')
    if result.get('link_count', 0) == 0:
        warnings.append('⚠️ SIN LINKS DE INSTAGRAM')
    return warnings

def parse_email_content(text: str) -> Dict:
    links = extract_instagram_links(text)
    result = {
        'project_type': detect_project_type(text),
        'instagram_links': links,
        'link_count': len(links),
        'is_private': detect_private_account(text),
        'has_video': detect_video_in_carousel(text),
        'sections': extract_sections(text),
        'warnings': []
    }
    result['warnings'] = generate_warnings(result)
    return result

def parse_email_file(filepath: Path) -> Dict:
    try:
        return parse_email_content(filepath.read_text(encoding='utf-8'))
    except Exception as e:
        return {'error': str(e)}
