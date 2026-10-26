# Fichas de datos — Contrataciones Perú

Todo lo que dice este documento sale de los archivos reales, perfilados con
`.claude/skills/perfilar-dataset/perfilar.py` y con conteos hechos a mano
(CP-0, 26 de octubre de 2026). Lo que no se pudo comprobar con los archivos
está marcado como **por verificar**.

Archivos perfilados (todos los descargó el usuario del Portal de Datos Abiertos
del OECE; la fecha es la de modificación del archivo en disco):

| Archivo | Ruta en `data/raw/oece/` | Filas | Fecha | SHA-256 |
| --- | --- | --- | --- | --- |
| `CONOSCE_CONTRATOS2024_0.xlsx` | `contratos/2024/` | 11,228 | 2026-10-26 | `d00a124e…d096` |
| `CONOSCE_PROVEEDORES2024_0.xlsx` | `proveedores/2024/` | 45,294 | 2026-10-26 | `ec72229e…55ac` |
| `CONOSCE_CONSORCIO2024_0.xlsx` | `proveedores/2024/` | 27,542 | 2026-10-26 | `1272e9e5…0d9a` |
| `entidades_contratantes.csv` | `entidades/` | 3,366 | 2026-10-26 | `07fea1d5…4cbc` |

Los tres `.xlsx` tienen una sola hoja (`Sheet1`), encabezado en la fila 1 y
texto sin caracteres dañados (0 celdas con U+FFFD).

---

## Contratos

- **Fuente y URL:** Portal de Datos Abiertos del OECE (CONOSCE),
  <https://bi.seace.gob.pe/pentaho/api/repos/:public:portal:datosabiertos.html/content?userid=public&password=key>,
  página "Contratos" (portal actualizado al 30 de setiembre de 2026).
  Descarga:
  <https://conosce.osce.gob.pe/buscador/assets/67ae6c4a/reportes/contratos/2024/CONOSCE_CONTRATOS2024_0.xlsx>
- **Archivo y fecha de descarga:** `CONOSCE_CONTRATOS2024_0.xlsx`, 2026-10-26.
  2.4 MB, 24 columnas.
- **Grano (1 fila = …):** **contrato × ítem × registro de modificación.** Hay
  7,477 contratos, 7,828 pares contrato-ítem y 11,228 filas.
  - El 97.3% de los contratos tiene un solo ítem; el máximo es 50.
  - Cuando un contrato tiene adicionales, reducciones o prórrogas, el par
    (contrato, ítem) se repite una vez por cada modificación. 1,744 pares
    tienen entre 2 y 50 filas. Entre esas filas **solo cambian**
    `MONTO_ADICIONAL`, `MONTO_REDUCCION` y `MONTO_PRORROGA`; las otras 19
    columnas son idénticas. Comprobado con conteos y revisando 3 grupos.
  - No hay una columna que identifique cada modificación (ni número ni fecha).
- **Clave natural:**
  - `N_COD_CONTRATO` a nivel contrato: es única después de quedarse con una
    fila por contrato (7,477). Todas las columnas de contrato son constantes
    dentro de cada `N_COD_CONTRATO`: entidad, convocatoria, contratista,
    fecha de suscripción, monto total y URL. La única excepción es la moneda,
    ver Limitaciones.
  - A nivel fila no hay clave única: `(N_COD_CONTRATO, NUM_ITEM)` se repite
    en 5,144 filas por las modificaciones.
  - `CODIGO_CONTRATO` es igual a `N_COD_CONTRATO` en las 11,228 filas.
  - `NUM_CONTRATO` (el número del documento) **no sirve como clave**: 79 veces
    se repite dentro de una misma entidad para contratos distintos.
