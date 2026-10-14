#!/usr/bin/env python3
"""
Genera marcadores.pdf: los 4 carteles para pegar en el edificio, uno por hoja A4.

Cada hoja dice que es del juego y donde va. La de la entrada es la portada: trae el
titulo, como jugar y un QR que abre el juego (markers/qr-juego.svg).

Uso:  python3 tools/gen_pdf.py
Requiere Google Chrome (lo usa para imprimir el HTML a PDF).

El QR esta generado aparte con segno (pip install segno):
    segno.make(URL, error="m").save("markers/qr-juego.svg", scale=10, border=4)
Si cambia la URL del juego, regenerarlo y cambiar URL aca abajo.
"""
import os, subprocess, tempfile, time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
URL = "ibonarambarri.github.io/UCU-LabRL"

HOJAS = [
    # id, encabezado, nombre, lugar
    ("inicio", "Punto de partida", "📜 El diario del vigía", "Entrada"),
    ("pista1", "Pista I de III", "🗝️ La llave de bronce", "Cafetería"),
    ("pista2", "Pista II de III", "🧭 La brújula inquieta", "Clase más alta del edificio"),
    ("pista3", "Pista III de III", "💎 El cristal verde", "Biblioteca · libros de informática"),
]

CSS = """
@page{size:A4;margin:0}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;color:#161a24}
.hoja{width:210mm;height:297mm;padding:12mm 14mm;display:flex;flex-direction:column;
  align-items:center;break-after:page;page-break-after:always;overflow:hidden}
.hoja:last-child{break-after:auto;page-break-after:auto}
.juego{font-size:9.5pt;letter-spacing:.22em;text-transform:uppercase;color:#8a6316;font-weight:700}
h1{font-family:"Iowan Old Style",Palatino,Georgia,serif;margin:2mm 0 0;text-align:center;line-height:1.1}
.portada h1{font-size:34pt}
.pista h1{font-size:22pt}
.rol{margin-top:3mm;font-size:13pt;font-weight:700;border:1.5pt solid #b8862a;border-radius:20mm;
  padding:1.5mm 6mm;color:#5a3f0a}
.marca{flex:none;margin:4mm 0}
.marca svg{display:block}
.portada .marca svg{width:132mm;height:132mm}
.pista .marca svg{width:150mm;height:150mm}
.apuntar{font-size:12pt;color:#3a3f4b;text-align:center;margin:0}
.pie{margin-top:auto;width:100%;display:flex;gap:8mm;align-items:center;
  border-top:0.8pt solid #d8cfba;padding-top:5mm}
.qr svg{display:block}
.portada .qr svg{width:40mm;height:40mm}
.pista .qr svg{width:26mm;height:26mm}
.pasos{flex:1;font-size:11.5pt;line-height:1.5}
.pasos b{color:#5a3f0a}
.pasos ol{margin:1.5mm 0 0;padding-left:5mm}
.url{white-space:nowrap;font-family:Menlo,monospace;font-size:10.5pt;color:#161a24}
.aviso{font-size:9pt;color:#7a8090;margin-top:2mm}
"""


def svg(nombre, viewbox=None):
    s = open(os.path.join(RAIZ, "markers", nombre), encoding="utf-8").read()
    if viewbox and "viewBox" not in s:
        s = s.replace("<svg ", '<svg viewBox="%s" ' % viewbox, 1)
    return s


def hoja(id_, encabezado, nombre, lugar):
    qr = svg("qr-juego.svg", "0 0 370 370")
    marca = svg(id_ + ".svg")
    if id_ == "inicio":
        return f"""
<section class="hoja portada">
  <div class="juego">Búsqueda del tesoro en realidad aumentada</div>
  <h1>El tesoro del Sacré Coeur</h1>
  <div class="rol">🏁 {encabezado} · {lugar}</div>
  <div class="marca">{marca}</div>
  <p class="apuntar">Apuntá la cámara del juego a este cuadro negro, a unos 30–50 cm.</p>
  <div class="pie">
    <div class="qr">{qr}</div>
    <div class="pasos">
      <b>¿Cómo se juega?</b>
      <ol>
        <li>Escaneá el QR con el celular, o entrá a <span class="url">{URL}</span></li>
        <li>Permití el acceso a la <b>cámara</b>.</li>
        <li>Apuntá al cuadro negro grande y seguí las pistas por el edificio.</li>
      </ol>
      <div class="aviso">Juego en curso · Laboratorio de RA, UCU · Por favor no retirar este cartel.</div>
    </div>
  </div>
</section>"""
    return f"""
<section class="hoja pista">
  <div class="juego">El tesoro del Sacré Coeur · Búsqueda del tesoro en RA</div>
  <h1>{nombre}</h1>
  <div class="rol">{encabezado} · {lugar}</div>
  <div class="marca">{marca}</div>
  <div class="pie">
    <div class="qr">{qr}</div>
    <div class="pasos">
      Abrí el juego y apuntá la cámara al cuadro negro.<br>
      ¿No lo tenés abierto? Escaneá el QR o entrá a <span class="url">{URL}</span>
      <div class="aviso">Juego en curso · Laboratorio de RA, UCU · Por favor no retirar este cartel.</div>
    </div>
  </div>
</section>"""


def main():
    html = ('<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>'
            % (CSS, "".join(hoja(*h) for h in HOJAS)))
    with tempfile.TemporaryDirectory() as tmp:
        fuente = os.path.join(tmp, "carteles.html")
        open(fuente, "w", encoding="utf-8").write(html)
        salida = os.path.join(RAIZ, "marcadores.pdf")
        if os.path.exists(salida):
            os.remove(salida)
        # Chrome escribe el PDF pero a veces no termina solo: se espera a que el
        # archivo deje de crecer y se lo cierra.
        chrome = subprocess.Popen([CHROME, "--headless=new", "--no-pdf-header-footer",
                                   "--user-data-dir=" + os.path.join(tmp, "perfil"),
                                   "--print-to-pdf=" + salida, "file://" + fuente],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        previo = -1
        for _ in range(60):
            time.sleep(0.5)
            if chrome.poll() is not None:
                break
            tam = os.path.getsize(salida) if os.path.exists(salida) else -1
            if tam > 0 and tam == previo:
                break
            previo = tam
        chrome.kill()
        if not os.path.exists(salida):
            raise SystemExit("Chrome no genero el PDF")
    print(salida)


if __name__ == "__main__":
    main()
