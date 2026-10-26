-- Crea los roles y la base del proyecto. Se corre como superusuario:
--
--     psql -U postgres -f scripts/crear_base.sql
--
-- psql pide la clave de postgres y, al final, la clave nueva de cada rol con
-- \password, que no la muestra en pantalla ni la deja en ningún archivo.
-- Se puede volver a correr: lo que ya existe no se crea de nuevo, y las claves
-- se vuelven a pedir (sirve para cambiarlas).

\set ON_ERROR_STOP on

-- 1. Rol de la ingesta y de dbt. No es superusuario: solo es dueño de su base,
--    así que puede crear sus esquemas (raw, staging, marts) y nada más.
SELECT 'CREATE ROLE contrataciones_etl LOGIN'
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'contrataciones_etl')\gexec

-- 2. Base en UTF8 explícito, porque los datos traen tildes y Ñ. Se parte de
--    template0 para poder fijar la codificación aunque template1 tenga otra.
SELECT 'CREATE DATABASE contrataciones OWNER contrataciones_etl ENCODING ''UTF8'' TEMPLATE template0'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'contrataciones')\gexec

-- 3. Rol de solo lectura para el MCP de Postgres de Claude Code.
SELECT 'CREATE ROLE claude_lectura LOGIN'
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'claude_lectura')\gexec

GRANT CONNECT ON DATABASE contrataciones TO claude_lectura;

-- 4. Todo lo que cree contrataciones_etl de aquí en adelante (esquemas, tablas
--    y vistas) queda legible para claude_lectura. Así no hay que repetir un
--    GRANT después de cada dbt build, que vuelve a crear las tablas.
--    Puede volver a pedir la clave de postgres al cambiar de base.
\connect contrataciones
ALTER DEFAULT PRIVILEGES FOR ROLE contrataciones_etl GRANT USAGE ON SCHEMAS TO claude_lectura;
ALTER DEFAULT PRIVILEGES FOR ROLE contrataciones_etl GRANT SELECT ON TABLES TO claude_lectura;

-- 5. Claves de los dos roles.
\echo 'Clave para contrataciones_etl (la usan la ingesta y dbt):'
\password contrataciones_etl
\echo 'Clave para claude_lectura (la usa el MCP de Postgres):'
\password claude_lectura
