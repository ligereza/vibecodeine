import json
from datetime import datetime, timedelta

def main():
    with open('logs/red.jsonl', 'r') as file:
        logs = file.readlines()
    
    timeline = {}
    for log in logs:
        entry = json.loads(log)
        fecha = entry['fecha']
        estado = entry['estado']
        
        if fecha not in timeline:
            timeline[fecha] = []
        timeline[fecha].append(estado)
    
    for fecha, estados in sorted(timeline.items()):
        print(f"{fecha}:")
        tiempo_inicio = datetime.strptime(f"{fecha} 00:00:00", "%Y-%m-%d %H:%M:%S")
        for estado in estados:
            print(f"  - {tiempo_inicio.strftime('%H:%M:%S')}: {estado}")
            if estado == "online":
                tiempo_inicio += timedelta(seconds=1)
            elif estado == "offline":
                tiempo_inicio += timedelta(seconds=1)

if __name__ == "__main__":
    main()
    print("PRUEBAS OK")
