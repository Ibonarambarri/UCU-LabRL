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
index.html          juego (escena AR + HUD + lógica)
marcadores.html     marcadores para imprimir (A4, uno por hoja)
markers/*.patt      patrones ARToolKit (16×16, 4 rotaciones)
markers/*.svg       marcadores imprimibles 100×100 mm
tools/gen_markers.py generador de patrones + SVG
```

## Marcadores propios

Los 5 patrones son **propios**, no los de ejemplo de AR.js. `tools/gen_markers.py`:

- define cada marcador en una grilla 8×8 (anillo exterior blanco + 6×6 de contenido),
- la escala a la grilla 16×16 y escribe el `.patt` en formato ARToolKit
  (4 rotaciones × 3 canales × 16 filas),
- emite el SVG imprimible con **exactamente** la misma grilla (borde negro del 25 %,
  patrón interior del 50 %, que es el `patternRatio: 0.5` configurado en la escena),
- el conjunto se eligió por búsqueda aleatoria minimizando la similitud entre patrones
  considerando las 4 rotaciones: **0.58 máx.** sobre la región discriminante (azar ≈ 0.50).

Para regenerarlos o cambiar los diseños:

```bash
python3 tools/gen_markers.py
```

## Detalles técnicos

- **Anti-falsos positivos:** un marcador debe verse ~900 ms seguidos para contar (`ESPERA_MS`).
- **Anti-jitter:** `smooth`, `smoothCount: 10`, `smoothTolerance: 0.01`, `smoothThreshold: 5`.
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
- Marcador **plano**, bien iluminado, sin sombras duras encima.
- Cámara a **25–50 cm**, con todo el marco negro dentro de la pantalla.
- También funciona apuntando a los marcadores mostrados en **otra pantalla**.

---

Laboratorio de Realidad Aumentada · AR.js + A-Frame
