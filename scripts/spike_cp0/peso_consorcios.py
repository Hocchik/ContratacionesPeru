"""Peso de los consorcios en los contratos en soles: % de contratos y % del monto."""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
r = Path(sys.argv[1])
con = pd.read_excel(r / "contratos/2024/CONOSCE_CONTRATOS2024_0.xlsx", dtype=str).drop_duplicates("N_COD_CONTRATO")
cods = set(pd.read_excel(r / "proveedores/2024/CONOSCE_CONSORCIO2024_0.xlsx", dtype=str).RUC_CONSORCIO)
pen = con[con.MONEDA.isin(["Soles", "Nuevos Soles"])].assign(m=lambda d: pd.to_numeric(d.MONTO_CONTRATADO_TOTAL))
es = pen.RUC_CONTRATISTA.isin(cods)
print(f"contratos en soles: {len(pen):,} | de consorcio: {es.mean():.1%} de los contratos y {pen.m[es].sum() / pen.m.sum():.1%} del monto")
