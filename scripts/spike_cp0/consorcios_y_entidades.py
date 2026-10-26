"""Verifica con datos lo que dicen los diccionarios: códigos de consorcio, resoluciones y nombres de entidad."""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
R = Path(sys.argv[1])
con = pd.read_excel(R / "contratos/2024/CONOSCE_CONTRATOS2024_0.xlsx", dtype=str)
cons = pd.read_excel(R / "proveedores/2024/CONOSCE_CONSORCIO2024_0.xlsx", dtype=str)
ent = pd.read_csv(R / "entidades/entidades_contratantes.csv", dtype=str, sep="|", encoding="latin-1")
porc = con.drop_duplicates("N_COD_CONTRATO")
codigos = set(cons.RUC_CONSORCIO)

print("=== ¿El código de consorcio es uno por procedimiento?")
pc = porc[porc.RUC_CONTRATISTA.isin(codigos)]
conv_por_codigo = pc.groupby("RUC_CONTRATISTA").CODIGOCONVOCATORIA.nunique()
print("códigos de consorcio en contratos:", len(conv_por_codigo), "| con más de una convocatoria:", int((conv_por_codigo > 1).sum()))
miembros = cons.groupby("RUC_CONSORCIO").RUC_MIEMBRO.apply(lambda s: tuple(sorted(s)))
codigos_por_grupo = miembros.reset_index().groupby("RUC_MIEMBRO").RUC_CONSORCIO.nunique()
print("grupos de miembros distintos:", len(codigos_por_grupo), "| códigos:", len(miembros))
print("grupos con más de un código:", int((codigos_por_grupo > 1).sum()), "| máx. códigos por grupo:", int(codigos_por_grupo.max()))

pc = pc.assign(grupo=pc.RUC_CONTRATISTA.map(miembros), m=pd.to_numeric(pc.MONTO_CONTRATADO_TOTAL))
por_entidad = pc.groupby(["CODIGOENTIDAD", "grupo"]).RUC_CONTRATISTA.nunique()
print("pares (entidad, mismo grupo de miembros) con más de un código:", int((por_entidad > 1).sum()),
      "| contratos afectados:", int(pc.set_index(["CODIGOENTIDAD", "grupo"]).index.isin(por_entidad[por_entidad > 1].index).sum()))

print("\n=== TIENERESOLUCION (resolución y/o nulidad), por contrato")
print(porc.TIENERESOLUCION.fillna("(vacío)").value_counts().to_dict())

print("\n=== Nombre de entidad: ¿se puede inferir el nivel de gobierno? (evidencia, no regla)")
nombre = ent.NOMBRE_DE_ENTIDAD.str.upper()
patrones = {
    "MUNICIPALIDAD": nombre.str.startswith("MUNICIPALIDAD"),
    "GOBIERNO REGIONAL": nombre.str.contains("GOBIERNO REGIONAL", regex=False),
    "MINISTERIO": nombre.str.startswith("MINISTERIO"),
}
for k, v in patrones.items():
    print(f"{k}: {int(v.sum())} entidades")
cualquiera = pd.concat(patrones.values(), axis=1).any(axis=1)
print("ninguno de los 3 patrones:", int((~cualquiera).sum()), "de", len(ent))
cod_ent = ent.assign(cod=ent.CODCONSUCODE.str.zfill(6), patron=cualquiera)
pe = porc.merge(cod_ent[["cod", "patron"]], left_on="CODIGOENTIDAD", right_on="cod", how="left")
print("contratos de entidades con alguno de los 3 patrones:", f"{pe.patron.mean():.1%}")
print("ejemplos sin patrón:", nombre[~cualquiera].sample(5, random_state=1).str[:50].tolist())
