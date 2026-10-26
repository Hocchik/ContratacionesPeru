---
name: ticket
description: Trabaja un ticket del plan de Contrataciones Perú (CP-0 a CP-8, R1 a R4) de punta a punta y deja lista la descripción del PR para el code review del tech lead. Úsalo cuando el usuario escriba /ticket CP-N.
disable-model-invocation: true
argument-hint: CP-N
---

# Trabajar el ticket $ARGUMENTS

Eres el desarrollador. El tech lead revisa tu trabajo en otra conversación,
así que todo lo que decidas tiene que quedar escrito y justificado.

## 1. Entender antes de tocar código

1. Lee el ticket `$ARGUMENTS` en `docs/plan.md`: contexto, criterios de
   aceptación y la definición de "listo". Si el ticket no existe, detente.
2. Lee `docs/datasets.md` si el ticket toca datos. Usa solo nombres de
   columnas que estén ahí; si falta alguno, usa la skill `perfilar-dataset`.
3. Escribe al usuario, en 5 líneas como máximo: qué vas a hacer, en qué orden
   y qué supuestos estás tomando. Espera su "ok" si algún supuesto es dudoso.

## 2. Hacer

- Crea la rama `ticket/<id-en-minúsculas>-<slug-corto>` desde `main`.
- Avanza en pasos chicos. Haz un commit por paso lógico.
- **Reparto con el usuario** (es parte del objetivo del proyecto):
  - Lo escribe el usuario: el SQL de staging y marts, el cálculo de
    participaciones y del HHI, y las medidas DAX. Tú preparas el archivo con
    la estructura, un comentario `-- TODO(usuario):` que explica qué falta y
    por qué, y los tests que deben pasar. Luego revisas lo que escribió.
  - Lo puedes escribir tú: andamiaje, scripts de descarga y carga, manifiesto,
    tests repetitivos, configuración y documentación.
- No inventes columnas, archivos ni URLs. Si algo no está verificado,
  márcalo como "por verificar".

## 3. Verificar

Corre lo que aplique al ticket y guarda la salida resumida:

- Scripts de ingesta: córrelos **dos veces** y confirma que la segunda vez no
  cambia el conteo de filas (idempotencia).
- dbt: `dbt build` (o `dbt build --select <modelos>`) sin errores. Los warnings
  deben estar explicados.
- Revisa cada criterio de aceptación uno por uno: cumple o no cumple, con evidencia.

## 4. Entregar

Crea `docs/prs/$ARGUMENTS.md` con esta plantilla y muéstrasela al usuario:

```markdown
# $ARGUMENTS — <título>

## Qué
<2–4 líneas>

## Por qué (decisiones)
- <decisión> — <alternativa descartada y motivo>

## Cómo probarlo
<comandos exactos, en Windows>

## Criterios de aceptación
- [x] <criterio> — <evidencia: comando + resultado>
- [ ] <criterio> — <por qué no se cumple>

## Hecho por la IA vs. por el usuario
- IA: <archivos o partes>
- Usuario: <archivos o partes>
- El usuario debe verificar: <lista concreta>

## Pendientes y riesgos
- <...>
```

Después **detente**. No empieces el siguiente ticket aunque tengas tiempo:
primero va el code review.
