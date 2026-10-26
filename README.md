# Contrataciones Perú

Pipeline de datos públicos de contrataciones del Estado peruano (OECE/SEACE y
tipo de cambio de BCRPData) que termina en un dashboard de Power BI sobre la
concentración de proveedores por entidad y año.

> **Estado:** en construcción (sprint v1). El plan está en
> [docs/plan.md](docs/plan.md). Por ahora este README explica cómo levantar el
> entorno; la arquitectura, las métricas y las limitaciones se completan en
> CP-8.

## Estructura

```
ingestion/   descarga y carga al esquema raw (python -m ingestion.<script>)
dbt/         proyecto dbt: staging -> intermediate -> marts
powerbi/     archivo .pbix y capturas del dashboard
scripts/     SQL para crear la base y los roles
docs/        plan, fichas de datos y descripciones de los PR
data/        archivos descargados; no va a git
```

## Requisitos (Windows)

| Herramienta | Versión probada | Verificar |
| --- | --- | --- |
| Git for Windows | 2.55 | `git --version` |
| Python | 3.12 (sirve 3.11 o más) | `python --version` |
| PostgreSQL | 17 | `psql --version` |

Si `psql` no se reconoce, agrega `C:\Program Files\PostgreSQL\17\bin` al
`PATH` o llámalo con la ruta completa.

## Puesta en marcha

### 1. Entorno de Python

Desde la raíz del repo, en PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell responde que la ejecución de scripts está deshabilitada, puedes
activar el entorno desde `cmd` con `.venv\Scripts\activate.bat`, o permitir
scripts locales para tu usuario con
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. Esto último cambia una
política de seguridad de Windows: decídelo tú.

### 2. Base de datos

```powershell
psql -U postgres -f scripts/crear_base.sql
```

El script pide la clave de `postgres` y después la clave nueva de cada rol.
Crea:

- `contrataciones_etl`: el rol con el que corren la ingesta y dbt. No es
  superusuario; es dueño de la base `contrataciones` y nada más.
- `contrataciones`: la base, en UTF8.
- `claude_lectura`: un rol de solo lectura para el MCP de Postgres de Claude
  Code. Puede leer todo lo que cree `contrataciones_etl`.

Se puede volver a correr sin romper nada.

### 3. Variables de entorno

La ingesta y dbt leen la conexión de variables de entorno de tu usuario de
Windows. Así no hay claves en el repo.

| Variable | Obligatoria | Valor por defecto |
| --- | --- | --- |
| `CONTRATACIONES_DB_PASSWORD` | Sí | (ninguno) |
| `CONTRATACIONES_DB_USER` | No | `contrataciones_etl` |
| `CONTRATACIONES_DB_NAME` | No | `contrataciones` |
| `CONTRATACIONES_DB_HOST` | No | `localhost` |
| `CONTRATACIONES_DB_PORT` | No | `5432` |

Para guardar la clave sin que quede escrita en el historial de PowerShell (con
`setx "..."` sí quedaría):

```powershell
$clave = Read-Host "Clave de contrataciones_etl" -AsSecureString
[Environment]::SetEnvironmentVariable("CONTRATACIONES_DB_PASSWORD", [Net.NetworkCredential]::new("", $clave).Password, "User")
```

Cierra y vuelve a abrir la terminal: las variables nuevas solo llegan a las
terminales que se abren después.

### 4. Verificar

```powershell
.venv\Scripts\Activate.ps1
cd dbt
dbt debug
```

Tiene que terminar con `All checks passed!`.

Si PowerShell dice que no reconoce `dbt`, el entorno no está activado: dbt solo
está instalado dentro de `.venv`, y con el entorno activo el prompt empieza con
`(.venv)`. Desde `dbt/`, actívalo con `..\.venv\Scripts\Activate.ps1`.

## Claude Code

El repo incluye la configuración con la que se trabaja con Claude Code:
`CLAUDE.md`, las skills de `.claude/skills/` y los MCP de `.mcp.json` (dbt y
Postgres en solo lectura). El detalle del kit (plugins, origen de las skills
y el MCP de Power BI) está en
[docs/kit-claude-code.md](docs/kit-claude-code.md). Los MCP leen estas
variables de entorno:

| Variable | Qué es |
| --- | --- |
| `DBT_PROJECT_DIR` | Ruta absoluta a la carpeta `dbt/` del repo |
| `DBT_PATH` | Ruta absoluta a `.venv/Scripts/dbt.exe` |
| `CONTRATACIONES_DB_URI_LECTURA` | `postgresql://claude_lectura:<clave>@localhost:5432/contrataciones` |
