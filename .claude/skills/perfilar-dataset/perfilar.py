"""Perfila un archivo de datos crudo (CSV, XLSX o JSON/JSONL) sin modificarlo.

Uso (desde la raíz del repo):
    python .claude/skills/perfilar-dataset/perfilar.py <ruta_archivo> [--hoja NOMBRE] [--max-filas N]

Imprime un reporte en Markdown: formato, codificación, filas, columnas,
% de nulos, valores de ejemplo, columnas candidatas a clave y chequeos
específicos de contrataciones (RUC, moneda, fechas). Todo se lee como texto
(dtype=str): el perfilado no debe adivinar tipos.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

ENCODINGS = ("utf-8-sig", "utf-8", "latin-1", "cp1252")
RUC_RE = re.compile(r"^(10|15|17|20)\d{9}$")
PISTAS_RUC = ("ruc",)
PISTAS_MONEDA = ("moneda", "currency")
PISTAS_FECHA = ("fecha", "date")
PISTAS_MONTO = ("monto", "amount", "valor", "importe")


def leer(ruta: Path, hoja: str | None, max_filas: int | None, sep: str | None = None) -> tuple[pd.DataFrame, str]:
    sufijo = ruta.suffix.lower()
    if sufijo in (".xlsx", ".xls"):
        df = pd.read_excel(ruta, sheet_name=hoja or 0, dtype=str, nrows=max_filas)
        return df, "n/a (Excel)"
    if sufijo in (".json", ".jsonl"):
        df = pd.read_json(ruta, lines=sufijo == ".jsonl", dtype=False, nrows=max_filas if sufijo == ".jsonl" else None)
        return df.astype("string"), "utf-8 (JSON)"
    ultimo_error = None
    for enc in ENCODINGS:
        try:
            # Sin --sep, pandas adivina el separador; con nombres que traen comas se equivoca.
            df = pd.read_csv(ruta, dtype=str, encoding=enc, sep=sep, engine="python", nrows=max_filas)
            return df, enc
        except (UnicodeDecodeError, pd.errors.ParserError) as exc:
            ultimo_error = exc
    raise SystemExit(f"No se pudo leer {ruta}: {ultimo_error}")


def tiene_pista(columna: str, pistas: tuple[str, ...]) -> bool:
    nombre = columna.lower()
    return any(p in nombre for p in pistas)


def leer_fechas(serie: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Lee fechas solo con formatos explícitos: con dayfirst=True, pandas lee 2025-03-06 como 3 de junio."""
    iso = pd.to_datetime(serie, errors="coerce", format="%Y-%m-%d")
    dia_primero = pd.to_datetime(serie, errors="coerce", format="%d/%m/%Y")
    return iso, dia_primero


def perfilar(ruta: Path, hoja: str | None, max_filas: int | None, sep: str | None = None) -> str:
    df, encoding = leer(ruta, hoja, max_filas, sep)
    n = len(df)
    lineas = [
        f"## Perfil: `{ruta.name}`",
        "",
        f"- Formato: {ruta.suffix.lower()} · Codificación detectada: {encoding}",
        f"- Filas leídas: {n:,}" + (f" (limitado a {max_filas:,})" if max_filas else ""),
        f"- Columnas: {df.shape[1]}",
        f"- Filas duplicadas exactas: {int(df.duplicated().sum()):,}",
        "",
        "| Columna | % nulos | Distintos | Ejemplos |",
        "| --- | --- | --- | --- |",
    ]
    for col in df.columns:
        serie = df[col].astype("string").str.strip().replace("", pd.NA)
        nulos = serie.isna().mean() * 100 if n else 0
        ejemplos = ", ".join(f"`{v[:30]}`" for v in serie.dropna().unique()[:3])
        lineas.append(f"| {col} | {nulos:.1f}% | {serie.nunique():,} | {ejemplos} |")

    candidatas = [c for c in df.columns if n and df[c].notna().all() and df[c].nunique() == n]
    lineas += ["", "### Columnas candidatas a clave (únicas y sin nulos)", ""]
    lineas += [f"- `{c}`" for c in candidatas] or ["- Ninguna columna sola es única: probar claves compuestas."]

    lineas += ["", "### Chequeos de dominio", ""]
    for col in df.columns:
        serie = df[col].astype("string").str.strip()
        if tiene_pista(col, PISTAS_RUC):
            validos = serie.dropna().str.fullmatch(RUC_RE.pattern).mean() * 100 if serie.notna().any() else 0
            nulos = serie.isna().mean() * 100 if n else 0
            lineas.append(
                f"- RUC `{col}`: {nulos:.1f}% nulo · de los no nulos, {validos:.1f}% con formato válido "
                "(11 dígitos, prefijo 10/15/17/20)"
            )
        if tiene_pista(col, PISTAS_MONEDA):
            top = serie.value_counts(dropna=False).head(6)
            dist = ", ".join(f"{k}: {v:,}" for k, v in top.items())
            lineas.append(f"- Moneda `{col}`: {dist}")
        if tiene_pista(col, PISTAS_FECHA):
            iso, dia_primero = leer_fechas(serie)
            fechas = iso.fillna(dia_primero)
            ok_iso, ok_dia, ok = (s.notna().mean() * 100 if n else 0 for s in (iso, dia_primero, fechas))
            rango = f"{fechas.min():%Y-%m-%d} a {fechas.max():%Y-%m-%d}" if fechas.notna().any() else "sin fechas legibles"
            lineas.append(
                f"- Fecha `{col}`: {ok_iso:.1f}% AAAA-MM-DD · {ok_dia:.1f}% DD/MM/AAAA · "
                f"{100 - ok:.1f}% en otro formato o ilegible · rango {rango}"
            )
        if tiene_pista(col, PISTAS_MONTO):
            numeros = pd.to_numeric(serie.str.replace(",", "", regex=False), errors="coerce")
            ok = numeros.notna().mean() * 100 if n else 0
            lineas.append(
                f"- Monto `{col}`: {ok:.1f}% numérico · ≤0: {int((numeros <= 0).sum()):,} · máx: {numeros.max():,.2f}"
                if numeros.notna().any() else f"- Monto `{col}`: no numérico"
            )
    if lineas[-1] == "":
        lineas.append("- Ninguna columna coincide con las pistas de RUC, moneda, fecha o monto. Revisar a mano.")
    lineas += ["", "> Las pistas se basan en el nombre de la columna. Confirma a mano qué columna es cuál."]
    return "\n".join(lineas)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ruta", type=Path)
    parser.add_argument("--hoja", default=None)
    parser.add_argument("--max-filas", type=int, default=None)
    parser.add_argument("--sep", default=None, help="separador del CSV (por ejemplo '|'); si se omite, se adivina")
    args = parser.parse_args()
    if not args.ruta.exists():
        sys.exit(f"No existe: {args.ruta}")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(perfilar(args.ruta, args.hoja, args.max_filas, args.sep))


if __name__ == "__main__":
    main()
