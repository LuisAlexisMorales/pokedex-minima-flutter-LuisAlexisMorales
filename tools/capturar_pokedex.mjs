// Capturas reales de la Pokédex mínima ejecutada en Chrome (build web).
// Requiere: flutter build web --debug y servidor estático en http://127.0.0.1:8083
import { spawn } from 'node:child_process';
import { mkdirSync, mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import process from 'node:process';

const APP_URL = process.env.APP_URL ?? 'http://127.0.0.1:8083/';
const OUT_DIR = path.resolve('evidencias');
const PORT = 9336;
const CHROME =
  process.env.CHROME_PATH ?? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status} en ${url}`);
  return response.json();
}

mkdirSync(OUT_DIR, { recursive: true });
const profile = mkdtempSync(path.join(tmpdir(), 'pokedex-chrome-'));
const chrome = spawn(
  CHROME,
  [
    '--headless=new',
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${profile}`,
    '--window-size=900,900',
    '--hide-scrollbars',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-extensions',
    'about:blank',
  ],
  { stdio: 'ignore' },
);

let browserWs;
try {
  let version;
  for (let i = 0; i < 50; i += 1) {
    try {
      version = await getJson(`http://127.0.0.1:${PORT}/json/version`);
      break;
    } catch {
      await delay(200);
    }
  }
  if (!version) throw new Error('Chrome no expuso el puerto de depuración');

  browserWs = new WebSocket(version.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    browserWs.onopen = resolve;
    browserWs.onerror = reject;
  });

  let nextId = 0;
  const pending = new Map();
  browserWs.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
    }
  };

  const send = (method, params = {}, sessionId) =>
    new Promise((resolve, reject) => {
      const id = ++nextId;
      pending.set(id, { resolve, reject });
      browserWs.send(
        JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }),
      );
    });

  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  const cmd = (method, params = {}) => send(method, params, sessionId);

  await cmd('Page.enable');
  await cmd('Runtime.enable');
  await cmd('Accessibility.enable');
  await cmd('Emulation.setDeviceMetricsOverride', {
    width: 900,
    height: 900,
    deviceScaleFactor: 1,
    mobile: false,
  });

  const evalJs = async (expression) => {
    const result = await cmd('Runtime.evaluate', { expression, returnByValue: true });
    return result.result.value;
  };

  const axLabels = async () => {
    const ax = await cmd('Accessibility.getFullAXTree');
    return ax.nodes.map((n) => n.name?.value).filter(Boolean);
  };

  const waitForLabels = async (predicado, timeout = 25000) => {
    const inicio = Date.now();
    while (Date.now() - inicio < timeout) {
      const labels = await axLabels();
      if (predicado(labels)) return labels;
      await delay(300);
    }
    throw new Error(`Timeout esperando etiquetas: ${(await axLabels()).join(' | ')}`);
  };

  const abrirApp = async () => {
    await cmd('Page.navigate', { url: APP_URL });
    for (let i = 0; i < 100; i += 1) {
      const listo = await evalJs(
        "!!document.querySelector('[aria-label=\"Enable accessibility\"]')",
      );
      if (listo) {
        await evalJs(
          "document.querySelector('[aria-label=\"Enable accessibility\"]')?.click()",
        );
        await delay(600);
        if (await evalJs("document.querySelectorAll('flt-semantics').length > 0")) {
          break;
        }
      }
      await delay(200);
    }
    if (!(await evalJs("document.querySelectorAll('flt-semantics').length > 0"))) {
      throw new Error('No se pudo activar la semántica de Flutter');
    }
    await waitForLabels((labels) => labels.some((l) => l.includes('Buscar')));
  };

  const centroDe = async (texto, indice = 0) => {
    const punto = await evalJs(`(() => {
      const todos = [
        ...document.querySelectorAll('[role], [data-semantics-role], input'),
      ];
      const nombre = e => (e.getAttribute('aria-label') || e.textContent || '').trim();
      let els = todos.filter(e => nombre(e) === ${JSON.stringify(texto)});
      if (!els.length) els = todos.filter(e => nombre(e).includes(${JSON.stringify(texto)}));
      const el = els[${indice}];
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2, w: r.width, h: r.height };
    })()`);
    if (!punto) throw new Error(`No encontré el control "${texto}" (índice ${indice})`);
    return punto;
  };

  const raton = async (x, y) => {
    for (const type of ['mousePressed', 'mouseReleased']) {
      await cmd('Input.dispatchMouseEvent', { type, x, y, button: 'left', clickCount: 1 });
    }
    await delay(300);
  };

  const click = async (texto, indice = 0) => {
    const { x, y } = await centroDe(texto, indice);
    await raton(x, y);
  };

  const escribir = async (texto) => {
    await cmd('Input.dispatchKeyEvent', {
      type: 'keyDown',
      windowsVirtualKeyCode: 65,
      modifiers: 2,
      key: 'a',
      code: 'KeyA',
    });
    await cmd('Input.dispatchKeyEvent', {
      type: 'keyUp',
      windowsVirtualKeyCode: 65,
      modifiers: 2,
      key: 'a',
      code: 'KeyA',
    });
    await cmd('Input.insertText', { text: texto });
    await delay(250);
  };

  const buscar = async (texto) => {
    await click('Nombre o número del Pokémon');
    await escribir(texto);
    await click('Buscar');
  };

  const shot = async (archivo) => {
    const { data } = await cmd('Page.captureScreenshot', { format: 'png' });
    writeFileSync(path.join(OUT_DIR, archivo), Buffer.from(data, 'base64'));
    console.log(`Guardada: ${archivo}`);
    console.log(`  Etiquetas: ${(await axLabels()).slice(0, 12).join(' | ')}`);
  };

  await abrirApp();
  const roles = await evalJs(
    "[...document.querySelectorAll('[role]')].map(e => e.getAttribute('role') + ':' + (e.getAttribute('aria-label') || e.textContent || '')).slice(0, 20)",
  );
  console.log('Roles iniciales:', roles.join(' | '));

  // -------------------------------------------------- Pikachu (nombre)
  await buscar('pikachu');
  await waitForLabels(
    (l) =>
      l.some((x) => x.includes('25') && x.includes('pikachu')) &&
      l.some((x) => x.includes('electric')) &&
      l.some((x) => x.includes('Altura: 0.4 m')),
  );
  await delay(1500); // esperar la imagen remota
  await shot('figura_1_pikachu.png');

  // -------------------------------------------------- Charizard (número 6)
  await buscar('6');
  await waitForLabels(
    (l) =>
      l.some((x) => x.includes('6') && x.includes('charizard')) &&
      l.some((x) => x.includes('fire')),
  );
  await delay(1200);
  await shot('figura_3_numero_6.png');

  // -------------------------------------------------- Nombre mal escrito
  await buscar('pikachuu');
  await waitForLabels((l) =>
    l.some((x) => x.includes('No se encontró el Pokémon')),
  );
  await delay(400);
  await shot('figura_2_error.png');

  console.log('Evidencias generadas en', OUT_DIR);
} finally {
  browserWs?.close();
  chrome.kill();
}
