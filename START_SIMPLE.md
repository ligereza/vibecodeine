# START SIMPLE — Flujo mínimo para no empezar de cero

Si todo el sistema se siente demasiado grande, usa solo esto.

## Objetivo

Acumular avance, guardar contexto y poder compartirlo con otra IA sin volver a explicar todo.

## Solo necesitas 3 cosas

```txt
1. inbox/                         Archivos sueltos, códigos, carpetas, pruebas viejas.
2. context/ESTADO_ACTUAL_SIMPLE.md Resumen vivo de lo que estás haciendo.
3. bash scripts/simple_checkpoint.sh "mensaje"  Guarda avance + GitHub.
```

---

# Flujo diario simple

## 1. Tirar archivos al inbox

Copia ahí cualquier cosa que ayude a entender tu avance:

```txt
inbox/
```

Puede ser:

- scripts viejos
- capturas
- notas
- carpetas a medias
- ejemplos de código
- exports livianos
- README viejos

No importa si están feos o incompletos. Son evidencia, no sistema final.

## 2. Editar el estado actual

Edita este archivo:

```txt
context/ESTADO_ACTUAL_SIMPLE.md
```

Responde solo estas preguntas:

```md
## Qué estoy intentando lograr
## Qué tengo funcionando aunque sea mal
## Qué está roto o incompleto
## Qué quiero que revise la próxima IA
## Próximo paso pequeño
```

## 3. Guardar checkpoint

Ejecuta:

```bash
bash scripts/simple_checkpoint.sh "avance del dia"
```

Eso:

- escanea `inbox/`
- actualiza `context/INBOX_INDEX.md`
- crea un checkpoint en `checkpoints/`
- hace commit
- hace push si ya conectaste GitHub

---

# Para compartir con una IA

Pega o sube estos archivos:

```txt
context/ESTADO_ACTUAL_SIMPLE.md
context/INBOX_INDEX.md
checkpoints/último checkpoint
```

Y usa este prompt:

```md
No empieces desde cero. Lee este estado actual, el índice de archivos y el último checkpoint. Necesito que me ayudes a ordenar el próximo paso mínimo. Trata los archivos como evidencia incompleta: pueden estar viejos, rotos o básicos.
```

---

# Regla principal

No intentamos crear el sistema perfecto ahora.

Solo buscamos:

```txt
guardar avance
+ entender qué existe
+ saber qué está roto
+ continuar desde ahí
```