- **Columnas usadas:**

  | Significado | Nombre real | Tipo esperado | % nulos |
  | --- | --- | --- | --- |
  | Clave del contrato | `N_COD_CONTRATO` | texto (dígitos) | 0.0% |
  | Ítem | `NUM_ITEM` | entero | 0.0% |
  | Entidad | `CODIGOENTIDAD` | texto, 6 dígitos con ceros a la izquierda | 0.0% |
  | Procedimiento (convocatoria) | `CODIGOCONVOCATORIA` | texto (dígitos) | 0.0% |
  | Descripción del proceso | `DESCRIPCION_PROCESO` | texto libre | 0.0% |
  | Monto original del contrato | `MONTO_CONTRATADO_TOTAL` | numérico | 0.0% |
  | Monto del ítem | `MONTO_CONTRATADO_ITEM` | numérico | 0.0% |
  | Moneda | `MONEDA` | texto (etiqueta, no código ISO) | 0.0% |
  | Proveedor | `RUC_CONTRATISTA` | texto: RUC o código de consorcio | 0.0% |
  | Quién cobra | `RUC_DESTINATARIO_PAGO` | texto (RUC) | 0.0% |
  | Fecha de suscripción | `FECHA_SUSCRIPCION_CONTRATO` | fecha `AAAA-MM-DD` | 0.0% |
  | Fecha de publicación | `FECHA_PUBLICACION_CONTRATO` | fecha `AAAA-MM-DD` | 0.0% |
  | Modificaciones (roadmap R2) | `MONTO_ADICIONAL`, `MONTO_REDUCCION`, `MONTO_PRORROGA` | numérico | 0.0% |

  No se usan:
  - `CODIGO_CONTRATO`: es igual a `N_COD_CONTRATO`.
  - `NUM_CONTRATO`.
  - `MONTO_COMPLEMENTARIO`: siempre vale 0.
  - `TIENERESOLUCION`: `SI` en 174 filas y nulo en el resto.
  - `URLCONTRATO`.
  - `ESPUBLICADO`: siempre vale 1.
  - `FECHA_VIGENCIA_INICIAL`, `FECHA_VIGENCIA_FINAL` y
    `FECHA_VIGENCIA_FIN_ACTUALIZADA`.
- **Calidad (por contrato, salvo que se diga otra cosa):**
  - **Montos:** `MONTO_CONTRATADO_TOTAL` ≤ 0 en 0 contratos. En la moneda de
    cada contrato, sin convertir: mediana 395,881, percentil 99.9 de 308
    millones y máximo de 806 millones (una obra, en soles).
  - **Monto total vs. ítems:** `MONTO_CONTRATADO_TOTAL` es la suma de los
    ítems distintos en 7,476 de 7,477 contratos. La excepción es
    `2304992`: solo trae el ítem 6, que cubre el 33% del total.
  - **Monedas:** `Soles` 7,349, `Nuevos Soles` 45, `Dólar Norteamericano` 78
    y `Euro` 5. En total, 98.9% en soles.
  - **`RUC_CONTRATISTA`:**
    - 4,748 contratos (63.5%) tienen un RUC válido (11 dígitos con prefijo 10,
      15, 17 o 20), y el 99.9% de esos RUC está en el archivo de Proveedores.
    - 2,655 (35.5%) son códigos de consorcio de 6–7 dígitos. Ver Consorcios.
    - 74 (1.0%) son otros identificadores: 70 empiezan con `L0` y no están en
      Proveedores; 4 empiezan con `99` y en Proveedores figuran como
      proveedores de España o Guatemala.
  - **Fechas de suscripción:** 100% en `AAAA-MM-DD`, de 2023-08-14 a
    2025-12-15.
  - **Duplicados:** 0 filas duplicadas exactas. Las repeticiones de
    (contrato, ítem) son modificaciones, no duplicados.
- **Limitaciones encontradas:**
  1. **No trae tipo de procedimiento ni objeto contractual** (bien, servicio,
     obra o consultoría). Tampoco trae el nombre de la entidad ni el del
     proveedor: salen de los otros archivos.
  2. **Sumar por fila infla los montos.**
     - `MONTO_CONTRATADO_TOTAL` sumado por fila da 70,366 millones; sumado
       una vez por contrato da 22,548 millones, 3.1 veces menos.
     - `MONTO_CONTRATADO_ITEM` sumado por fila da 66,537 millones.
     - Regla para staging: tomar `MONTO_CONTRATADO_TOTAL` una vez por
       `N_COD_CONTRATO`.
  3. **El año del archivo no es el año de suscripción.** Por contrato, el
     archivo "2024" trae suscripciones de 2023 (4), 2024 (6,247) y 2025
     (1,226), y publicaciones hasta 2026-03-16. Además, enero de 2024 tiene
     solo 3 contratos y febrero 109, contra 500–900 por mes desde abril.
  4. **La moneda se escribe de dos formas para la misma divisa:** `Soles` y
     `Nuevos Soles`. Dos contratos (`2242294` y `2296722`) mezclan las dos
     etiquetas entre sus ítems; normalizando a PEN quedan con una sola
     moneda.
