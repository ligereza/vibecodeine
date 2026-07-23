import json
from typing import List, Dict
import random
import argparse
import os

CONFIGURATION_PATH = "ajustes_junta.json"
BACKLOG_PATH = "backlog_codex.json"

def update_settings(path: str = CONFIGURATION_PATH) -> None:
    settings = {
        "primary": "groq",
        "secondary": "ollama",
        "max_retries": 2,
        "retry_delay_s": 60,
        "auto_review_confidence": 0.85
    }
    
    with open(path, 'r+') as file:
        data = json.load(file)
        data["codex"] = settings
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()
        
def cron_codex_retry(backlog_path: str = BACKLOG_PATH) -> None:
    with open(backlog_path, 'r+') as file:
        backlog = json.load(file)["tasks"]
        for task in random.sample(backlog, min(10, len(backlog))):
            if task['status'] in ['failed', 'pending_generate'] and task['retries_left'] > 0:
                task['retries_left'] -= 1
                task['provider'] = random.choices(['primary', 'secondary'], weights=[0.8, 0.2], k=1)[0]
                task['status'] = "queued" if task['retries_left'] > 0 else "exhausted"
        file.seek(0)
        json.dump({'tasks': backlog}, file, indent=4)
        file.truncate()
        
def cron_codex_autoreview(backlog_path: str = BACKLOG_PATH) -> None:
    with open(backlog_path, 'r+') as file:
        backlog = json.load(file)["tasks"]
        for task in random.sample(backlog, min(10, len([task for task in backlog if task['status'] == "revisar" and "low_complexity" in task['tags']]))):
            confidence = mejora_libre()  # función determinista que devuelve un valor entre 0 y 1
            if confidence >= json.load(open(CONFIGURATION_PATH))["auto_review_confidence"]:
                task['status'] = "listo"
            else:
                backlog["manual_review_needed"].append(task)
        file.seek(0)
        json.dump({'tasks': backlog}, file, indent=4)
        file.truncate()
        
def main():
    update_settings()
    cron_codex_retry()
    cron_codex_autoreview()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Codex Maintenance')
    parser.add_argument('--settings', default=CONFIGURATION_PATH, help=f"Path to settings file (default: {CONFIGURATION_PATH})")
    parser.add_argument('--backlog', default=BACKLOG_PATH, help=f"Path to backlog file (default: {BACKLOG_PATH})")
    args = parser.parse_args()
    
    update_settings(args.settings)
    cron_codex_retry(args.backlog)
    cron_codex_autoreview(args.backlog)
