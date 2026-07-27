import os
import json
from pathlib import Path
import time
import random

def load_backlog(path):
    with open(path, 'r') as file:
        return [json.loads(line) for line in file]

def save_backlog(path, data):
    with open(path, 'w') as file:
        for item in data:
            file.write(json.dumps(item) + '\n')

def route_provider():
    return random.choices(['groq', 'ollama'], weights=[0.8, 0.2], k=1)[0]

def process_task(task):
    task['attempts'] += 1
    if task['status'] == 'failed':
        task['status'] = 'retrying'
        return False
    else:
        task['status'] = 'succeeded'
        return True

def retry_failed_tasks(backlog_path, manual_review_path, max_retries=2, delay=60):
    backlog = load_backlog(backlog_path)
    failed_tasks = [task for task in backlog if task['status'] == 'failed' and task['attempts'] < max_retries]
    
    for task in failed_tasks:
        while not process_task(task):
            time.sleep(delay)
        
        if task['attempts'] >= max_retries:
            task['status'] = 'manual_review_needed'
            manual_review = load_backlog(manual_review_path)
            manual_review.append(task)
            save_backlog(manual_review_path, manual_review)
    
    save_backlog(backlog_path, backlog)

def auto_review_low_complexity(backlog_path, output_path, limit=10):
    backlog = load_backlog(backlog_path)
    low_complexity_tasks = [task for task in backlog if task['status'] == 'succeeded' and task['complexity'] == 'low']
    
    auto_reviewed_tasks = random.sample(low_complexity_tasks, min(limit, len(low_complexity_tasks)))
    
    for task in auto_reviewed_tasks:
        task['auto_reviewed'] = True
        
    save_backlog(output_path, auto_reviewed_tasks)

def install_cron_jobs(script_path, cron_dir=str(Path.home() / "cron.d")):
    os.makedirs(cron_dir, exist_ok=True)
    
    with open(os.path.join(cron_dir, 'codex_retry'), 'w') as file:
        file.write('*/10 * * * * python {} retry\n'.format(script_path))
        
    with open(os.path.join(cron_dir, 'codex_autoreview'), 'w') as file:
        file.write('*/15 * * * * python {} autoreview\n'.format(script_path))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2 or sys.argv[1] not in ['retry', 'autoreview', 'install_cron']:
        print("Uso: python {} [retry|autoreview|install_cron]".format(sys.argv[0]))
        sys.exit(1)
    
    if sys.argv[1] == "retry":
        retry_failed_tasks('backlog_codex.json', 'manual_review.json')
        
    elif sys.argv[1] == "autoreview":
        auto_review_low_complexity('backlog_codex.json', 'auto_reviewed.json')
        
    elif sys.argv[1] == "install_cron":
        install_cron_jobs(sys.argv[0])
