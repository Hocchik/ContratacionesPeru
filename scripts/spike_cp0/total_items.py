"""¿TOTAL = suma de ítems distintos? y bytes cp1252 en el CSV de entidades."""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(sys.argv[1])
con = pd.read_excel(RAIZ / "contratos/2024/CONOSCE_CONTRATOS2024_0.xlsx", dtype=str)

items = con.drop_duplicates(["N_COD_CONTRATO", "NUM_ITEM"])
g = items.assign(item=pd.to_numeric(items.MONTO_CONTRATADO_ITEM), total=pd.to_numeric(items.MONTO_CONTRATADO_TOTAL)).groupby("N_COD_CONTRATO")
comp = pd.DataFrame({"total": g.total.max(), "suma": g.item.sum(), "n_items": g.size()})
cuadra = (comp.total - comp.suma).abs() <= 0.01
print("contratos:", len(comp), "| TOTAL = suma de ítems distintos:", int(cuadra.sum()), f"({cuadra.mean():.1%})")
print("no cuadran: TOTAL > suma:", int((comp.total - comp.suma > 0.01).sum()), "| TOTAL < suma:", int((comp.suma - comp.total > 0.01).sum()))
print("ítems por contrato:", comp.n_items.value_counts().sort_index().head(6).to_dict())
falt = comp[~cuadra]
print("de los que no cuadran, % del TOTAL cubierto por los ítems presentes (mediana):", f"{(falt.suma / falt.total).median():.1%}")

crudo = (RAIZ / "entidades/entidades_contratantes.csv").read_bytes()
altos = sorted({b for b in crudo if b >= 0x80})
print("\nCSV entidades: bytes >= 0x80 presentes:", [hex(b) for b in altos])
print("hay bytes 0x80-0x9F (solo existen como letras en cp1252, no en latin-1):", any(0x80 <= b <= 0x9F for b in altos))
try:
    crudo.decode("utf-8")
    print("decodifica como UTF-8: sí")
except UnicodeDecodeError as e:
    print("decodifica como UTF-8: no ->", e.reason)
