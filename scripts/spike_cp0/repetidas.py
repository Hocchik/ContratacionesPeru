"""Mira filas repetidas de (N_COD_CONTRATO, NUM_ITEM) y casos raros. Sin nombres de personas."""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 20)
RAIZ = Path(sys.argv[1])
con = pd.read_excel(RAIZ / "contratos/2024/CONOSCE_CONTRATOS2024_0.xlsx", dtype=str)
prov = pd.read_excel(RAIZ / "proveedores/2024/CONOSCE_PROVEEDORES2024_0.xlsx", dtype=str)

cols = ["N_COD_CONTRATO", "NUM_ITEM", "MONTO_CONTRATADO_TOTAL", "MONTO_CONTRATADO_ITEM", "MONTO_ADICIONAL",
        "MONTO_REDUCCION", "MONTO_PRORROGA", "TIENERESOLUCION", "FECHA_VIGENCIA_FINAL", "FECHA_VIGENCIA_FIN_ACTUALIZADA"]
rep = con[con.duplicated(["N_COD_CONTRATO", "NUM_ITEM"], keep=False)]
print("=== 3 grupos repetidos (N_COD_CONTRATO, NUM_ITEM)")
for c in rep.N_COD_CONTRATO.drop_duplicates().iloc[[0, 10, 50]]:
    print(con.loc[con.N_COD_CONTRATO == c, cols].to_string(index=False), "\n")

print("=== ¿qué columnas cambian entre filas repetidas del mismo (contrato, ítem)?")
g = rep.groupby(["N_COD_CONTRATO", "NUM_ITEM"])
print({c: int((g[c].nunique(dropna=False) > 1).sum()) for c in con.columns if c not in ("N_COD_CONTRATO", "NUM_ITEM")})

print("\n=== repeticiones por (contrato, ítem):", g.size().value_counts().sort_index().to_dict())

print("\n=== contratos con más de una moneda")
multi = con.groupby("N_COD_CONTRATO").MONEDA.nunique()
for c in multi[multi > 1].index:
    print(con.loc[con.N_COD_CONTRATO == c, ["N_COD_CONTRATO", "NUM_ITEM", "MONEDA", "MONTO_CONTRATADO_TOTAL", "MONTO_CONTRATADO_ITEM"]].to_string(index=False))

print("\n=== contrato de 1 fila con ITEM != TOTAL")
una = con.groupby("N_COD_CONTRATO").filter(lambda d: len(d) == 1)
dif = una[pd.to_numeric(una.MONTO_CONTRATADO_TOTAL) != pd.to_numeric(una.MONTO_CONTRATADO_ITEM)]
print(dif[["N_COD_CONTRATO", "NUM_ITEM", "MONTO_CONTRATADO_TOTAL", "MONTO_CONTRATADO_ITEM", "MONEDA"]].to_string(index=False))

print("\n=== RUC_CONTRATISTA con prefijo L0 o 99")
raros = con.drop_duplicates("N_COD_CONTRATO").RUC_CONTRATISTA
raros = raros[raros.str[:2].isin(["L0", "99"])]
print("ejemplos de forma (enmascarados):", sorted({r[:3] + "*" * (len(r) - 3) for r in raros})[:3])
print("están en PROVEEDORES:", raros.isin(set(prov["RUC PROVEEDOR"])).sum(), "de", len(raros))
print("ORIGEN de esos proveedores:", prov[prov["RUC PROVEEDOR"].isin(set(raros))].drop_duplicates("RUC PROVEEDOR").ORIGEN.value_counts().to_dict())

print("\n=== NUM_CONTRATO repetido dentro de la misma entidad")
porc = con.drop_duplicates("N_COD_CONTRATO")
print("grupos (entidad, NUM_CONTRATO) con más de un N_COD_CONTRATO:",
      int((porc.groupby(["CODIGOENTIDAD", "NUM_CONTRATO"]).N_COD_CONTRATO.nunique() > 1).sum()))
