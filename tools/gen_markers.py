#!/usr/bin/env python3
"""
Genera marcadores AR personalizados para AR.js / ARToolKit.

Para cada marcador produce:
  markers/<nombre>.patt  -> patron 16x16 en las 4 rotaciones (formato ARToolKit)
  markers/<nombre>.svg   -> imagen imprimible (borde negro + patron interior)

El patron interior impreso es EXACTAMENTE la grilla 16x16 del .patt escalada,
por lo que el downsample que hace ARToolKit sobre la camara reproduce el patron.
"""
import os

CELL = 2  # cada celda de diseno 8x8 ocupa 2x2 px en la grilla 16x16

# 1 = negro, 0 = blanco. Grillas 8x8, asimetricas bajo rotacion y distintas entre si.
PATTERNS = {
    # Anillo exterior blanco: separa el patron del borde negro.
    # Conjunto elegido por busqueda para minimizar confusion entre marcadores
    # (ver tools/gen_markers.py, similitud cruzada maxima ~0.58 en las 4 rotaciones).
    "inicio": [
        "00000000",
        "01011100",
        "00000100",
        "00100110",
        "00001010",
        "01111100",
        "00011000",
        "00000000",
    ],
    "pista1": [
        "00000000",
        "01101110",
        "00110100",
        "01100100",
        "01010000",
        "01001010",
        "00001110",
        "00000000",
    ],
    "pista2": [
        "00000000",
        "01111000",
        "01110010",
        "01101000",
        "01000000",
        "00011010",
        "00100000",
        "00000000",
    ],
    "pista3": [
        "00000000",
        "01110110",
        "01111000",
        "01001000",
        "01001000",
        "00100100",
        "00000110",
        "00000000",
    ],
    "tesoro": [
        "00000000",
        "01011010",
        "01010100",
        "01110000",
        "00110110",
        "00110000",
        "01110100",
        "00000000",
    ],
}


def to16(grid8):
    """Escala la grilla 8x8 de diseno a la grilla 16x16 del patron."""
    out = []
    for row in grid8:
        big = "".join(c * CELL for c in row)
        for _ in range(CELL):
            out.append(big)
    return out


def rot90(grid):
    """Rota 90 grados en sentido horario."""
    n = len(grid)
    return ["".join(grid[n - 1 - r][c] for r in range(n)) for c in range(n)]


def patt_block(grid):
    """Un bloque de orientacion: R, G y B, cada uno 16 filas de 16 valores."""
    lines = []
    for _channel in range(3):
        for row in grid:
            vals = ["  0" if ch == "1" else "255" for ch in row]
            lines.append(" ".join(vals))
    return "\n".join(lines)


def write_patt(path, grid16):
    blocks = []
    g = grid16
    for _ in range(4):
        blocks.append(patt_block(g))
        g = rot90(g)
    with open(path, "w") as f:
        f.write("\n\n".join(blocks) + "\n")


def write_svg(path, grid16, label):
    """Marcador imprimible: 100x100 mm, borde negro de 25%, patron interior de 50%."""
    size = 100.0
    border = size * 0.25
    inner = size * 0.5
    cell = inner / 16.0
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}mm" height="{size}mm" '
        f'viewBox="0 0 {size} {size}">',
        f'<rect x="0" y="0" width="{size}" height="{size}" fill="#000000"/>',
        f'<rect x="{border}" y="{border}" width="{inner}" height="{inner}" fill="#ffffff"/>',
    ]
    for r, row in enumerate(grid16):
        for c, ch in enumerate(row):
            if ch == "1":
                x = border + c * cell
                y = border + r * cell
                parts.append(
                    f'<rect x="{x:.4f}" y="{y:.4f}" width="{cell:.4f}" '
                    f'height="{cell:.4f}" fill="#000000"/>'
                )
    parts.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(parts) + "\n")


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = os.path.join(here, "markers")
    os.makedirs(outdir, exist_ok=True)
    for name, grid8 in PATTERNS.items():
        grid16 = to16(grid8)
        write_patt(os.path.join(outdir, f"{name}.patt"), grid16)
        write_svg(os.path.join(outdir, f"{name}.svg"), grid16, name)
        print(f"ok  markers/{name}.patt  markers/{name}.svg")


if __name__ == "__main__":
    main()
