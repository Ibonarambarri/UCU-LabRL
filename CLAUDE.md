# El tesoro del Sacré Coeur — búsqueda del tesoro en AR

Juego web de realidad aumentada con **AR.js 3.4.7 + A-Frame 1.6.0**. Sin build, sin
dependencias, sin framework: son tres HTML estáticos servidos por GitHub Pages.

- **Juego:** https://ibonarambarri.github.io/tesoro-sacre-coeur-ar/
- **Repo:** https://github.com/Ibonarambarri/tesoro-sacre-coeur-ar
- El **único entregable del laboratorio es la URL**. La nota depende de que tres beta
  testers (Bruno, Maxi, Gonzalo) puedan encontrar el tesoro. Robustez de detección
  antes que cualquier otra cosa.

## Estructura

```
index.html            juego: escena AR + HUD + lógica
marcadores.html       marcadores para imprimir (A4, uno por hoja)
pantalla.html         marcadores a pantalla completa (para mostrar en otro monitor)
markers/*.svg         los 5 marcadores, 14×14 cm (cuadro negro de 10×10 + zona blanca)
tools/gen_markers.py  genera los SVG a partir de las grillas 3×3
tools/pruebas/        banco de pruebas headless (ver más abajo)
```

Todo el texto de la interfaz y los comentarios del código están **en español rioplatense**
(«apuntá», «tenés»). Mantener ese registro.

## Reglas que NO hay que romper

Cada una salió de un fallo real y está verificada con el banco de pruebas. Si algo deja de
detectarse, revisar esta lista antes que nada.

### 1. Marcadores barcode, nunca patrones (`.patt`)

El juego usa `matrixCodeType: 3x3_HAMMING63` con `<a-marker type="barcode" value="N">`.

La primera versión usaba patrones propios y **no se detectaba en el celular**. Leyendo los
eventos `getMarker` de ARToolKit: dos de los cinco marcadores no se reconocían **nunca**
(sus ids no aparecían jamás, ARToolKit los confundía con un tercero) y la confianza mediana
era **−1.00**, o sea "ningún match". Causa medida: la correlación de imágenes es frágil,
**un desplazamiento del 2 % en la ventana de muestreo tira la confianza de 0.99 a 0.60**,
justo el umbral — y ese error es normal al estimar las esquinas con blur y perspectiva.

No era un problema de diseño de los patrones: comparados contra `hiro` bajo las mismas
perturbaciones puntuaban igual o mejor. El mecanismo entero es marginal.

Con barcode la confianza medida es **1.00** y no hay ninguna confusión. **No volver a
patrones.**

### 2. El string de `matrixCodeType` es exacto

Los valores válidos, sacados del bundle de AR.js, son:

```
3x3    3x3_HAMMING63    3x3_PARITY65    4x4    4x4_BCH_13_9_3    4x4_BCH_13_5_5
```

Escribí `3x3_HAMMING_63` (un guion bajo de más) y **AR.js no avisa nada**: simplemente no
decodifica jamás, cero eventos, sin error en consola. Si los barcode dejan de andar, este
string es el primer sospechoso.

### 3. La zona blanca es parte del marcador

ARToolKit localiza el marcador buscando **un cuadrado negro contra un fondo más claro**. Si
el negro llega al borde de la imagen no hay cuadrado que encontrar y ni siquiera empieza a
decodificar. Medido: **sin margen 0/5, con margen 5/5.**

Por eso el margen blanco va **dentro del SVG** (`QUIETO = 0.20` en `gen_markers.py`): así
sobrevive a una impresión a sangre o a que alguien abra el archivo a pantalla completa. El
fallo real que reportó el usuario fue exactamente ese: abrió `markers/inicio.svg` directo en
un monitor y el negro llenaba la pantalla.

Nunca generar un marcador sin zona blanca, ni recortarla en el CSS de impresión.

### 4. El fondo opaco va en `<html>`, no en `<body>`

AR.js le pone `z-index: -2` al `<video>` de la cámara. Por el orden de pintado de CSS, el
fondo de un `body` opaco se dibuja **por encima** de los hijos con z-index negativo: la
cámara captura (indicador verde encendido) pero se ve una pantalla negra. El fondo del
elemento raíz, en cambio, se pinta antes que todo.

En `index.html`: `html{background:var(--tinta)}` y `body{background:transparent}`.

### 5. La detección parpadea: no exigir visibilidad continua

AR.js alterna `markerFound`/`markerLost` varias veces por segundo (medido: FOUND y LOST a
192 ms de distancia). La primera versión exigía 900 ms de visibilidad **continua** y
cancelaba el temporizador en cada `markerLost`, así que el marcador casi nunca llegaba a
registrarse.

