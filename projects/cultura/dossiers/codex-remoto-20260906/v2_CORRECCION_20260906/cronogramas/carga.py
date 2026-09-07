#!/usr/bin/env python3
"""Calcula la carga mensual del responsable en cada escenario de adjudicacion.
Regenera CARGA_Y_ESCENARIOS.md. Reejecutar si cambian los perfiles de horas."""
JORNADA = 160
PROY = {
 "Ama Amoedo": {"inicio":"2027-01","perfil":{1:70,2:70,3:60,4:60,5:75,6:75,7:75,8:55,9:55,10:40,11:40,12:20}},
 "Difusion":   {"inicio":"2027-04","perfil":{1:50,2:50,3:55,4:60,5:60,6:55,7:45,8:40,9:40,10:35,11:30,12:20}},
 "Formativas": {"inicio":"2027-05","perfil":{1:45,2:55,3:70,4:70,5:70,6:70,7:45,8:35,9:30,10:25,11:20,12:15}},
 "Creacion":   {"inicio":"2027-04","perfil":{1:65,2:75,3:75,4:60,5:50,6:70,7:80,8:60,9:45,10:35,11:25,12:20}},
}
COMBOS = {
 "A · solo Ama Amoedo":["Ama Amoedo"], "B · solo Difusion":["Difusion"],
 "C · solo Formativas":["Formativas"], "D · Ama + Difusion":["Ama Amoedo","Difusion"],
 "E · Ama + Formativas":["Ama Amoedo","Formativas"],
 "F · Difusion + Formativas":["Difusion","Formativas"],
 "G · las tres recomendadas":["Ama Amoedo","Difusion","Formativas"],
 "H · Ama + Creacion + Formativas (con la alternativa)":["Ama Amoedo","Creacion","Formativas"],
}
def meses(ini, n=12):
    a, m = map(int, ini.split("-")); out = []
    for _ in range(n):
        out.append(f"{a}-{m:02d}"); m += 1
        if m == 13: a, m = a + 1, 1
    return out
SERIE = {k: {mm: v["perfil"][i+1] for i, mm in enumerate(meses(v["inicio"]))}
         for k, v in PROY.items()}
TODOS = sorted({m for s in SERIE.values() for m in s})
def marca(t):
    return "OK" if t <= 100 else ("ALTA" if t <= 140 else "**INSOSTENIBLE**")
if __name__ == "__main__":
    for nom, ps in COMBOS.items():
        tot = {m: sum(SERIE[p].get(m, 0) for p in ps) for m in TODOS}
        pico = max(tot.values())
        print(f"{nom:<52} pico {pico:>3} h/mes  total {sum(tot.values()):>5} h")
