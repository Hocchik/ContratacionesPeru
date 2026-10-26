# CP-1 — Repo y entorno

## Qué
Deja una base que se puede reproducir en Windows: las carpetas del proyecto, un
`requirements.txt` con versiones fijas, un script SQL que crea la base y los
roles, el esqueleto de dbt conectado por variables de entorno y un README con
la puesta en marcha. No hay modelos ni ingesta: eso llega en CP-2 a CP-4.

## Por qué (decisiones)
- **dbt-core fijado en 1.12.6 por separado** — Sin ese pin, pip instalaba la
  beta `1.13.0b1`. El motivo es que `dbt-postgres` pide
  `dbt-core>=1.8.0rc1`, y por ese "rc" pip también acepta versiones
  preliminares. Se descartó dejarlo suelto porque no tiene sentido construir
  sobre una beta.
- **Se queda en dbt Core v1 y no en dbt v2 (Fusion)** — dbt avisa al correr que
  "dbt v2 is available, and is the default for new installations". El plan
  (`requirements.txt` + `.venv`) y el kit (`DBT_PATH` apunta a
  `.venv/Scripts/dbt.exe`) suponen dbt Core instalado con pip, y las skills
  de dbt Labs soportan los dos. **Lo dejo a revisión del tech lead.**
- **Solo se fijan las dependencias directas** — Se descartó `pip freeze`
  (fija unos 60 paquetes, algunos propios de Windows, y es difícil de leer) y
  también `uv lock` (suma una herramienta más a la parte de Python). Con 6
  dependencias directas, el riesgo de que cambie una transitiva es bajo y
  queda anotado.
- **`psycopg2-binary` como único driver** — Es el mismo que ya instala
  `dbt-postgres`. Se descartó psycopg 3 para no tener dos drivers de
  Postgres en el proyecto.
- **Rol `contrataciones_etl` sin superusuario, dueño de la base** — Lo decidió
  el usuario. Se descartó usar `postgres` porque la ingesta y dbt no
  necesitan poder tocar otras bases.
- **Clave en una variable de entorno del usuario de Windows** — Lo decidió el
  usuario. Se descartó `.env` porque ni dbt ni el MCP de dbt lo leen. El
  README la guarda con `Read-Host -AsSecureString` y no con `setx "<clave>"`,
  que dejaría la clave en texto plano en el historial de PowerShell.
- **`dbt/profiles.yml` dentro del repo, con `env_var()`** — Se descartó
  `~/.dbt/profiles.yml` porque no se versiona y quien clone tendría que
  armarlo a mano. Además está en el `deny` de `.claude/settings.json`. Solo
  la clave es obligatoria: el resto tiene un valor por defecto para Postgres
  local.
- **`ALTER DEFAULT PRIVILEGES` para `claude_lectura`** — Se descartó el `GRANT
  SELECT ON ALL TABLES` después de cada build (Paso 4 de `INSTALAR.md`),
  porque `dbt build` recrea las tablas y el permiso se pierde.
- **Base en UTF8 explícito desde `template0`** — Los datos traen tildes y Ñ.
  Se descartó usar la codificación por defecto del servidor porque en Windows
  depende de cómo se instaló.
- **CP-1 antes de CP-0** — El plan pone CP-0 primero, pero CP-1 no depende de
  los datos, y así CP-0 ya encuentra el `.venv` y `perfilar.py` funcionando.
- **Fuera de alcance a propósito:** la intermediate queda en vista (el default
  de dbt) hasta CP-5, y el esquema destino es `public` hasta que CP-4 defina
  los esquemas por capa.