- **Por verificar:**
  - Qué define el año del archivo y si para completar las suscripciones de
    2024 hacen falta los archivos de 2023 y 2025. El portal dice que "entre
    la adjudicación y la suscripción del contrato transcurre un tiempo", lo
    que apunta al año de la convocatoria o de la adjudicación.
  - Si 7,477 contratos son todos los de 2024. **No hay más partes
    publicadas:** el portal enlaza un solo archivo por año (`_0`), de 2018 a
    2026. No se comprobó si el servidor guarda partes sin enlazar.
  - Si un mismo contrato aparece en archivos de años distintos. Hace falta
    otro año para comprobarlo.
  - Qué son los identificadores `L0…`.
  - Qué mide exactamente `MONTO_ADICIONAL`. En la primera fila de 5,150
    contratos (69%) vale más de 0, lo que parece demasiado para adicionales
    en sentido legal.
  - Si `CODIGOCONVOCATORIA` permite unir con "Datos de la Convocatoria" o
    "Datos de la Adjudicación", y si esos archivos traen el tipo de
    procedimiento y el objeto contractual. Ver "Revisión del portal".
  - Licencia de uso del portal.

---

## Proveedores

- **Fuente y URL:** Portal de Datos Abiertos del OECE (CONOSCE), página
  "Proveedores y Consorcios", botón "Individual". Descarga:
  <https://conosce.osce.gob.pe/buscador/assets/67ae6c4a/reportes/proveedores/2024/CONOSCE_PROVEEDORES2024_0.xlsx>
- **Archivo y fecha de descarga:** `CONOSCE_PROVEEDORES2024_0.xlsx`,
  2026-10-26. 2.3 MB, 9 columnas.
- **Grano (1 fila = …):** proveedor × tipo de registro en el RNP. Hay 45,294
  filas y 20,327 RUC. Registros por RUC: 1 (1,842), 2 (13,974), 3 (2,540) y
  4 (1,971).
- **Clave natural:** `(RUC PROVEEDOR, REGISTRO)`. Única: sí, verificada con
  conteo. Cada RUC tiene un solo nombre (0 RUC con más de un `PROVEEDOR`).
- **Columnas usadas:**

  | Significado | Nombre real | Tipo esperado | % nulos |
  | --- | --- | --- | --- |
  | RUC del proveedor | `RUC PROVEEDOR` (con espacio) | texto, 11 caracteres | 0.0% |
  | Razón social | `PROVEEDOR` | texto | 0.0% |
  | País de origen | `ORIGEN` | texto | 0.0% |
  | Ubicación | `DEPARTAMENTO`, `PROVINCIA`, `DISTRITO` | texto | 0.0% |
  | Tipo de registro RNP | `REGISTRO` | texto, 4 valores | 0.0% |

  No se usan: `D_FEC_INICIOVIGENCIA` ni `D_FEC_FINVIGENCIA`. Este último trae
  `2079-06-06`, que parece un valor de "sin vencimiento".
- **Calidad:**
  - `REGISTRO`: `Proveedor de Servicios` 20,054, `Proveedor de Bienes`
    18,553, `Ejecutor de Obras` 3,719 y `Consultor de Obras` 2,968.
  - RUC con formato válido: 99.9%. Prefijos: `20` 32,544, `10` 12,576, `15`
    93, `17` 43 y `99` 38.
  - `ORIGEN` distinto de `PERU`: 185 filas.
  - Duplicados exactos: 0.
- **Limitaciones encontradas:**
  - No marca qué proveedores son consorcios; los consorcios están en su
    propio archivo.
  - El RUC con prefijo `10` es de persona natural, así que el nombre es el
    de una persona: no mostrarlo fuera del dashboard sin necesidad.
