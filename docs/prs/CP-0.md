# CP-0 — Spike de datos

## Qué
Se perfilaron los 4 archivos OECE de 2024 (Contratos, Proveedores,
Consorcios y Entidades) y los diccionarios oficiales. También se revisó el
portal sin descargar nada, y todo quedó en `docs/datasets.md`.
**Decisión: portal OECE**, con "Datos de la Adjudicación" como quinto
dataset para el tipo de procedimiento. Además se corrigió el perfilador, que
leía mal las fechas ISO.

## Por qué (decisiones)
- **Portal OECE y no OCDS** — OCDS era el plan B por si el portal no
  servía. El portal sirve: Contratos se une al 100% con Entidades y con los
  códigos de Consorcios, y al 99.9% con Proveedores. El tipo de
  procedimiento existe en el mismo portal.
- **Adjudicación como fuente del tipo de procedimiento, no Convocatorias** —
  El diccionario de Adjudicación confirma `TIPOPROCESOSELECCION` y
  `CODIGOCONVOCATORIA`. De Convocatorias no llegaron ni el archivo ni el
  diccionario: lo que contiene sigue por verificar.
- **Monto del contrato = `MONTO_CONTRATADO_TOTAL` una vez por
  `N_COD_CONTRATO`** — Se descartó sumar por fila porque infla 3.1 veces
  (las filas repiten el contrato por cada modificación). Sumar los ítems
  distintos da lo mismo en el 99.99% de los casos, pero es más trabajo.
- **Clave `N_COD_CONTRATO` y no `CODIGO_CONTRATO`** — Según el diccionario,
  `CODIGO_CONTRATO` era un código compuesto hasta 2020; recién en 2024 son
  iguales.
- **Corregir el perfilador en vez de interpretar su salida** — Con
  `dayfirst=True`, pandas leía `2025-03-06` como 3 de junio y reportó un
  falso "35.5% legible". Ahora solo acepta `AAAA-MM-DD` y `DD/MM/AAAA`,
  como pide el plan para staging ("no se adivina"). Se agregó `--sep`
  porque el CSV de entidades usa `|` y el detector automático fallaba.
- **Los scripts del análisis van al repo (`scripts/spike_cp0/`)** — Se
  descartó dejarlos solo en local porque el reviewer no podría reproducir
  las cifras. Son de un solo uso; no son la ingesta.
- **No se tocó `docs/plan.md`** — Los cambios al plan los decide el tech
  lead. Abajo quedan propuestos.

