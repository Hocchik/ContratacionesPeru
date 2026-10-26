# Kit de Claude Code para Contrataciones Perú

> Es la guía con la que se instaló el kit (antes llamada `INSTALAR.md`). La
> puesta en marcha vigente del proyecto está en el [README](../README.md).
> Los pasos 3 (variables de entorno) y 4 (usuario de solo lectura) de esta
> guía los reemplazan el README y `scripts/crear_base.sql`, que además
> configura los privilegios por defecto de `claude_lectura`. Sigue vigente
> para los plugins, el MCP de Power BI (CP-6) y el origen de las skills.

Este kit deja Claude Code configurado para el proyecto: 7 skills, 2 servidores
MCP, permisos de seguridad y el `CLAUDE.md`. Tiempo estimado: 20–30 minutos.

## Qué trae

| Archivo | Qué es | Cuándo se usa |
| --- | --- | --- |
| `CLAUDE.md` | Reglas y arquitectura del proyecto. Claude Code lo lee en cada sesión | Siempre |
| `.claude/skills/ticket/` | **Skill propia.** `/ticket CP-N` trabaja un ticket del plan y deja la descripción del PR en `docs/prs/` | En cada ticket, invocada por ti |
| `.claude/skills/perfilar-dataset/` | **Skill propia** con script. Perfila un archivo crudo y llena `docs/datasets.md` | CP-0 y cada vez que llegue un archivo nuevo (se activa sola) |
| `.claude/skills/using-dbt-for-analytics-engineering/` | Oficial de dbt Labs: buenas prácticas para modelos, tests y depuración | CP-4 y CP-5 (se activa sola) |
| `.claude/skills/running-dbt-commands/` | Oficial de dbt Labs: cómo ejecutar el CLI de dbt correctamente | CP-4 en adelante (se activa sola) |
| `.claude/skills/adding-dbt-unit-test/` | Oficial de dbt Labs: unit tests de dbt | CP-5, para el modelo de concentración (se activa sola) |
| `.claude/skills/maintaining-dbt-documentation/` | Oficial de dbt Labs: audita y completa las `description` de `schema.yml` | CP-5 y CP-8 (se activa sola) |
| `.claude/skills/fetching-dbt-docs/` | Oficial de dbt Labs: consulta la documentación de dbt | Cuando haya dudas de dbt (se activa sola) |
| `.mcp.json` | Servidores MCP de dbt (local, sin dbt Cloud) y de PostgreSQL en **solo lectura** | Desde CP-4 |
| `.claude/settings.json` | Permisos: bloquea la lectura de `.env` y `profiles.yml`, pide confirmación para `git push` y prohíbe `push --force` | Siempre |

