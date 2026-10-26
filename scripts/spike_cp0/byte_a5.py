"""Busca el byte 0xA5 en el CSV de entidades: en latin-1 es ¥, en cp850 es Ñ."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
lineas = Path(sys.argv[1]).read_bytes().split(b"\n")
con_a5 = [l for l in lineas if b"\xa5" in l]
print("lineas con 0xA5:", len(con_a5), "de", len(lineas))
for l in con_a5[:2]:
    campo = l.split(b"|")[1]
    print("  latin-1:", campo.decode("latin-1"), "| cp850:", campo.decode("cp850"))
