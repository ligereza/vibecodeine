---
name: spanish-input-optimizer
description: |
  Compress Spanish input to English for token-efficient processing, then return response in Spanish.
  
  Use this skill whenever the user writes a prompt in Spanish — any domain (code questions, data analysis, 
  documentation, creative writing, technical help). The skill translates to compressed English (removing 
  redundancy, keeping only critical info), processes in English (saves ~15-20% tokens), and returns the 
  response fully in Spanish. No context lost, just leaner processing.
  
  Triggers: Spanish language prompts, email/messages in Spanish, any user request that isn't in English, 
  even if mixed with code or URLs.
---

# Spanish Input Optimizer

## How it works

When you write in Spanish, this skill:

1. **Reads your Spanish prompt** — any length, any domain (analysis, code review, creative work, questions)
2. **Translates to compressed English** — removes filler words, repetition, unnecessary context; keeps critical info intact
3. **Processes in English** — Claude processes the compressed version (15-20% token savings vs. processing Spanish directly)
4. **Returns response in Spanish** — complete, natural response; nothing lost in compression

## Why this saves tokens

Spanish uses ~15-20% more tokens than English for the same meaning:
- Longer average words
- More inflected forms (verb conjugations, gendered adjectives)
- Accented characters

By compressing to English for processing, you get the same quality output with fewer tokens burned.

## What gets compressed

**Removed:**
- Filler phrases ("Bueno, entonces...", "Es decir que...")
- Redundant explanations (first mention of concept is kept; repetitions are cut)
- Politeness overhead ("Por favor, ¿podrías...?" → imperative form in English)
- Repeated context (if mentioned twice, keep once)

**Preserved:**
- All technical terms, variable names, file paths
- Specific numbers, dates, amounts
- Code samples (exact formatting)
- Core intent and all nuance
- Examples the user provided
- Edge cases and requirements

## Example

**Your Spanish input:**
```
Mira, tengo este problema que no logro resolver. Estoy intentando crear un script en Python 
para leer un archivo CSV, y bueno, después procesarlo. Lo que quiero hacer es, en realidad, 
extraer ciertas columnas específicas (columnas A y C) y luego guardar el resultado en un 
archivo nuevo. ¿Cómo debería hacerlo?
```

**Compressed English (internal):**
```
Read CSV file, extract columns A+C, save to new file. Python script.
```

**Processing result (in Spanish):**
```
Aquí está el script que necesitas. Lee el CSV, extrae las columnas especificadas 
y guarda en un archivo nuevo...
```

Token savings: ~35% on input (compression) + response fully in Spanish as usual.

## Mixed code/language

If your prompt mixes Spanish with code, file paths, or URLs:
- Code blocks stay exact (no compression)
- File paths/URLs unchanged
- Spanish narrative gets compressed
- Response still fully in Spanish

## When NOT to compress

The skill auto-detects and skips if:
- Input is already in English
- Input is pure code (no Spanish prose)
- Input is a very short single sentence (compression not worth it)

Otherwise, compression always applies.

## Where this runs (important)

This compression only saves Claude's INPUT tokens when it happens BEFORE Claude, in the interpreter layer (Gemini/Arena). As a skill running inside Claude, the Spanish prompt is already ingested, so translating it internally does not refund those input tokens. Use this skill only as a fallback for direct chats with Claude; for the real savings, let the interpreter compress the request before it reaches Claude.
