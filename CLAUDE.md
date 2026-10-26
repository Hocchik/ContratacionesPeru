# Contrataciones Perú

Pipeline de datos públicos de contrataciones del Estado peruano (OECE/SEACE +
BCRPData) que termina en un dashboard de Power BI sobre concentración de
proveedores. Proyecto de portafolio: cada decisión tiene que poder explicarse
en una entrevista.

El plan aprobado está en `docs/plan.md`. Las fichas de datos reales están en
`docs/datasets.md`. Ante cualquier duda, esos dos archivos mandan.

## Reglas no negociables

- **No inventes** nombres de columnas, archivos, URLs ni códigos de series. Si
  no lo leíste en un archivo real o en `docs/datasets.md`, escríbelo como
  "por verificar".
- Si un supuesto del plan resulta falso con los datos, **detente y avisa**
  antes de seguir.
- Un ticket a la vez, en su rama `ticket/<id>-<slug>`. Al terminar, deja
  `docs/prs/<ID>.md` y espera el code review. Usa `/ticket CP-N`.
- Nada de datos, credenciales ni `.env` en git. `data/` está en `.gitignore`.
- Soluciones simples antes que ingeniosas. Explica el "por qué" de cada
  decisión que no sea obvia.
- El SQL de staging/marts, el cálculo del HHI y las medidas DAX los escribe el
  usuario. Tú preparas la estructura, los TODO y los tests, y luego revisas.

## Arquitectura

```
descarga (Python) → data/raw/<fuente>/<dataset>/<año>/ + _manifest.csv
  → PostgreSQL esquema raw (todo texto + _source_file, _file_hash, _loaded_at)
  → dbt: staging (vistas) → intermediate → marts (tablas)
  → Power BI Desktop (importación desde marts)
```

- Ingesta **idempotente por archivo**: si el hash ya está en el manifiesto, no
  se recarga. Si es nuevo, se borra e inserta en una sola transacción.
- `staging`: un modelo por fuente, renombra a snake_case, castea tipos,
  normaliza el RUC (texto de 11 dígitos) y deduplica. No hace joins.
- `marts`: `fct_contratos` (1 fila = 1 contrato), `dim_entidad`,
  `dim_proveedor`, `dim_procedimiento`, `dim_fecha`,
  `agg_concentracion_entidad_anio`.
- Montos en soles con el tipo de cambio SBS venta (BCRP PD04640PD), usando el
  último dato disponible en o antes de la fecha de suscripción.

## Comandos (Windows)

```
.venv\Scripts\activate
python -m ingestion.<script> --help
cd dbt && dbt build
python .claude/skills/perfilar-dataset/perfilar.py <archivo>
```

En Windows usa `python` o `py`, nunca `python3`: ese comando suele abrir la
Microsoft Store. Esto aplica también cuando una skill diga `python3`.

## Convenciones

- Python: funciones chicas, type hints y logging en vez de `print` en la ingesta.
- SQL/dbt: CTEs con nombre (`import`, `logic`, `final`), snake_case y una
  sola responsabilidad por modelo. Cada modelo nuevo lleva `description` y
  tests en su `schema.yml`.
- Commits en español, en imperativo: "Agrega carga idempotente de contratos".
