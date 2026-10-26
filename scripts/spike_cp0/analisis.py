"""Preguntas de CP-0 sobre los archivos OECE 2024. Solo imprime conteos (sin nombres de personas)."""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(sys.argv[1])
RUC_RE = r"(10|15|17|20)\d{9}"

con = pd.read_excel(RAIZ / "contratos/2024/CONOSCE_CONTRATOS2024_0.xlsx", dtype=str)
prov = pd.read_excel(RAIZ / "proveedores/2024/CONOSCE_PROVEEDORES2024_0.xlsx", dtype=str)
cons = pd.read_excel(RAIZ / "proveedores/2024/CONOSCE_CONSORCIO2024_0.xlsx", dtype=str)
ent = pd.read_csv(RAIZ / "entidades/entidades_contratantes.csv", dtype=str, sep="|", encoding="latin-1")
for df in (con, prov, cons, ent):
    df.columns = [c.strip() for c in df.columns]
    for c in df.columns:
        df[c] = df[c].str.strip()


def titulo(t: str) -> None:
    print(f"\n=== {t}")


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


titulo("CONTRATOS: grano y clave")
print("filas:", len(con))
print("N_COD_CONTRATO == CODIGO_CONTRATO en todas las filas:", (con.N_COD_CONTRATO == con.CODIGO_CONTRATO).all())
print("contratos distintos (N_COD_CONTRATO):", con.N_COD_CONTRATO.nunique())
for clave in (["N_COD_CONTRATO"], ["N_COD_CONTRATO", "NUM_ITEM"], ["CODIGOCONVOCATORIA", "N_COD_CONTRATO", "NUM_ITEM"]):
    dup = con.duplicated(clave, keep=False).sum()
    print(f"clave {clave}: filas en grupos repetidos = {dup}")
filas_por_contrato = con.groupby("N_COD_CONTRATO").size()
print("filas por contrato:", filas_por_contrato.value_counts().sort_index().head(8).to_dict(), "máx:", filas_por_contrato.max())

titulo("CONTRATOS: ¿qué es constante dentro de un contrato?")
for c in ["CODIGOENTIDAD", "CODIGOCONVOCATORIA", "RUC_CONTRATISTA", "MONEDA", "FECHA_SUSCRIPCION_CONTRATO",
          "MONTO_CONTRATADO_TOTAL", "MONTO_ADICIONAL", "MONTO_REDUCCION", "URLCONTRATO"]:
    varia = (con.groupby("N_COD_CONTRATO")[c].nunique() > 1).sum()
    print(f"{c}: contratos con más de un valor = {varia}")

titulo("CONTRATOS: ¿TOTAL = suma de ITEM?")
g = con.assign(total=num(con.MONTO_CONTRATADO_TOTAL), item=num(con.MONTO_CONTRATADO_ITEM)).groupby("N_COD_CONTRATO")
comp = pd.DataFrame({"total": g.total.max(), "suma_items": g.item.sum(), "n": g.size()})
comp["dif"] = (comp.total - comp.suma_items).abs()
print("contratos con 1 fila e ITEM != TOTAL:", ((comp.n == 1) & (comp.dif > 0.01)).sum())
print("contratos con >1 fila: ", (comp.n > 1).sum(), "| de ellos TOTAL = suma ITEM (±0.01):", ((comp.n > 1) & (comp.dif <= 0.01)).sum())
print("suma de TOTAL por fila (doble conteo):", f"{num(con.MONTO_CONTRATADO_TOTAL).sum():,.0f}")
print("suma de TOTAL por contrato:            ", f"{comp.total.sum():,.0f}")
print("suma de ITEM por fila:                 ", f"{num(con.MONTO_CONTRATADO_ITEM).sum():,.0f}")
mal = comp[(comp.n > 1) & (comp.dif > 0.01)].head(3)
print("ejemplos donde no cuadra (total, suma_items, n):", mal[["total", "suma_items", "n"]].round(2).values.tolist())

titulo("CONTRATOS: duplicados")
print("filas duplicadas exactas:", con.duplicated().sum())
sin_url = con.drop(columns=["URLCONTRATO"])
print("filas duplicadas ignorando URL:", sin_url.duplicated().sum())
print("NUM_CONTRATO (texto) compartido por más de un N_COD_CONTRATO:",
      (con.groupby("NUM_CONTRATO").N_COD_CONTRATO.nunique() > 1).sum())

titulo("CONTRATOS: año de suscripción (por contrato)")
porc = con.drop_duplicates("N_COD_CONTRATO")
print(porc.FECHA_SUSCRIPCION_CONTRATO.str[:4].value_counts().sort_index().to_dict())
print("año de publicación (por contrato):", porc.FECHA_PUBLICACION_CONTRATO.str[:4].value_counts().sort_index().to_dict())
print("contratos suscritos en 2024 por mes:", porc[porc.FECHA_SUSCRIPCION_CONTRATO.str[:4] == "2024"]
      .FECHA_SUSCRIPCION_CONTRATO.str[5:7].value_counts().sort_index().to_dict())

titulo("CONTRATOS: monedas (por contrato)")
print(porc.MONEDA.value_counts().to_dict())

titulo("CONTRATOS: RUC_CONTRATISTA (por contrato)")
r = porc.RUC_CONTRATISTA
print("largo:", r.str.len().value_counts().sort_index().to_dict())
print("formato RUC válido:", r.str.fullmatch(RUC_RE).sum(), "de", len(r))
codigos_consorcio = set(cons.RUC_CONSORCIO)
es_cod_cons = r.isin(codigos_consorcio)
print("coinciden con RUC_CONSORCIO del archivo de consorcios:", es_cod_cons.sum())
no_valido = r[~r.str.fullmatch(RUC_RE)]
print("no válidos que NO son código de consorcio:", (~no_valido.isin(codigos_consorcio)).sum(),
      "| largos:", no_valido[~no_valido.isin(codigos_consorcio)].str.len().value_counts().to_dict())
