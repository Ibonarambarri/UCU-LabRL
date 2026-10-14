# 🧭 El tesoro del Sacré Coeur — Búsqueda del tesoro en Realidad Aumentada

Juego web de realidad aumentada basada en marcadores, hecho con **AR.js 3.4.7** + **A-Frame 1.6.0**.
Funciona en el navegador del celular o de la notebook, sin instalar nada.

**▶️ Jugar:** https://ibonarambarri.github.io/UCU-LabRL/

**🖨️ Marcadores para imprimir:** https://ibonarambarri.github.io/UCU-LabRL/marcadores.html

**🖥️ Marcadores en pantalla (sin impresora):** https://ibonarambarri.github.io/UCU-LabRL/pantalla.html

**📄 Carteles en PDF (para pegar en el edificio):** https://ibonarambarri.github.io/UCU-LabRL/marcadores.pdf

---

## Cómo se juega

1. Abrís la URL (o escaneás el QR del cartel de la entrada) y permitís la cámara.
2. Empezás en la **entrada**: el juego lo dice al abrir y el HUD muestra siempre el próximo destino.
3. Cada marcador revela un elemento 3D y un verso que indica dónde está el siguiente.
4. Con las **3 pistas** reunidas, volvés a la entrada: el mismo marcador del inicio ahora
   es el **cofre**. Se abre, suena la fanfarria, cae confeti y aparece el final con tu tiempo.

El progreso se guarda en `localStorage`, así que se puede cerrar y retomar.

## El recorrido: 4 marcadores en el edificio

| # | Lugar | Marcador | Elemento 3D |
|---|-------|----------|-------------|
| 1 | Entrada | 📜 El diario del vigía | pergamino + nudo toroidal dorado |
| 2 | Cafetería | 🗝️ La llave de bronce | llave 3D flotando y girando |
| 3 | Clase más alta del edificio | 🧭 La brújula inquieta | brújula con aguja giratoria |
| 4 | Biblioteca, libros de informática | 💎 El cristal verde | octaedro translúcido con halo |
| — | Entrada, otra vez | 🏆 El cofre del vigía | el marcador 1 pasa a mostrar el cofre |

La broma del final: el tesoro estuvo todo el tiempo en la entrada. El cofre no tiene
marcador propio; es el de la entrada escaneado de nuevo con las tres pistas reunidas.

## Estructura

```
index.html           juego (escena AR + HUD + lógica)
marcadores.html      marcadores para imprimir (A4, uno por hoja)
marcadores.pdf       carteles para pegar: nombre del juego, lugar y QR al juego
pantalla.html        marcadores a pantalla completa, para mostrar en otro monitor
markers/*.svg        marcadores imprimibles 100×100 mm (+ qr-juego.svg)
tools/gen_markers.py generador de los marcadores
tools/gen_pdf.py     genera marcadores.pdf
```

## Marcadores: por qué barcode y no patrones

El juego usa marcadores **barcode `3x3_HAMMING63`** (ids 1 a 5 del set oficial de
ARToolKit), no marcadores de patrón.

La primera versión usaba patrones propios (`.patt`) y **no se detectaban en el celular**.
Midiéndolo con el detector real de AR.js, la causa quedó clara: la correlación de
imágenes es demasiado frágil. Un desplazamiento del 2 % en la ventana de muestreo
—error normal al estimar las esquinas del cuadrado— tiraba la confianza de 0.99 a 0.60,
justo el umbral. En la práctica dos de los cinco marcadores no se reconocían **nunca**:
ARToolKit los confundía con un tercero, y la confianza mediana era −1.00 (sin match).

Los barcode decodifican un código binario con corrección de errores en vez de comparar
imágenes. Medido en las mismas condiciones, la confianza es **1.00** y no hay ninguna
confusión entre marcadores.

### La zona blanca es parte del marcador

ARToolKit localiza el marcador buscando un **cuadrado negro sobre un fondo más claro**.
Si el negro llega al borde de la imagen no hay cuadrado que encontrar y **no se detecta nada**:
medido en el banco de pruebas, sin margen la detección es de 0 sobre 5, y con margen 5 sobre 5.

Por eso el margen blanco va **dentro del SVG** (14 × 14 cm en total para un cuadro de 10 × 10 cm),
y así sobrevive aunque el archivo se imprima a sangre o se abra a pantalla completa. No lo recortes.

Para regenerar los SVG imprimibles:

```bash
python3 tools/gen_markers.py
```

## Detalles técnicos

- **Detección tolerante al parpadeo:** AR.js alterna `markerFound`/`markerLost` varias veces
  por segundo. Exigir visibilidad *continua* hacía que el marcador casi nunca se registrara,
  porque cada `markerLost` cancelaba el temporizador. Ahora se muestrea la visibilidad cada
  100 ms y se acumulan 500 ms de tiempo visible, con 700 ms de gracia antes de descontar.
- **Anti-jitter:** `smooth`, `smoothCount: 6`, `smoothTolerance: 0.02`, `smoothThreshold: 2`.
- **Sin assets externos:** los sonidos se sintetizan con la Web Audio API (fanfarria, error,
  hallazgo) y el confeti se dibuja en un `<canvas>`; solo se cargan A-Frame y AR.js por CDN.
- **Feedback:** panel narrativo por pista, aviso emergente, cronómetro, vibración
  (`navigator.vibrate`), fichas de progreso y final con confeti + tiempo.
- La cámara **exige HTTPS** (o `localhost`). El juego avisa si se abrió por HTTP.

## Probar en local

```bash
python3 -m http.server 8000
# luego abrir http://localhost:8000
```

Para probar desde el celular en la red local hace falta HTTPS: lo más simple es desplegar
(GitHub Pages / Vercel) y abrir la URL pública.

## Consejos para los beta testers

- Papel **blanco mate**, sin brillo, y con el **margen blanco** alrededor del cuadro negro.
- Probado en automático (Chrome headless + cámara sintética, detector real de AR.js):
  el juego completa los 5 marcadores incluso con el marcador ocupando un tercio del cuadro,
  desenfoque fuerte e inclinación de 18°.
- Marcador **plano**, bien iluminado, sin sombras duras encima.
- Cámara a **25–50 cm**, con todo el marco negro dentro de la pantalla.
- También funciona apuntando a los marcadores mostrados en **otra pantalla**.

---

Laboratorio de Realidad Aumentada · AR.js + A-Frame
