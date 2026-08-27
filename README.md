# 🧭 El tesoro del Sacré Coeur — Búsqueda del tesoro en Realidad Aumentada

Juego web de realidad aumentada basada en marcadores, hecho con **AR.js 3.4.7** + **A-Frame 1.6.0**.
Funciona en el navegador del celular o de la notebook, sin instalar nada.

**▶️ Jugar:** https://ibonarambarri.github.io/tesoro-sacre-coeur-ar/

**🖨️ Marcadores para imprimir:** https://ibonarambarri.github.io/tesoro-sacre-coeur-ar/marcadores.html

---

## Cómo se juega

1. Abrís la URL y permitís el acceso a la cámara.
2. Apuntás a cada marcador y lo mantenés encuadrado ~1 segundo.
3. Cada marcador revela un elemento 3D distinto y un verso del mensaje del vigía.
4. Con las **4 primeras señales** reunidas, el **cofre** se desbloquea: al escanearlo se abre,
   suena la fanfarria, cae confeti y aparece el final con tu tiempo.

El progreso se guarda en `localStorage`, así que se puede cerrar y retomar.

## Los 5 marcadores

| # | Marcador | Elemento 3D | Rol |
|---|----------|-------------|-----|
| 1 | 📜 El diario del vigía | pergamino + nudo toroidal dorado | historia inicial |
| 2 | 🗝️ La llave de bronce | llave 3D flotando y girando | pista I |
| 3 | 🧭 La brújula inquieta | brújula con aguja giratoria | pista II |
| 4 | 💎 El cristal verde | octaedro translúcido con halo | pista III |
| 5 | 🏆 El cofre del vigía | cofre cerrado / cofre abierto con joyas | final |

## Estructura

```
index.html           juego (escena AR + HUD + lógica)
marcadores.html      marcadores para imprimir (A4, uno por hoja)
markers/*.svg        marcadores imprimibles 100×100 mm
tools/gen_markers.py generador de los marcadores
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