## Cómo probarlo
Requiere el `.venv` de CP-1 y los archivos en `data\raw\oece\` con los
SHA-256 de `docs/datasets.md`. En PowerShell, desde la raíz:

```powershell
.venv\Scripts\python.exe -I .claude\skills\perfilar-dataset\perfilar.py data\raw\oece\contratos\2024\CONOSCE_CONTRATOS2024_0.xlsx
.venv\Scripts\python.exe -I .claude\skills\perfilar-dataset\perfilar.py data\raw\oece\entidades\entidades_contratantes.csv --sep "|"
.venv\Scripts\python.exe -I scripts\spike_cp0\analisis.py data\raw\oece
.venv\Scripts\python.exe -I scripts\spike_cp0\repetidas.py data\raw\oece
.venv\Scripts\python.exe -I scripts\spike_cp0\total_items.py data\raw\oece
.venv\Scripts\python.exe -I scripts\spike_cp0\peso_consorcios.py data\raw\oece
.venv\Scripts\python.exe -I scripts\spike_cp0\consorcios_y_entidades.py data\raw\oece
.venv\Scripts\python.exe -I scripts\spike_cp0\diccionarios.py data\raw\oece\diccionario
```

Cifras para comparar: 7,477 contratos; 70,366 vs. 22,548 millones (por
fila vs. por contrato); consorcios = 70.2% del monto en soles; 1,480 grupos
de consorcio con más de un código.

## Criterios de aceptación
- [x] Descargaste 1 año de Contratos, Proveedores y Consorcios y Entidades
  — Los bajó el usuario: 2024. Los nombres, las filas y los SHA-256 están
  al inicio de `docs/datasets.md`.
- [x] `docs/datasets.md` tiene, por dataset: nombres reales de las
  columnas, qué es una fila, clave natural candidata, columnas de moneda,
  monto y fecha, y n.º de filas — Las 4 fichas, más una de Adjudicación
  solo con el diccionario. Las claves se verificaron con conteos (scripts
  `analisis.py` y `repetidas.py`).
- [x] Decisión escrita: portal OECE u OCDS — Sección "Decisión de fuente":
  portal OECE.
- [x] (pedido del usuario) Usar los diccionarios para confirmar columnas —
  Se usaron los de Contratos, Adjudicación, Entidades y Consorcios (2
  versiones). Falta el de Proveedores; no llegó.
- [ ] (pedido del usuario) Resolver la contradicción 1 — **Parcial.** El
  tipo de procedimiento está en Adjudicación (`TIPOPROCESOSELECCION`),
  unible por `CODIGOCONVOCATORIA` según los diccionarios, pero **sin
  verificar con datos**. El objeto contractual no aparece en ningún
  diccionario recibido. La unión Convocatorias–Contratos no se pudo
  revisar: `data/raw/oece/convocatorias/2024/` no existe.
- [x] (pedido del usuario) Entidades: nivel de gobierno, sector o tipo — No
  los trae: lo confirman el archivo y el diccionario. Por el nombre solo se
  clasifica el 60.4% de los contratos.
- [x] (pedido del usuario) Consorcios Adjudicados: integrantes y % — Trae
  integrantes (`RUC_MIEMBRO`, `MIEMBRO`) y **no trae %**, ni en la versión
  actual ni en la v1 del diccionario. La carpeta
  `data/raw/oece/consorcios/2024/` no existe; por el diccionario y la ruta
  del portal es el mismo `CONOSCE_CONSORCIO2024_0.xlsx` ya perfilado.
- [ ] Timebox de 45 minutos — Se pasó: hubo 3 rondas por archivos que
  faltaban y una revisión del portal.

## Hecho por la IA vs. por el usuario
- IA: la corrección de `.claude/skills/perfilar-dataset/perfilar.py`,
  `docs/datasets.md`, `scripts/spike_cp0/*.py`, la revisión del portal en
  el navegador y este documento.
- Usuario: la descarga de los 4 archivos de datos y de los diccionarios.
- El usuario debe verificar:
  1. Correr 2 o 3 de los comandos de "Cómo probarlo" y comparar las cifras.
  2. Si bajó `CONOSCE_CONVOCATORIAS2024_0.xlsx` y un "Consorcios
     Adjudicados" distinto. No están en `data/raw/oece/`.
  3. Que el "diccionario de Proveedores y Consorcios" que mencionó sea el de
     Consorcios Adjudicados; no hay otro en la carpeta.

## Pendientes y riesgos
**Decisiones para el tech lead.** Cambian `docs/plan.md`:
1. **Objeto contractual:** no aparece en ninguna fuente revisada. Opciones:
   sacar el filtro por objeto de la v1, o revisar Convocatorias en CP-2.
2. **Nivel de gobierno para los pares:**
   - una fuente externa por `CODIGO_SIAF` (MEF, por verificar);
   - una regla por nombre (Municipalidad, Gobierno Regional, Ministerio y
     "otros"), que cubre el 60.4% de los contratos;
   - o pares solo por tercil de monto.
3. **Clave del consorcio:** el código cambia en cada procedimiento. Usarlo
   como `proveedor_key` fragmenta a los consorcios, que son el 70.2% del
   monto, y subestima el HHI. La alternativa es identificarlos por el
   conjunto de RUC de sus miembros.
4. **Contratos resueltos o nulos** (92, 1.2%): ¿cuentan para el HHI?
5. **Línea de corte por años:** el archivo de un año agrupa por convocatoria.
   Para cerrar un año de suscripción Y hay que cargar Y y Y−1.

**Cambios técnicos que siguen de estos hallazgos:**
- CP-2: bajar también Adjudicación y medir la unión con Contratos. Usar las
  rutas del servidor (`reportes/<dataset>/<año>/`): el archivo de consorcios
  vive en `consorcios/`, no en `proveedores/`.
- CP-3: hay 5 contratos en euros, así que también hace falta PD04648PD.
- CP-4:
  - deduplicar a nivel contrato antes de sumar montos;
  - mapear `Soles` y `Nuevos Soles` a PEN;
  - aceptar fechas con y sin hora;
  - en el test "RUC válido", separar los códigos de consorcio, que si no
    darían 36.5% de "inválidos".

**Por verificar:** qué son los identificadores `L0…` (70 contratos), por qué
`MONTO_ADICIONAL` es mayor que 0 en el 69% de los contratos, y si existen
partes de archivos que el portal no enlaza.

**Orden de merge:** esta rama sale de `main` sin CP-1. Conviene mergear
CP-1 primero, porque `docs/prs/` y el `.venv` vienen de ahí.