- **Por verificar:** si el año del archivo es el del procedimiento
  adjudicado, y si sirve para contratos de otros años. El portal lo describe
  como "proveedores que han adjudicado procedimientos, a nivel de ítem".

---

## Consorcios

- **Fuente y URL:** Portal de Datos Abiertos del OECE (CONOSCE), página
  "Proveedores y Consorcios", botón "Consorcio". Descarga:
  <https://conosce.osce.gob.pe/buscador/assets/67ae6c4a/reportes/consorcios/2024/CONOSCE_CONSORCIO2024_0.xlsx>
- **Archivo y fecha de descarga:** `CONOSCE_CONSORCIO2024_0.xlsx`, 2026-10-26.
  1.2 MB, 5 columnas.
- **Grano (1 fila = …):** consorcio × miembro. Hay 27,542 filas y 13,408
  consorcios. Miembros por consorcio: 2 (12,752), 3 (611), 4 (31) y hasta 9.
- **Clave natural:** `(RUC_CONSORCIO, RUC_MIEMBRO)`. Única: sí, verificada con
  conteo.
- **Columnas usadas:**

  | Significado | Nombre real | Tipo esperado | % nulos |
  | --- | --- | --- | --- |
  | Año | `AÑO` | entero (solo `2024`) | 0.0% |
  | Código del consorcio | `RUC_CONSORCIO` | texto, 6–7 dígitos (**no es un RUC**) | 0.0% |
  | Nombre del consorcio | `CONSORCIO` | texto | 0.0% |
  | RUC del miembro | `RUC_MIEMBRO` | texto, 11 caracteres | 0.0% |
  | Nombre del miembro | `MIEMBRO` | texto | 0.0% |

- **Calidad:**
  - `RUC_MIEMBRO` con formato válido: 99.5%.
  - **El 100% de los códigos de consorcio que aparecen en Contratos (2,655)
    está en este archivo.**
  - El nombre no identifica al consorcio: hay 9,703 nombres para 13,408
    códigos. Por ejemplo, varios consorcios distintos se llaman igual.
  - Duplicados exactos: 0.
- **Limitaciones encontradas:**
  - **No trae el % de participación de cada miembro.** Con este archivo no
    se puede repartir el monto de un consorcio entre sus integrantes, y eso
    confirma la limitación del plan.
  - **Los consorcios pesan mucho:** son el 35.8% de los contratos en soles,
    pero el **70.2% del monto**.
  - En los contratos de consorcio, `RUC_DESTINATARIO_PAGO` nunca es el código
    del consorcio. En 1,635 de 2,655 (62%) es el RUC de un miembro; en el
    resto es otro RUC.
- **Por verificar:**
  - Si el RUC de pago que no es de un miembro es el RUC propio del
    consorcio. Los consorcios con contabilidad independiente tienen RUC.
  - Si el archivo de otro año trae los mismos códigos.

---

## Entidades Contratantes

- **Fuente y URL:** Portal de Datos Abiertos del OECE (CONOSCE), página
  "Entidades Contratantes" (listado del SEACE v3.0). Descarga:
  <https://conosce.osce.gob.pe/buscador/assets/67ae6c4a/reportes/entidadescontratantes/entidades_contratantes.csv>
- **Archivo y fecha de descarga:** `entidades_contratantes.csv`, 2026-10-26.
  0.4 MB.
  - Separado por `|`. Hay que indicarlo: el detector automático de pandas se
    equivoca.
  - Codificación latin-1, salvo una Ñ guardada en cp850 que se lee como
    `¥` (`MUNICIPALIDAD DISTRITAL DE LEONOR ORDO¥EZ`).
  - Es una foto del padrón actual, no un archivo por año. Por eso está en
    `entidades/` y no en `entidades/2024/`.
- **Grano (1 fila = …):** entidad. Hay 3,366 filas.
- **Clave natural:** `CODCONSUCODE`. Única: sí, verificada con conteo. `RUC`
  también es único.
- **Unión con Contratos:** `CODIGOENTIDAD` = `CODCONSUCODE` con ceros a la
  izquierda hasta 6 dígitos. Une el **100%** de los contratos (1,401
  entidades). Sin el relleno de ceros solo une el 21.5%.
