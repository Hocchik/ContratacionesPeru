---
name: perfilar-dataset
description: Perfila un archivo crudo (CSV, XLSX, JSON) del OECE, del SEACE o de BCRPData y documenta lo que realmente trae en docs/datasets.md. Úsalo cuando haya un archivo nuevo en data/raw, cuando haya que confirmar nombres de columnas, el grano, la clave natural, las monedas o la calidad del RUC, o en el ticket CP-0.
allowed-tools: Bash(python .claude/skills/perfilar-dataset/perfilar.py *), Bash(py .claude/skills/perfilar-dataset/perfilar.py *), Read, Edit
---

# Perfilar un dataset de Contrataciones Perú

El objetivo es reemplazar supuestos por hechos. Nada de lo que escribas en
`docs/datasets.md` puede venir de memoria ni de la documentación del portal:
sale del archivo real o se marca como "por verificar".

## Pasos

1. Ubica el archivo en `data/raw/<fuente>/<dataset>/<año>/`. Si no está ahí,
   pide al usuario que lo descargue a esa ruta; no lo descargues tú.
2. Corre el perfilador desde la raíz del repo (en Windows usa `python` o `py`):

   ```
   python .claude/skills/perfilar-dataset/perfilar.py <ruta> [--hoja NOMBRE] [--max-filas 200000]
   ```

   Si el archivo pesa más de ~300 MB, empieza con `--max-filas 200000` y dilo
   en la ficha.
3. Con la salida, responde estas preguntas. Si una no se puede responder con
   los datos, escribe "por verificar" y qué haría falta para saberlo:
   - **Grano**: ¿qué es una fila? ¿un contrato, un ítem, una adjudicación?
     Compruébalo: si la clave candidata se repite, mira 2–3 filas repetidas.
   - **Clave natural**: ¿qué columna o combinación es única? Verifícalo con un
     conteo, no por el nombre de la columna.
   - **Columnas de negocio**: monto, moneda, fecha de suscripción, RUC del
     proveedor, entidad, tipo de procedimiento, objeto contractual. Da el
     nombre real exacto de cada una.
   - **Consorcios**: ¿cómo se distinguen? ¿Hay % de participación por integrante?
   - **Calidad**: % de RUC nulo o inválido, monedas y su proporción, montos ≤ 0,
     fechas ilegibles, duplicados exactos.
4. Agrega o actualiza la ficha del dataset en `docs/datasets.md` con este formato:

   ```markdown
   ## <Nombre del dataset>
   - Fuente y URL: ...
   - Archivo y fecha de descarga: ...
   - Grano (1 fila = ...): ...
   - Clave natural: ... (única: sí/no, verificado con conteo)
   - Columnas usadas: | significado | nombre real | tipo esperado | % nulos |
   - Limitaciones encontradas: ...
   - Por verificar: ...
   ```

5. Termina con un resumen de 5 líneas como máximo: qué confirmaste, qué
   contradice al plan (`docs/plan.md`) y qué sigue por verificar.

## Reglas

- Lee todo como texto. No conviertas tipos en el perfilado.
- No modifiques ni muevas el archivo crudo.
- Si algo contradice al plan (por ejemplo, el dataset viene por ítem y no por
  contrato), **detente y avísale al usuario** antes de seguir con otro ticket.
- No muestres más de 3 valores de ejemplo por columna. Los datos son públicos,
  pero pueden incluir nombres de personas naturales con RUC 10.
