import json
import os
import sys
from typing import List, Dict

SETTINGS_FILE = 'ajustes_junta.json'
BACKLOG_FILE = 'backlog_codex.json'
DEFAULT_PRIMARY = 'groq'
DEFAULT_SECONDARY = 'ollama'
DEFAULT_MAX_RETRIES = 2
DEFAULT_RETRY_DELAY_S = 60
DEFAULT_AUTO_REVIEW_CONFIDENCE = 0.85

def init_settings():
    settings = {
        "primary": DEFAULT_PRIMARY,
        "secondary": DEFAULT_SECONDARY,
        "max_retries": DEFAULT_MAX_RETRIES,
        "retry_delay_s": DEFAULT_RETRY_DELAY_S,
        "auto_review_confidence": DEFAULT_AUTO_REVIEW_CONFIDENCE,
    }
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

def load_backlog() -> List[Dict]:
    if not os.path.exists(BACKLOG_FILE):
        return []
    with open(BACKLOG_FILE, 'r') as f:
        return json.load(f)

def save_backlog(tasks: List[Dict]):
    with open(BACKLOG_FILE, 'w') as f:
        json.dump(tasks, f)

def enqueue(task, primary_ratio=0.8):
    if task['attempts'] >= load_backlog()["max_retries"]:
        return False  # No se puede reintentar más
    route = DEFAULT_PRIMARY if task['type'] == 'generation' and task['status'] == 'failed' else DEFAULT_SECONDARY
    task['route'] = route
    save_backlog(load_backlog())
    return True

def should_retry(task) -> bool:
    if task['attempts'] >= load_backlog()["max_retries"]:
        return False  # No se puede reintentar más
    return True

def run_retry(limit=10):
    backlog = load_backlog()
    for i, task in enumerate(backlog):
        if task['type'] == 'generation' and task['status'] == 'failed':
            if should_retry(task) and i < limit:
                task['attempts'] += 1
                enqueue(task)
    save_backlog(backlog)

def run_autoreview(limit=10):
    backlog = load_backlog()
    for i, task in enumerate(backlog):
        if task['type'] == 'review' and task['confidence'] < DEFAULT_AUTO_REVIEW_CONFIDENCE and i < limit:
            task['status'] = 'reviewed'
            enqueue(task)
    save_backlog(backlog)

def main():
    if "--init" in sys.argv or "-i" in sys.argv:
        init_settings()
    else:
        run_retry()
        run_autoreview()

if __name__ == "__main__":
    main()
    
    # Casos de prueba
    if "--test" in sys.argv:
        init_settings()
        with open("ajustes_junta.json") as f:
            cfg = json.load(f)
        assert cfg["primary"] == DEFAULT_PRIMARY
        assert cfg["secondary"] == DEFAULT_SECONDARY
        assert cfg["max_retries"] == DEFAULT_MAX_RETRIES
        assert cfg["retry_delay_s"] == DEFAULT_RETRY_DELAY_S
        assert cfg["auto_review_confidence"] == DEFAULT_AUTO_REVIEW_CONFIDENCE
        
        print("PRUEBAS OK")