- **Columnas usadas:**

  | Significado | Nombre real | Tipo esperado | % nulos |
  | --- | --- | --- | --- |
  | Código de la entidad | `CODCONSUCODE` | texto (dígitos, sin ceros a la izquierda) | 0.0% |
  | RUC de la entidad | `RUC` | texto, 11 dígitos | 0.0% |
  | Nombre | `NOMBRE_DE_ENTIDAD` | texto | 0.0% |
  | Ubicación | `DEPARTAMENTO`, `PROVINCIA`, `DISTRITO` | texto | 0.0% |
  | Código presupuestal | `CODIGO_SIAF` | texto | 10.4% |
  | Estado | `ESTADO` | `Activo` / `Inactivo` | 0.0% |

  No se usa `ULTIMAACTUALIZACION`, que trae fechas `DD/MM/AA` con año de 2
  dígitos.
- **Calidad:**
  - `ESTADO`: `Activo` 3,259 e `Inactivo` 107.
  - RUC válido: 100%.
  - Duplicados exactos: 0.
- **Limitaciones encontradas:**
  - **No trae nivel de gobierno, sector ni tipo de entidad.**
  - La región se puede tomar de `DEPARTAMENTO`: 25 valores distintos.
- **Por verificar:**
  - Si `CODIGO_SIAF` permite traer el nivel de gobierno de otra fuente,
    como la clasificación presupuestal del MEF.
  - Si el padrón incluye entidades que ya no existen pero tienen contratos
    en años anteriores.

---

## Revisión del portal (26 de octubre de 2026)

Se revisó en el navegador, **sin descargar nada**, el portal actualizado al
30 de setiembre de 2026. Las páginas del portal no muestran columnas; solo
describen cada dataset y enlazan sus archivos.

**Datasets publicados.** Cada uno se elige con el parámetro `pagina=` de
`…:portal:dataset.html/content`:

| Dataset | `pagina=` | ¿Sirve para alguna contradicción? |
| --- | --- | --- |
| Plan Anual de Contrataciones | `pac` | No se sabe: su descripción no menciona nivel de gobierno |
| **Datos de la Convocatoria** | `convocatorias` | **Candidato para tipo de procedimiento y objeto** |
| Miembros de Comité | `comite` | No |
| Procesos con nulidad | `nulos` | No (roadmap R3) |
| Procesos desiertos | `desiertos` | No (roadmap R3) |
| **Datos de la Adjudicación** | `adjudicaciones` | Candidato: "datos del proveedor adjudicado, valor adjudicado, cantidad" |
| Listado de Ofertantes | `postores` | No en v1 |
| Proveedores y Consorcios | `proveedores` | Ya perfilado |
| **Contrataciones Directas** | `directa` | **Marca la contratación directa** |
| Contratos | `contratos` | Ya perfilado |
| Arbitraje | `arbitraje` | No |
| Órdenes de Compra y/o Servicios | `ordenes` | Fuera del proyecto |
| Ampliaciones de Contrato | `ampliaciones` | Roadmap R2 |
| Cuaderno de incidencias de obras | `cio` | No |
| Entidades Contratantes | `entidades` | Ya perfilado; un solo CSV |

También hay datos complementarios: SICAN, Pronunciamientos, Opiniones
Normativas, Conformación Jurídica del RNP y Sanciones.

**Archivos relevantes para 2024.** Todos bajo
`https://conosce.osce.gob.pe/buscador/assets/67ae6c4a/reportes/`:

| Archivo | Qué contiene, según el portal |
| --- | --- |
| `convocatorias/2024/CONOSCE_CONVOCATORIAS2024_0.xlsx` | Convocatorias de "todos los procesos" adjudicados |
| `convocatorias/2024/CONOSCE_CONVOCATORIAS_CD2024_0.xlsx` | Solo contratación directa |
| `convocatorias/2024/CONOSCE_CONVOCATORIAS_SIE2024_0.xlsx` | Solo subasta inversa electrónica |
| `adjudicaciones/2024/CONOSCE_ADJUDICACIONES2024_0.xlsx` | Adjudicaciones de todos los procesos |
| `adjudicaciones/2024/CONOSCE_ADJUDICACIONES_CD2024_0.xlsx` | "Procesos adjudicados de contratación directa" (página `directa`) |