Las skills de dbt Labs se copiaron del repositorio oficial
[dbt-labs/dbt-agent-skills](https://github.com/dbt-labs/dbt-agent-skills)
(commit `b8facde`, 21 de octubre de 2026), bajo licencia Apache-2.0. La
licencia está en `.claude/skills/_licencias/`. Dejé fuera las de Semantic
Layer, Mesh, dbt Cloud y migraciones porque no aplican a dbt Core local.

---

## Paso 0. Requisitos en Windows

Instala lo que te falte. Para verificar cada uno, abre una terminal nueva y
corre el comando de la derecha.

| Herramienta | Para qué | Verificar |
| --- | --- | --- |
| Git for Windows | Claude Code y git | `git --version` |
| Python 3.11+ | Ingesta y dbt | `python --version` |
| Node.js LTS | `npx` (MCP de Power BI, el día 2) | `node --version` |
| uv | Ejecuta los MCP de dbt y Postgres con `uvx` | `uv --version` |
| PostgreSQL | Base local | `psql --version` |
| Claude Code | El agente | `claude --version` |

Para instalar uv en PowerShell: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`.
Está en la [documentación de uv](https://docs.astral.sh/uv/getting-started/installation/).

## Paso 1. Copiar el kit al repo

1. Descomprime el zip y copia **el contenido** de la carpeta
   `claude-kit-contrataciones-peru` (no la carpeta) a la raíz de tu repo
   `contrataciones-peru`. `.claude` y `.mcp.json` empiezan con punto; si el
   Explorador de Windows no los muestra, activa "Elementos ocultos". Este
   `INSTALAR.md` puedes moverlo a `docs/` o borrarlo cuando termines.
2. Guarda el plan exportado como `docs/plan.md`.
3. Si ya tenías un `CLAUDE.md`, combínalos en uno solo.
4. Haz commit del kit: `git add CLAUDE.md .claude .mcp.json` y luego
   `git commit -m "Agrega configuración de Claude Code"`. Es parte del repo y
   suma en el portafolio: muestra cómo trabajas con IA.

## Paso 2. Plugins oficiales de Anthropic

Abre Claude Code en la carpeta del repo (`claude`) y ejecuta:

```
/plugin install commit-commands@claude-plugins-official
/plugin install learning-output-style@claude-plugins-official
/reload-plugins
```

- **commit-commands**: comandos `/commit-commands:commit` y
  `/commit-commands:commit-push-pr`.
- **learning-output-style**: Claude te explica sus decisiones y te pide que
  escribas tú las partes clave. Cuando te pregunte el alcance, elige
  **proyecto** (no usuario): agrega tokens a cada sesión y no lo quieres en
  todos tus proyectos.
- Opcional: `pyright-lsp@claude-plugins-official` para revisión de tipos en
  Python. Requiere `npm install -g pyright`.

El marketplace oficial ya viene agregado en Claude Code. Si un `install`
falla, corre `/plugin marketplace update claude-plugins-official` y repite.

> **Alternativa a las skills copiadas:** puedes instalar todas las skills de
> dbt como plugin (`/plugin marketplace add dbt-labs/dbt-agent-skills` y luego
> `/plugin install dbt@dbt-agent-marketplace`). Así se actualizan solas, pero
> traen también las que no usas. **No uses las dos formas a la vez**: si
> instalas el plugin, borra las 5 carpetas de dbt de `.claude/skills/`.

## Paso 3. Variables de entorno de los MCP

`.mcp.json` no guarda rutas ni contraseñas: las lee de variables de entorno.
En PowerShell (ajusta las rutas a las tuyas y usa `/`):

```powershell
setx DBT_PROJECT_DIR "C:/Users/<tu_usuario>/contrataciones-peru/dbt"
setx DBT_PATH "C:/Users/<tu_usuario>/contrataciones-peru/.venv/Scripts/dbt.exe"
setx CONTRATACIONES_DB_URI_LECTURA "postgresql://claude_lectura:<clave>@localhost:5432/contrataciones"
```

Cierra y vuelve a abrir la terminal: `setx` solo afecta a terminales nuevas.

## Paso 4. Usuario de solo lectura en PostgreSQL

El MCP de Postgres ya corre en modo `restricted` (solo lectura). Un usuario sin
permisos de escritura es la segunda capa de defensa; es lo que harías en una
empresa. Primero, en `psql` como superusuario:

```sql
CREATE ROLE claude_lectura LOGIN PASSWORD '<clave>';
GRANT CONNECT ON DATABASE contrataciones TO claude_lectura;
```

Después del primer `dbt build` (CP-4), cuando ya existan los esquemas, otorga
lectura por esquema. Revisa los nombres reales con `\dn`: dbt suele anteponer
el esquema base, por ejemplo `public_staging`.

```sql
GRANT USAGE ON SCHEMA raw TO claude_lectura;
GRANT SELECT ON ALL TABLES IN SCHEMA raw TO claude_lectura;
-- repetir para cada esquema de staging, intermediate y marts
```

`GRANT SELECT ON ALL TABLES` no cubre tablas creadas después. Si dbt recrea
una tabla, vuelve a correrlo, o configura `ALTER DEFAULT PRIVILEGES` con el
mismo usuario que usa dbt.

## Paso 5. Verificar

En Claude Code, dentro del repo:

1. `/skills`: deben aparecer `ticket`, `perfilar-dataset` y las 5 de dbt.
2. `/mcp`: Claude Code te pide aprobar `dbt` y `postgres` la primera vez
   (vienen de `.mcp.json`). Apruébalos. **Antes de CP-4 aparecerán como
   fallidos**, porque todavía no existen ni la carpeta `dbt/` ni la base. Es
   normal.
3. Prueba rápida: escribe `/ticket CP-1`. Claude Code debe leer
   `docs/plan.md` y proponerte un plan corto antes de tocar nada.

---

## MCP opcionales (cuando lleguen sus tickets)

### Día 2, CP-6: Power BI Modeling MCP (Microsoft, Public Preview)

Se conecta a tu modelo abierto en Power BI Desktop. **Haz un backup del archivo
antes de conectarlo.** Úsalo para descripciones de medidas, formatos y revisar
relaciones. Las medidas DAX las escribes tú.

```
claude mcp add powerbi-modeling -- npx -y @microsoft/powerbi-modeling-mcp@latest --start
```

Si en Windows no arranca, prueba envolverlo:
`claude mcp add powerbi-modeling -- cmd /c npx -y @microsoft/powerbi-modeling-mcp@latest --start`.
Instrucciones oficiales: [microsoft/powerbi-modeling-mcp](https://github.com/microsoft/powerbi-modeling-mcp).

### Sprint R1: Terraform (HashiCorp)

Está en el marketplace oficial y requiere Docker Desktop:

```
/plugin install terraform@claude-plugins-official
```

---

## Cosas que conviene saber

- **Las skills y el `.mcp.json` del repo funcionan en Claude Code local**
  (terminal o app de escritorio sobre tu carpeta). Las sesiones en la nube de
  Claude Code no cargan las skills ni el `.mcp.json` del repo; solo el
  `CLAUDE.md`.
- **Los permisos `deny` de lectura** bloquean las herramientas de archivos de
  Claude y comandos como `cat`, pero no un script de Python que abra el
  archivo por su cuenta. Por eso las contraseñas viven en variables de entorno
  y no en el repo.
- **Para actualizar las skills de dbt**, vuelve a copiarlas del repositorio
  oficial o cámbiate al plugin (ver Paso 2).

## Fuentes

- Claude Code: [Skills](https://code.claude.com/docs/en/skills), [MCP](https://code.claude.com/docs/en/mcp), [Permisos](https://code.claude.com/docs/en/permissions), [Descubrir plugins](https://code.claude.com/docs/en/discover-plugins), [Projects](https://code.claude.com/docs/en/claude-projects)
- [dbt Agent Skills (dbt Labs)](https://github.com/dbt-labs/dbt-agent-skills) · [dbt MCP local](https://docs.getdbt.com/docs/dbt-ai/setup-local-mcp)
- [Postgres MCP Pro](https://github.com/crystaldba/postgres-mcp)
- [Plugins oficiales de Anthropic](https://github.com/anthropics/claude-plugins-official)
