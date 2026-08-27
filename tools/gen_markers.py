#!/usr/bin/env python3
"""
Genera los marcadores AR imprimibles del juego (AR.js / ARToolKit).

Se usan marcadores BARCODE del tipo 3x3_HAMMING63, no patrones de imagen:
el detector decodifica un codigo binario con correccion de errores en vez de
correlacionar imagenes, asi que no hay confusion entre marcadores y la
confianza de deteccion es 1.00 en lugar de quedar al borde del umbral.

Las grillas de abajo son las de los ids 1..5 del set oficial de ARToolKit
(artoolkit-barcode-markers-collection, carpeta 3x3_hamming_6_3), verificadas
contra el decodificador real de AR.js.

Geometria (la que espera ARToolKit): borde negro del 25% de cada lado y
grilla 3x3 ocupando el 50% central.
"""
import os

# id -> grilla 3x3 (1 = celda negra), leida del set oficial
CODIGOS = {
    "inicio": (1, [[1,0,0],[0,1,1],[1,1,0]]),
    "pista1": (2, [[1,0,1],[1,0,0],[1,1,0]]),
    "pista2": (3, [[1,0,1],[1,1,1],[1,0,0]]),
    "pista3": (4, [[1,1,0],[1,0,1],[1,0,0]]),
    "tesoro": (5, [[1,1,0],[1,1,0],[1,1,0]]),
}

LADO_MM = 100.0     # marcador impreso de 10 x 10 cm


def svg(grilla, lado=LADO_MM):
    borde = lado * 0.25
    inner = lado * 0.5
    cell = inner / 3.0
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{lado}mm" height="{lado}mm" '
        f'viewBox="0 0 {lado} {lado}" shape-rendering="crispEdges">',
        f'<rect x="0" y="0" width="{lado}" height="{lado}" fill="#000000"/>',
        f'<rect x="{borde}" y="{borde}" width="{inner}" height="{inner}" fill="#ffffff"/>',
    ]
    for r in range(3):
        for c in range(3):
            if grilla[r][c]:
                x = borde + c * cell
                y = borde + r * cell
                p.append(f'<rect x="{x:.4f}" y="{y:.4f}" width="{cell:.4f}" '
                         f'height="{cell:.4f}" fill="#000000"/>')
    p.append("</svg>")
    return "\n".join(p) + "\n"


def main():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    salida = os.path.join(raiz, "markers")
    os.makedirs(salida, exist_ok=True)
    for nombre, (codigo, grilla) in CODIGOS.items():
        with open(os.path.join(salida, f"{nombre}.svg"), "w") as f:
            f.write(svg(grilla))
        print(f"ok  markers/{nombre}.svg  (barcode id {codigo})")


if __name__ == "__main__":
    main()