**Lo que se puede afirmar:**
- **Partes de Contratos 2024:** el portal enlaza un solo archivo por año,
  `CONOSCE_CONTRATOS<año>_0.xlsx`, de 2018 a 2026. No hay `_1` ni `_2`
  publicados. Lo mismo pasa con convocatorias y adjudicaciones.
- **Tipo de procedimiento y objeto:** que el portal separe archivos "solo
  contratación directa" (`_CD`) y "solo subasta inversa" (`_SIE`) indica
  que el tipo de procedimiento existe en los datos de convocatoria y
  adjudicación. Qué columna lo trae, si también viene el objeto contractual
  y si se une por `CODIGOCONVOCATORIA` está **por verificar**.
- **Nivel de gobierno:** ninguna descripción del portal lo menciona
  (también se buscaron "gobierno", "sector" y "objeto"). La página de
  Entidades solo dice que el listado cubre a las entidades del artículo 3
  del TUO de la Ley 30225 y de la Ley 32069. **Sin evidencia de que el
  portal lo publique.**

**Lo que no se pudo revisar:** el **diccionario de datos**, el único lugar
donde están las columnas de cada archivo. Está detrás de
`https://tinyurl.com/conoscediccionarioopendata`, y la vista previa de
tinyurl pide una verificación anti-bots que la IA no resuelve.

---

## Decisión de fuente: portal OECE u OCDS

**Propuesta: portal OECE.** Queda **pendiente de confirmar** con el tech lead
porque los datos contradicen el plan en tres puntos.

Por qué el portal OECE:
- Las piezas centrales están y se unen bien entre sí:
  - Contratos con Entidades: 100%.
  - Contratos con Consorcios: 100% de los códigos.
  - Contratos con Proveedores: 99.9% de los RUC válidos.
- La clave del contrato es estable y el monto total cuadra con la suma de
  sus ítems en el 99.99% de los casos.
- Trae los montos de las modificaciones, que el plan esperaba de un segundo
  dataset (roadmap R2).

Contradicciones con el plan:

| # | El plan supone | Los datos muestran | Qué afecta | Posible solución en el portal |
| --- | --- | --- | --- | --- |
| 1 | Hay tipo de procedimiento y objeto contractual | Ninguno de los 4 archivos los trae | `dim_procedimiento`, P2 (contratación directa), la métrica % contratación directa y el filtro por objeto | Probable: `CONOSCE_CONVOCATORIAS2024_0.xlsx`. Columnas y clave de unión por verificar |
| 2 | La entidad trae nivel de gobierno | Entidades no lo trae | `grupo_pares` (nivel de gobierno × tercil), el percentil vs. pares, la clasificación Alta/Media/Baja y la página 3 | No se encontró. Habría que buscar fuera del portal o cambiar el criterio de pares |
| 3 | El archivo de un año = el periodo de análisis | El archivo "2024" mezcla suscripciones de 2023–2025, y enero–marzo de 2024 llegan casi vacíos | Para tener completo un año de suscripción hay que cargar los archivos de años vecinos. La línea de corte 2023–2026 necesita revisarse | Están todos los años de 2018 a 2026, un archivo por año: alcanza con cargar años vecinos |

Otros hallazgos que cambian el diseño pero no lo bloquean:
- **Grano con modificaciones.** El plan ya preveía agregar en staging. La
  regla es tomar `MONTO_CONTRATADO_TOTAL` una vez por contrato.
- **Los códigos de consorcio no son RUC.** El test "RUC válido" daría 36.5%
  de inválidos si no se separan. `dim_proveedor` necesita un tipo de
  identificador (RUC, consorcio u otro).
- **No hace falta el hash de razón social.** El plan lo usaba como clave
  alternativa del proveedor, pero Contratos no trae nombres y
  `RUC_CONTRATISTA` nunca es nulo.
- **Los consorcios son el 70.2% del monto.** La limitación "consorcio = un
  proveedor" pesa más de lo que suponía el plan.
- **Hay contratos en euros** (5): CP-3 tiene que traer también la serie
  PD04648PD.