print("11 dígitos con prefijo no válido:", no_valido[no_valido.str.len() == 11].str[:2].value_counts().to_dict())
print("RUC válidos que están en PROVEEDORES:", r[r.str.fullmatch(RUC_RE)].isin(set(prov["RUC PROVEEDOR"])).mean().round(3))

titulo("CONTRATOS: RUC_DESTINATARIO_PAGO en contratos de consorcio")
pc = porc[es_cod_cons]
print("contratos de consorcio:", len(pc))
print("destinatario == contratista:", (pc.RUC_DESTINATARIO_PAGO == pc.RUC_CONTRATISTA).sum())
print("destinatario con formato RUC válido:", pc.RUC_DESTINATARIO_PAGO.str.fullmatch(RUC_RE).sum(), "| prefijos:",
      pc.RUC_DESTINATARIO_PAGO.str[:2].value_counts().to_dict())
miembros = cons.groupby("RUC_CONSORCIO").RUC_MIEMBRO.apply(set)
es_miembro = [d in miembros.get(c, set()) for c, d in zip(pc.RUC_CONTRATISTA, pc.RUC_DESTINATARIO_PAGO)]
print("destinatario es uno de los miembros del consorcio:", sum(es_miembro))
pnc = porc[~es_cod_cons]
print("contratos NO consorcio con destinatario distinto del contratista:", (pnc.RUC_DESTINATARIO_PAGO != pnc.RUC_CONTRATISTA).sum())

titulo("CONTRATOS: montos")
t = num(porc.MONTO_CONTRATADO_TOTAL)
print("TOTAL <= 0:", (t <= 0).sum(), "| percentiles:", t.quantile([0.5, 0.9, 0.99, 0.999]).round(0).to_dict())
top = porc.assign(t=t).nlargest(3, "t")
print("3 mayores (monto, moneda, descripción recortada):",
      [(f"{m:,.0f}", mo, d[:60]) for m, mo, d in zip(top.t, top.MONEDA, top.DESCRIPCION_PROCESO)])
print("contratos con MONTO_ADICIONAL > 0:", (num(porc.MONTO_ADICIONAL) > 0).sum(),
      "| con MONTO_REDUCCION > 0:", (num(porc.MONTO_REDUCCION) > 0).sum())

titulo("CONTRATOS: entidad")
cod = porc.CODIGOENTIDAD
print("largo de CODIGOENTIDAD:", cod.str.len().value_counts().to_dict(), "| entidades distintas:", cod.nunique())
consu = set(ent.CODCONSUCODE)
consu_pad = {c.zfill(6) for c in ent.CODCONSUCODE}
siaf_pad = {c.zfill(6) for c in ent.CODIGO_SIAF.dropna()}
print("CODIGOENTIDAD en CODCONSUCODE tal cual:", cod.isin(consu).mean().round(3))
print("CODIGOENTIDAD en CODCONSUCODE con ceros a la izquierda (6):", cod.isin(consu_pad).mean().round(3))
print("CODIGOENTIDAD sin ceros en CODCONSUCODE:", cod.str.lstrip("0").isin(consu).mean().round(3))
print("CODIGOENTIDAD en CODIGO_SIAF con ceros (6):", cod.isin(siaf_pad).mean().round(3))

titulo("CONTRATOS: texto")
textos = con.select_dtypes(["object", "str"])
print("celdas con carácter de reemplazo U+FFFD:", int(textos.apply(lambda s: s.str.contains("�", na=False)).sum().sum()))
print("TIENERESOLUCION:", con.TIENERESOLUCION.value_counts(dropna=False).to_dict())

titulo("PROVEEDORES")
print("filas:", len(prov), "| RUC distintos:", prov["RUC PROVEEDOR"].nunique())
print("(RUC, REGISTRO) único:", not prov.duplicated(["RUC PROVEEDOR", "REGISTRO"]).any())
print("REGISTRO:", prov.REGISTRO.value_counts().to_dict())
print("registros por RUC:", prov.groupby("RUC PROVEEDOR").size().value_counts().sort_index().to_dict())
print("RUC con más de un nombre:", (prov.groupby("RUC PROVEEDOR").PROVEEDOR.nunique() > 1).sum())
print("prefijos RUC:", prov["RUC PROVEEDOR"].str[:2].value_counts().to_dict())
print("ORIGEN != PERU:", (prov.ORIGEN != "PERU").sum())

titulo("CONSORCIOS")
print("filas:", len(cons), "| (RUC_CONSORCIO, RUC_MIEMBRO) único:", not cons.duplicated(["RUC_CONSORCIO", "RUC_MIEMBRO"]).any())
print("largo RUC_CONSORCIO:", cons.RUC_CONSORCIO.str.len().value_counts().sort_index().to_dict())
print("miembros por consorcio:", cons.groupby("RUC_CONSORCIO").size().value_counts().sort_index().to_dict())
print("RUC_CONSORCIO con más de un nombre:", (cons.groupby("RUC_CONSORCIO").CONSORCIO.nunique() > 1).sum())
print("columnas:", list(cons.columns))

titulo("ENTIDADES")
print("ESTADO:", ent.ESTADO.value_counts().to_dict())
print("columnas:", list(ent.columns))