## Cómo probarlo
En PowerShell, desde la raíz del repo:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
psql -U postgres -f scripts/crear_base.sql
$clave = Read-Host "Clave de contrataciones_etl" -AsSecureString
[Environment]::SetEnvironmentVariable("CONTRATACIONES_DB_PASSWORD", [Net.NetworkCredential]::new("", $clave).Password, "User")
```

Después, en una terminal **nueva**:

```powershell
.venv\Scripts\Activate.ps1
cd dbt
dbt debug
```

## Criterios de aceptación
- [x] Estructura `ingestion/`, `dbt/`, `powerbi/` y `docs/` — `git diff --stat
  main..HEAD` muestra las 4 carpetas (vacías, con `.gitkeep`, salvo
  `ingestion/__init__.py`).
- [x] `data/` en `.gitignore` — `git check-ignore -v
  data/raw/oece/contratos/2024/x.csv` → `.gitignore:2:data/`. También quedan
  ignorados `.venv/`, `dbt/target/`, `dbt/logs/` y `dbt/.user.yml`.
- [x] Postgres local corriendo — `pg_isready -h localhost -p 5432` →
  `localhost:5432 - aceptando conexiones`. El servicio `postgresql-x64-17`
  está en `Running`.
- [x] `requirements.txt` — Se borró el `.venv`, se recreó y se corrió
  `pip install -r requirements.txt` → `pip check`: `No broken requirements
  found.` `dbt --version` → Core 1.12.6, postgres 1.11.0. `perfilar.py` probado
  con pandas 3.1 sobre un CSV de prueba en latin-1: lee bien tildes, Ñ y RUC.
- [x] El README explica cómo levantarlo en Windows — `README.md`, secciones
  1 a 4.
- [x] El proyecto dbt se carga — `dbt parse --project-dir dbt --profiles-dir
  dbt` → exit 0. Avisa de 3 rutas de configuración sin modelos, lo que es
  esperable hasta CP-4.
- [ ] **La base existe y dbt se conecta (`dbt debug` → `All checks passed!`)**
  — Falta que el usuario corra `crear_base.sql`, guarde la clave y ejecute
  `dbt debug`. La IA no puede: el hook `guardian-secretos` bloquea cualquier
  comando que toque variables con claves, y la IA no ingresa contraseñas.

## Hecho por la IA vs. por el usuario
- IA: `.gitattributes`, `.gitignore` (`dbt_packages/`, `.user.yml`),
  `ingestion/__init__.py`, `requirements.txt`, `scripts/crear_base.sql`,
  `dbt/dbt_project.yml`, `dbt/profiles.yml`, `README.md` y este documento.
- Usuario: tres decisiones de diseño (rol de la base, mecanismo de
  credenciales y alcance de dbt en CP-1). Ejecutar `crear_base.sql` y
  `dbt debug`.
- El usuario debe verificar:
  1. Que `crear_base.sql` corra completo. No lo pude probar sin la clave de
     `postgres`. En particular, que `\password` pida las claves aunque el
     script corra con `-f`, y que `\connect contrataciones` no falle.
  2. `dbt debug` → `All checks passed!`.
  3. La codificación: `psql -U postgres -c "\l contrataciones"` debe mostrar
     `UTF8`.
  4. Los privilegios por defecto: `psql -U postgres -d contrataciones -c
     "\ddp"` debe mostrar 2 filas para `contrataciones_etl` → `claude_lectura`
     (schema `U`, table `r`).

## Pendientes y riesgos
- **dbt v1 o v2:** la decisión de arriba queda para el tech lead. Si se pasa a
  v2, cambian la instalación, el `DBT_PATH` del MCP y parte del README.
- **Esquemas por capa (CP-4):** si se usa `+schema: staging` sin
  sobrescribir `generate_schema_name`, dbt crea `public_staging` y no
  `staging`, como pide el plan.
- **No hay remoto en GitHub:** la definición de "listo" pide un PR hacia
  `main`. Hasta que exista el remoto, el merge tendría que ser local.
- **`INSTALAR.md` sigue sin versionar:** el README ya cubre la puesta en
  marcha, y `crear_base.sql` reemplaza su Paso 4. Falta decidir si se mueve
  a `docs/` o se borra.
- **MCP de dbt:** por verificar si `dbt-mcp` encuentra `dbt/profiles.yml`
  cuando se definan `DBT_PROJECT_DIR` y `DBT_PATH`.
- **Valores por defecto duplicados:** la ingesta (CP-2) va a leer las mismas
  variables. Sus valores por defecto tienen que coincidir con los de
  `profiles.yml`.
- **Python de la Microsoft Store:** funciona (3.12.10), pero si aparecen
  problemas raros de rutas en `AppData`, la alternativa es el instalador de
  python.org.
