/**
 * Juega el juego entero de forma automatica: abre index.html en Chrome headless
 * con una camara falsa alimentada por un .y4m, simula al jugador cerrando los
 * paneles, y reporta que marcadores quedaron registrados.
 *
 * Requiere un servidor estatico en la raiz del repo:
 *     python3 -m http.server 8790
 *
 * Uso:  node tools/pruebas/probar_juego.mjs <video.y4m> [ms_de_espera]
 * Ej.:  node tools/pruebas/probar_juego.mjs /tmp/prueba.y4m 18000
 *
 * Exito = las 5 fichas halladas y finTs distinto de null.
 */
import { spawn } from "node:child_process";

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const VIDEO = process.argv[2];
const ESPERA = Number(process.argv[3] || 18000);
if (!VIDEO) { console.error("falta el .y4m"); process.exit(1); }

const chrome = spawn(CHROME, [
  "--headless=new", "--remote-debugging-port=9333",
  "--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream",
  `--use-file-for-fake-video-capture=${VIDEO}`,
  "--autoplay-policy=no-user-gesture-required",
  "--enable-unsafe-swiftshader", "--use-gl=swiftshader", "--no-sandbox",
  `--user-data-dir=/tmp/perfil-ar-${Date.now()}`,
  "http://localhost:8790/index.html",
], { stdio: ["ignore", "ignore", "ignore"] });

const espera = ms => new Promise(r => setTimeout(r, ms));
let tg = null;
for (let i = 0; i < 20 && !tg; i++) {
  await espera(1000);
  try {
    tg = (await (await fetch("http://localhost:9333/json")).json())
      .find(t => t.type === "page" && t.url.includes("index.html"));
  } catch (e) {}
}
if (!tg) { console.error("Chrome no arranco (¿esta corriendo el servidor en 8790?)"); process.exit(1); }

const ws = new WebSocket(tg.webSocketDebuggerUrl);
let id = 0; const pend = new Map();
const send = (m, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); } };
await new Promise(r => ws.onopen = r);
await send("Runtime.enable");

// saltear la intro
await send("Runtime.evaluate", { expression: `
  localStorage.setItem("sacre-coeur-ar-v2", JSON.stringify({hallados:[],inicioTs:null,finTs:null,vistoIntro:true}));
  location.reload();` });
await espera(3500);

// espiar la deteccion cruda de ARToolKit y cerrar los paneles como haria el jugador
await send("Runtime.evaluate", { expression: `
  window.__visible = {};
  ["inicio","pista1","pista2","pista3"].forEach(function(n){ __visible[n] = 0; });
  setInterval(function(){
    ["inicio","pista1","pista2","pista3"].forEach(function(n){
      var el = document.getElementById("mk-"+n);
      if (el && el.object3D && el.object3D.visible) __visible[n] += 50;
    });
  }, 50);
  setInterval(function(){
    var v = document.getElementById("velo");
    if (v && v.classList.contains("visible")) {
      var b = document.querySelector("#carta [data-cerrar]");
      if (b) b.click();
    }
  }, 250);` });

await espera(ESPERA);
const r = await send("Runtime.evaluate", { expression: `JSON.stringify({
  fichas: [...document.querySelectorAll(".ficha.hallado .nombre")].map(f => f.textContent),
  visible: window.__visible,
  guardado: JSON.parse(localStorage.getItem("sacre-coeur-ar-v2"))
})`, returnByValue: true });

const d = JSON.parse(r.result.value);
console.log("ms visible por marcador:", JSON.stringify(d.visible));
console.log("fichas halladas:", d.fichas.join(", ") || "(ninguna)");
console.log("tesoro abierto:", d.guardado.finTs ? "SI" : "no");
console.log(d.fichas.length === 5 && d.guardado.finTs ? "\n✅ OK: juego completado" : "\n❌ FALLO: no se completo");
chrome.kill();
process.exit(d.fichas.length === 5 && d.guardado.finTs ? 0 : 1);
