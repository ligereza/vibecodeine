import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

def review_item(item: dict, provider: str) -> dict:
    approved = item['score'] >= 0.7
    return {
        'id': item['id'], 
        'approved': approved, 
        'reason': 'Aprobado' if approved else 'Reprobado', 
        'provider': provider
    }

def review_batch(items: list[dict], provider: str = 'cerebras', concurrency: int = 4, success_threshold: float = 0.8) -> dict:
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(review_item, item, provider): item for item in items}
        approved, total = 0, 0
        details = []
        for future in as_completed(futures):
            result = future.result()
            details.append(result)
            if result['approved']:
                approved += 1
            total += 1
        rate = float(approved / total)
        passed = rate >= success_threshold
    return {
        'total': total, 
        'approved': approved, 
        'failed': total - approved, 
        'rate': rate, 
        'passed': passed, 
        'details': details
    }

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--provider', default='cerebras')
    parser.add_argument('--concurrency', type=int, default=4)
    parser.add_argument('--threshold', type=float, default=0.8)
    args = parser.parse_args(argv)
    
    items = [{'id': i, 'score': random.uniform(0.5, 1)} for i in range(13)] if not argv else argv
    report = review_batch(items, **vars(args))
    
    print('Total:', report['total'])
    print('Aprobados:', report['approved'])
    print('Fallidos:', report['failed'])
    print('Tasa de éxito:', report['rate'])
    print('Pasado:', 'Sí' if report['passed'] else 'No')
    
    return 0 if report['passed'] else 1

if __name__ == "__main__":
    random.seed(42) # Semilla para reproducibilidad de los tests
    assert main() == 0, "Pruebas fallidas"
    print("PRUEBAS OK")