Ahora se muestrea `el.object3D.visible` cada `PULSO_MS` (100 ms) y se acumulan `ESPERA_MS`
(500 ms) de tiempo visible, con `GRACIA_MS` (700 ms) antes de empezar a descontar, y
descontando de a poco en vez de reiniciar. No volver a una lógica basada en eventos
`markerFound`/`markerLost` crudos.

## Banco de pruebas headless

No hace falta imprimir nada ni apuntar un teléfono: Chrome headless acepta un video como
cámara falsa, así que se puede jugar el juego entero de forma automática.

```bash
# 1. servidor estático en la raíz del repo
python3 -m http.server 8790

# 2. generar un video con los 5 marcadores (lado_px, blur, giro, salida)
python3 tools/pruebas/generar_video.py 160 1.0 8 /tmp/ok.y4m

# 3. jugarlo automáticamente (cierra los paneles como haría el jugador)
node tools/pruebas/probar_juego.mjs /tmp/ok.y4m 18000
```

Sale `✅ OK: juego completado` cuando registra los 5 marcadores y abre el cofre; devuelve
código de salida 1 si falla, así que sirve para CI.

Para reproducir el fallo clásico y comprobar que el test discrimina:

```bash
python3 tools/pruebas/generar_video.py sin_margen 1.0 0 /tmp/mal.y4m
node tools/pruebas/probar_juego.mjs /tmp/mal.y4m 18000     # debe dar ❌ con 0 detecciones
```

**Correr esto ante cualquier cambio que toque marcadores, la escena AR o la lógica de
detección.** Condiciones que ya pasan: marcador a un tercio del encuadre, blur 2.0 e
inclinación de 18°.

### Diagnóstico crudo de ARToolKit

Cuando haga falta saber *qué está viendo* el detector y no solo si detecta, engancharse al
controlador y escuchar `getMarker`. Es la herramienta que resolvió todo esto:

```js
var sc = document.querySelector("a-scene");
var ctrl = sc.systems.arjs._arSession.arContext.arController;
ctrl.addEventListener("getMarker", function (ev) {
  var m = ev.data.marker;
  console.log(m.idPatt, m.cfPatt, m.idMatrix, m.cfMatrix);
});
```

`cfMatrix: 1` es un barcode decodificado limpio. `cfPatt: -1` es "ningún patrón coincide".
Ojo: el controlador tarda en existir, hay que reintentar con un `setInterval`.

Notas del entorno: Chrome headless corre a ~120 fps con swiftshader, así que el framerate no
es cuello de botella. Un `.y4m` de 320×240 pesa ~40 MB por cada 15 s. Si Chrome no arranca,
suele ser un `SingletonLock` de un perfil viejo: usar `--user-data-dir` con timestamp.

## Detalles de implementación

- **Sin assets externos.** Los sonidos se sintetizan con la Web Audio API y el confeti se
  dibuja en un `<canvas>`. Lo único que viene de CDN son A-Frame y AR.js. Mantenerlo así:
  un archivo que falta es un modo de fallo silencioso más.
- **A-Frame `<a-text>` no renderiza acentos** con la fuente por defecto. El texto 3D va sin
  tildes («EL DIARIO DEL VIGIA»); los acentos van en el HUD HTML, que sí los soporta.
- **Progreso en `localStorage`** bajo la clave `sacre-coeur-ar-v1`. El botón ↺ lo borra.
- **El cofre (`tesoro`, barcode 5) está bloqueado** hasta tener los otros 4: escanearlo
  antes muestra un panel de "cofre cerrado".
- **Vigía de cámara:** si a los 12 s no llega imagen, aparece un panel con causas concretas
  en vez de una pantalla negra muda.
- La cámara **exige HTTPS** (o localhost). El juego avisa si se abrió por HTTP.

## Despliegue

GitHub Pages desde `main` / raíz, con `.nojekyll`. Después de `git push`:

```bash
gh api repos/Ibonarambarri/tesoro-sacre-coeur-ar/pages/builds/latest --jq '.commit+" "+.status'
```

Esperar a que el commit del build coincida con `git rev-parse HEAD` **y** el estado sea
`built` antes de dar nada por desplegado: consultar solo el estado devuelve el build
anterior y engaña. Al probar en el celular conviene forzar la recarga, porque Pages cachea
el HTML unos minutos.

## Convenciones de git

Commits en español, sin coautoría ni trailers (el usuario lo pidió explícitamente).
