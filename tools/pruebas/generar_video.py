#!/usr/bin/env python3
"""
Genera un video .y4m con el recorrido completo (entrada, 3 pistas, entrada otra vez), para alimentar la camara
falsa de Chrome (--use-file-for-fake-video-capture) y probar la deteccion sin
tener que imprimir nada ni apuntar un telefono.

Uso:  python3 tools/pruebas/generar_video.py <lado_px> <blur> <giro_grados> <salida.y4m>
Ej.:  python3 tools/pruebas/generar_video.py 160 1.0 8 /tmp/prueba.y4m

  lado_px  tamano del cuadro negro dentro de un encuadre de 320x240
  blur     desenfoque gaussiano (simula camara movida / fuera de foco)
  giro     inclinacion en grados

Modo especial:  lado_px = "sin_margen" reproduce el fallo clasico (el marcador
llena el encuadre y no queda zona blanca): debe dar 0 detecciones.
"""
import sys, os
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from gen_markers import CODIGOS, QUIETO

W, H, FPS = 320, 240, 30
FRAMES = 90          # 3 s por marcador
SUP = 4              # supermuestreo


def dibujar(grilla, lado_negro, con_margen=True):
    """Marcador tal como se imprime: cuadro negro + zona blanca alrededor."""
    q = int(lado_negro * QUIETO) if con_margen else 0
    total = lado_negro + 2 * q
    L = total * SUP
    im = Image.new("L", (L, L), 255)
    d = ImageDraw.Draw(im)
    o = q * SUP
    N = lado_negro * SUP
    d.rectangle([o, o, o + N - 1, o + N - 1], fill=0)
    b, inner = o + N * 0.25, N * 0.5
    d.rectangle([b, b, b + inner - 1, b + inner - 1], fill=255)
    cell = inner / 3.0
    for r in range(3):
        for c in range(3):
            if grilla[r][c]:
                d.rectangle([b + c*cell, b + r*cell, b + (c+1)*cell - 1, b + (r+1)*cell - 1], fill=0)
    return im.resize((total, total), Image.LANCZOS)


def main():
    arg, blur, giro, salida = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    sin_margen = (arg == "sin_margen")
    lado = H + 40 if sin_margen else int(arg)
    with open(salida, "wb") as f:
        f.write(b"YUV4MPEG2 W%d H%d F%d:1 Ip A1:1 C420mpeg2\n" % (W, H, FPS))
        # el cofre es el marcador de la entrada escaneado de nuevo al final
        for nombre in ["inicio", "pista1", "pista2", "pista3", "inicio"]:
            m = dibujar(CODIGOS[nombre][1], lado, con_margen=not sin_margen)
            if giro:
                m = m.rotate(giro, resample=Image.BICUBIC, expand=True, fillcolor=255)
            c = Image.new("L", (W, H), 255)
            c.paste(m, ((W - m.size[0]) // 2, (H - m.size[1]) // 2))
            if blur:
                c = c.filter(ImageFilter.GaussianBlur(blur))
            Y = c.tobytes()
            U = bytes([128]) * ((W // 2) * (H // 2))
            for _ in range(FRAMES):
                f.write(b"FRAME\n"); f.write(Y); f.write(U); f.write(U)
    print("%s  (lado=%s blur=%.1f giro=%.0f%s)" %
          (salida, arg, blur, giro, ", SIN zona blanca" if sin_margen else ""))


if __name__ == "__main__":
    main()
