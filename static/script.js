/* =====================================================================
   SYNCWEB SOLUTIONS | script.js
   1. Menu do celular
   2. Parallax do fundo (mouse e rolagem)
   3. Pausa das animações fora da tela
   4. Objeto 3D (three.js): estrela esmeralda flutuante
   5. Navegação fixa e destaque da seção atual no menu
   6. Animação de entrada das seções
   7. Contato: botão flutuante, planos e formulário
   ===================================================================== */

const reducedMQ = window.matchMedia("(prefers-reduced-motion: reduce)");
const hero = document.querySelector(".hero");
const backdrop = document.querySelector(".sw-backdrop");
const starEl = document.getElementById("sw-star");

/* ---------- 1. menu do celular ---------- */
const menuBtn = document.querySelector(".nav__menu-btn");
const menu = document.getElementById("menu-mobile");

function setMenu(open) {
  menuBtn.setAttribute("aria-expanded", String(open));
  menuBtn.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
  menu.hidden = !open;
}
menuBtn.addEventListener("click", () => setMenu(menu.hidden));
menu.addEventListener("click", (e) => {
  if (e.target.closest("a")) setMenu(false);
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !menu.hidden) {
    setMenu(false);
    menuBtn.focus();
  }
});

/* ---------- 2. parallax do fundo ----------
   Escreve --sw-px / --sw-py (mouse, de -1 a 1) e --sw-sy (rolagem em px).
   Cada camada do fundo usa uma profundidade diferente (--d no HTML).
   Atualiza no máximo uma vez por quadro. */
const pointer = { x: 0, y: 0 }; // compartilhado com o objeto 3D
(function parallax() {
  let frame = 0;
  let sy = 0;
  const apply = () => {
    frame = 0;
    backdrop.style.setProperty("--sw-px", pointer.x.toFixed(3));
    backdrop.style.setProperty("--sw-py", pointer.y.toFixed(3));
    backdrop.style.setProperty("--sw-sy", sy.toFixed(1));
  };
  const schedule = () => {
    if (!frame && !reducedMQ.matches) frame = requestAnimationFrame(apply);
  };
  window.addEventListener(
    "pointermove",
    (e) => {
      if (e.pointerType === "touch") return;
      pointer.x = (e.clientX / window.innerWidth) * 2 - 1;
      pointer.y = (e.clientY / window.innerHeight) * 2 - 1;
      schedule();
    },
    { passive: true },
  );
  window.addEventListener(
    "scroll",
    () => {
      const rect = hero.getBoundingClientRect();
      if (rect.bottom < 0) return; // Hero já saiu da tela
      sy = Math.max(0, -rect.top);
      schedule();
    },
    { passive: true },
  );
})();

/* ---------- 3. pausa fora da tela ---------- */
let engine = null; // objeto 3D, criado mais abaixo
let heroVisible = true;

if ("IntersectionObserver" in window) {
  new IntersectionObserver(
    ([entry]) => {
      heroVisible = entry.isIntersecting;
      backdrop.toggleAttribute("data-paused", !heroVisible);
      starEl.toggleAttribute("data-paused", !heroVisible);
      engine?.setRunning(heroVisible);
    },
    { rootMargin: "120px" },
  ).observe(hero);
}

/* ---------- 4. objeto 3D ----------
   A biblioteca three.js vem no arquivo three.min.js (na mesma pasta),
   então funciona sem internet e abrindo o index.html com dois cliques.
   Ela só é baixada depois que a página terminou de carregar: o texto aparece
   primeiro e, enquanto isso, a estrela em SVG ocupa o lugar do 3D. */
function loadThree() {
  const s = document.createElement("script");
  s.src = document.body.dataset.threeSrc || "three.min.js"; // caminho vem do Django ({% static %})
  s.async = true;
  s.onload = loadStar;
  s.onerror = () => starEl.classList.add("is-failed");
  document.head.appendChild(s);
}
function whenIdle(fn) {
  if ("requestIdleCallback" in window) requestIdleCallback(fn, { timeout: 1500 });
  else setTimeout(fn, 200);
}
if (document.readyState === "complete") whenIdle(loadThree);
else window.addEventListener("load", () => whenIdle(loadThree), { once: true });

function loadStar() {
  try {
    const THREE = window.THREE;
    if (!THREE || !THREE.WebGLRenderer) throw new Error("three.min.js não foi carregado");
    engine = createStarScene(THREE, THREE.mergeVertices, starEl.querySelector(".sw-star__canvas"), {
      reducedMotion: reducedMQ.matches,
      onReady: () => starEl.classList.add("is-ready"),
    });
    engine.setRunning(heroVisible);
    reducedMQ.addEventListener("change", () => engine.setReducedMotion(reducedMQ.matches));
  } catch (err) {
    // navegador sem WebGL: fica a estrela em SVG, também flutuando
    console.warn("Objeto 3D indisponível, usando a versão em SVG.", err);
    starEl.classList.add("is-failed");
  }
}

/* ---- geometria da estrela de 6 pontas (contorno arredondado e oco) ---- */
function starOutline({ points = 6, outer = 1, inner = 0.64, tipRadius = 0.21, valleyRadius = 0.1, samples = 360 } = {}) {
  const total = points * 2;
  const verts = [];
  for (let k = 0; k < total; k++) {
    const a = Math.PI / 2 + (k * Math.PI) / points;
    const r = k % 2 === 0 ? outer : inner;
    verts.push({ x: Math.cos(a) * r, y: Math.sin(a) * r });
  }
  // arredonda cada vértice com um arco tangente às duas arestas
  const raw = [];
  for (let k = 0; k < total; k++) {
    const v = verts[k];
    const prev = verts[(k - 1 + total) % total];
    const next = verts[(k + 1) % total];
    const radius = k % 2 === 0 ? tipRadius : valleyRadius;
    const u1 = norm({ x: prev.x - v.x, y: prev.y - v.y });
    const u2 = norm({ x: next.x - v.x, y: next.y - v.y });
    const half = Math.acos(Math.min(1, Math.max(-1, u1.x * u2.x + u1.y * u2.y))) / 2;
    const d = radius / Math.tan(half);
    const bis = norm({ x: u1.x + u2.x, y: u1.y + u2.y });
    const c = { x: v.x + (bis.x * radius) / Math.sin(half), y: v.y + (bis.y * radius) / Math.sin(half) };
    const a1 = Math.atan2(v.y + u1.y * d - c.y, v.x + u1.x * d - c.x);
    const a2 = Math.atan2(v.y + u2.y * d - c.y, v.x + u2.x * d - c.x);
    let delta = a2 - a1;
    while (delta > Math.PI) delta -= Math.PI * 2;
    while (delta < -Math.PI) delta += Math.PI * 2;
    for (let s = 0; s <= 14; s++) {
      const a = a1 + (delta * s) / 14;
      raw.push({ x: c.x + Math.cos(a) * radius, y: c.y + Math.sin(a) * radius });
    }
  }
  return resample(raw, samples);
}

function offsetInward(outline, thickness) {
  const n = outline.length;
  return outline.map((p, i) => {
    const a = outline[(i - 1 + n) % n];
    const b = outline[(i + 1) % n];
    const t = norm({ x: b.x - a.x, y: b.y - a.y });
    return { x: p.x - t.y * thickness, y: p.y + t.x * thickness }; // contorno anti-horário: normal para dentro
  });
}

function resample(pts, count) {
  const closed = [...pts, pts[0]];
  const lens = [0];
  for (let i = 1; i < closed.length; i++) {
    lens.push(lens[i - 1] + Math.hypot(closed[i].x - closed[i - 1].x, closed[i].y - closed[i - 1].y));
  }
  const total = lens[lens.length - 1];
  const out = [];
  let j = 1;
  for (let k = 0; k < count; k++) {
    const target = (k / count) * total;
    while (lens[j] < target) j++;
    const f = (target - lens[j - 1]) / (lens[j] - lens[j - 1] || 1);
    out.push({
      x: closed[j - 1].x + (closed[j].x - closed[j - 1].x) * f,
      y: closed[j - 1].y + (closed[j].y - closed[j - 1].y) * f,
    });
  }
  return out;
}

function norm(v) {
  const l = Math.hypot(v.x, v.y) || 1;
  return { x: v.x / l, y: v.y / l };
}

/* ---- cena 3D ----
   Tudo que mexe no objeto acontece num único loop: flutuação, rotação sutil,
   inclinação lateral, parallax do mouse, reflexos girando, brilho interno
   pulsando, luzes de borda orbitando e sombra/reflexo acompanhando a altura. */
function createStarScene(THREE, mergeVertices, host, opts) {
  const TAU = Math.PI * 2;
  const FOV = 30;
  const easeOutCubic = (x) => 1 - Math.pow(1 - x, 3);

  // renderer
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.08;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
  const canvas = renderer.domElement;
  canvas.style.cssText = "width:100%;height:100%;display:block";
  host.appendChild(canvas);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(FOV, 1, 0.1, 60);

  // ambiente de reflexos gerado na hora (nenhuma imagem externa)
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene();
  envScene.add(
    new THREE.Mesh(new THREE.BoxGeometry(30, 30, 30), new THREE.MeshBasicMaterial({ color: 0x04090c, side: THREE.BackSide })),
  );
  const panel = (w, h, hex, power, x, y, z) => {
    const m = new THREE.Mesh(
      new THREE.PlaneGeometry(w, h),
      new THREE.MeshBasicMaterial({ color: new THREE.Color(hex).multiplyScalar(power), side: THREE.DoubleSide }),
    );
    m.position.set(x, y, z);
    m.lookAt(0, 0, 0);
    envScene.add(m);
  };
  panel(4.5, 1.1, 0xf2fffb, 10, 6, 7, 4); // softbox superior direita
  panel(1.2, 7, 0x00c58e, 6, -8, 0.5, 2); // faixa esmeralda à esquerda
  panel(9, 0.7, 0x2bffd0, 5, 0, -7, 3); // faixa do chão
  panel(1.4, 7, 0x087f68, 5, 5, -1, -7); // contraluz verde-escuro
  panel(1.4, 1.4, 0xeafff8, 12, -3, 4, 8); // brilho frontal pequeno
  panel(0.6, 6, 0x9bffe2, 8, 7, 0, 3); // filete lateral direito
  const envRT = pmrem.fromScene(envScene, 0.035);
  scene.environment = envRT.texture;
  envScene.traverse((o) => {
    if (o.isMesh) {
      o.geometry.dispose();
      o.material.dispose();
    }
  });

  // geometria: estrela oca extrudada com bordas chanfradas
  const outer = starOutline();
  const inner = offsetInward(outer, 0.075);
  const shape = new THREE.Shape(outer.map((p) => new THREE.Vector2(p.x, p.y)));
  shape.holes.push(new THREE.Path(inner.map((p) => new THREE.Vector2(p.x, p.y))));
  let geometry = new THREE.ExtrudeGeometry(shape, {
    depth: 0.5,
    steps: 1,
    bevelEnabled: true,
    bevelThickness: 0.03,
    bevelSize: 0.022,
    bevelSegments: 5,
    curveSegments: 1,
  });
  geometry.deleteAttribute("uv");
  geometry = mergeVertices(geometry, 1e-4); // normais suaves = reflexos contínuos
  geometry.computeVertexNormals();
  geometry.center();

  const material = new THREE.MeshPhysicalMaterial({
    color: 0x2ee6b0,
    metalness: 0.75,
    roughness: 0.05,
    transmission: 0.35, // um pouco de vidro
    thickness: 0.8,
    ior: 1.5,
    attenuationColor: new THREE.Color(0x00c58e),
    attenuationDistance: 0.6,
    clearcoat: 1, // verniz: brilho branco nas bordas
    clearcoatRoughness: 0.02,
    iridescence: 0.3, // leve variação esverdeada/ciano nos reflexos
    iridescenceIOR: 1.5,
    specularIntensity: 1,
    specularColor: new THREE.Color(0xd8fff4),
    emissive: new THREE.Color(0x003828),
    emissiveIntensity: 0.4,
    envMapIntensity: 1.8,
  });

  const star = new THREE.Mesh(geometry, material);
  const floatGroup = new THREE.Group();
  floatGroup.add(star);
  scene.add(floatGroup);
  const BASE = { x: 0.22, y: -0.62, z: 0.1 }; // ângulo de repouso (mostra a lateral da fita)

  // brilho interno visto através do vazado + halo
  const core = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: radialTexture(THREE, [
        [0, "rgba(190,255,236,1)"],
        [0.22, "rgba(40,240,180,0.7)"],
        [0.55, "rgba(0,197,142,0.18)"],
        [0.9, "rgba(0,197,142,0)"],
      ]),
      blending: THREE.AdditiveBlending,
      transparent: true,
      depthWrite: false,
    }),
  );
  core.scale.set(1.8, 1.8, 1);
  core.position.z = -0.12;
  floatGroup.add(core);

  const halo = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: radialTexture(THREE, [
        [0, "rgba(0,197,142,0.55)"],
        [0.45, "rgba(8,127,104,0.16)"],
        [0.85, "rgba(8,127,104,0)"],
      ]),
      blending: THREE.AdditiveBlending,
      transparent: true,
      depthWrite: false,
    }),
  );
  halo.scale.set(2.6, 2.6, 1);
  halo.position.z = -0.6;
  floatGroup.add(halo);

  // sombra de contato e reflexo verde no chão
  const FLOOR_Y = -1.24;
  const shadow = new THREE.Mesh(
    new THREE.PlaneGeometry(2.2, 1.6),
    new THREE.MeshBasicMaterial({
      map: radialTexture(THREE, [
        [0, "rgba(0,8,6,0.85)"],
        [0.5, "rgba(0,8,6,0.35)"],
        [0.9, "rgba(0,8,6,0)"],
      ]),
      transparent: true,
      depthWrite: false,
    }),
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = FLOOR_Y;
  scene.add(shadow);

  const pool = new THREE.Mesh(
    new THREE.PlaneGeometry(3, 2),
    new THREE.MeshBasicMaterial({
      map: radialTexture(THREE, [
        [0, "rgba(60,255,200,0.55)"],
        [0.35, "rgba(0,197,142,0.2)"],
        [0.85, "rgba(0,197,142,0)"],
      ]),
      blending: THREE.AdditiveBlending,
      transparent: true,
      depthWrite: false,
    }),
  );
  pool.rotation.x = -Math.PI / 2;
  pool.position.y = FLOOR_Y - 0.01;
  scene.add(pool);

  // luzes
  scene.add(new THREE.AmbientLight(0x0d2c26, 0.3));
  const key = new THREE.DirectionalLight(0xdffff5, 1.7);
  key.position.set(3, 4, 5);
  scene.add(key);
  const rimA = new THREE.PointLight(0x19ffb8, 20, 12, 2); // luzes de borda que orbitam
  const rimB = new THREE.PointLight(0x8affea, 11, 12, 2);
  const innerLight = new THREE.PointLight(0x3dffc4, 9, 3.2, 2); // ilumina as paredes internas
  scene.add(rimA, rimB);
  floatGroup.add(innerLight);

  // estado do loop
  let reduced = opts.reducedMotion;
  let wanted = false;
  let running = false;
  let raf = 0;
  let last = 0;
  let t = reduced ? 2 : 0;
  let intro = reduced ? 1 : 0;
  let ampWorld = 0.05;
  const smooth = { x: 0, y: 0 };

  function resize() {
    const w = Math.max(1, host.clientWidth);
    const h = Math.max(1, host.clientHeight);
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    const tanHalf = Math.tan(((FOV / 2) * Math.PI) / 180);
    const dist = Math.max(1.45 / tanHalf, 1.32 / (tanHalf * camera.aspect)); // enquadra em qualquer proporção
    camera.position.set(0, 0.5, dist);
    camera.lookAt(0, -0.12, 0);
    camera.updateProjectionMatrix();
    const pxPerUnit = h / (2 * dist * tanHalf);
    ampWorld = (w < 520 ? 9 : 14) / pxPerUnit; // flutuação de 14 px (9 px no celular)
    if (!running) renderFrame(0);
  }
  const ro = new ResizeObserver(resize);
  ro.observe(host);

  function update(dt) {
    if (!reduced) t += dt;
    intro = reduced ? 1 : Math.min(1, intro + dt / 1.9);
    const ei = easeOutCubic(intro);

    // mouse suavizado
    const k = 1 - Math.exp(-dt * 2.4);
    smooth.x += ((reduced ? 0 : pointer.x) - smooth.x) * k;
    smooth.y += ((reduced ? 0 : pointer.y) - smooth.y) * k;

    // flutuação: soma de senos com período comum de 8 s (sem salto no fim do ciclo)
    const fy = 0.82 * Math.sin((TAU * t) / 8) + 0.18 * Math.sin((TAU * t) / 4 + 0.6);
    floatGroup.position.y = fy * ampWorld - (1 - ei) * 0.32;
    floatGroup.position.x = smooth.x * 0.07;
    floatGroup.scale.setScalar(0.88 + 0.12 * ei);

    // rotação de poucos graus em cada eixo, com períodos diferentes
    star.rotation.set(
      BASE.x + 0.06 * Math.sin((TAU * t) / 12 + 1.1) + smooth.y * 0.1,
      BASE.y + 0.11 * Math.sin((TAU * t) / 16 + 0.3) + smooth.x * 0.16,
      BASE.z + 0.045 * Math.sin((TAU * t) / 8 + 2.0),
    );

    // brilho e reflexos variando discretamente
    const pulse = 0.5 + 0.5 * Math.sin((TAU * t) / 6);
    material.emissiveIntensity = 0.42 + 0.22 * pulse;
    innerLight.intensity = (7 + 3.5 * pulse) * ei;
    core.material.opacity = (0.8 + 0.2 * pulse) * ei;
    halo.material.opacity = (0.3 + 0.1 * pulse) * ei;
    scene.environmentRotation.y = 0.45 * Math.sin((TAU * t) / 20);
    scene.environmentRotation.x = 0.12 * Math.sin((TAU * t) / 14 + 0.8);

    // luzes de borda orbitando: o destaque percorre o acabamento
    rimA.position.set(Math.cos((TAU * t) / 14) * 3.1, 1.1 + Math.sin((TAU * t) / 10) * 1.3, 2.4);
    rimB.position.set(Math.cos((TAU * t) / 14 + Math.PI) * 2.9, -0.7 + Math.sin((TAU * t) / 12 + 1) * 1.1, 2.1);

    // sombra e reflexo acompanham a altura (subiu = sombra menor e mais clara)
    const h01 = (fy + 1) / 2;
    shadow.scale.setScalar(1.06 - 0.14 * h01);
    shadow.material.opacity = (0.62 - 0.2 * h01) * ei;
    pool.scale.setScalar(1.02 - 0.08 * h01);
    pool.material.opacity = (0.75 - 0.15 * h01 + 0.1 * pulse) * ei;
    shadow.position.x = pool.position.x = floatGroup.position.x;
  }

  let readySent = false;
  function renderFrame(dt) {
    update(dt);
    renderer.render(scene, camera);
    if (!readySent) {
      readySent = true;
      opts.onReady?.();
    }
  }

  function loop(now) {
    raf = requestAnimationFrame(loop);
    const dt = Math.min((now - last) / 1000, 1 / 20);
    last = now;
    renderFrame(dt);
  }

  // roda só com a Hero visível, aba ativa e sem "reduzir movimento"
  function sync() {
    const shouldRun = wanted && !reduced && !document.hidden;
    if (shouldRun === running) return;
    running = shouldRun;
    if (running) {
      last = performance.now();
      raf = requestAnimationFrame(loop);
    } else {
      cancelAnimationFrame(raf);
    }
  }
  document.addEventListener("visibilitychange", sync);

  resize();

  return {
    setRunning(on) {
      wanted = on;
      sync();
    },
    setReducedMotion(r) {
      reduced = r;
      if (r) {
        t = 2;
        intro = 1;
      }
      sync();
      if (!running) renderFrame(0);
    },
  };
}

function radialTexture(THREE, stops) {
  const size = 256;
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const ctx = c.getContext("2d");
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  stops.forEach(([o, col]) => g.addColorStop(o, col));
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

/* ---------- 5. navegação fixa e destaque da seção atual ---------- */
(function navegacao() {
  const nav = document.querySelector(".nav");
  const heroInner = document.querySelector(".hero__inner");
  const links = [...document.querySelectorAll('.nav__links a[href^="#"]')];
  const secoes = links
    .map((a) => document.querySelector(a.getAttribute("href")))
    .filter((el) => el && !el.hidden);

  // fixa a navegação depois que a original sai da tela
  let fixa = false;
  const atualizarFixa = () => {
    const deveFixar = window.scrollY > nav.offsetHeight + 240;
    if (deveFixar === fixa) return;
    fixa = deveFixar;
    // reserva o espaço da navegação para o conteúdo não "pular"
    heroInner.style.paddingTop = fixa ? nav.offsetHeight + "px" : "";
    nav.classList.toggle("is-fixa", fixa);
    if (!fixa) setMenu(false);
  };

  // marca no menu a seção que está no meio da tela
  const atualizarAtual = () => {
    const meio = window.innerHeight * 0.4;
    let atual = secoes[0];
    for (const sec of secoes) {
      if (sec.getBoundingClientRect().top <= meio) atual = sec;
    }
    // no fim da página, a última seção é a atual
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) {
      atual = secoes[secoes.length - 1];
    }
    links.forEach((a) => {
      if (a.getAttribute("href") === "#" + atual.id) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  };

  let frame = 0;
  const onScroll = () => {
    if (frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      atualizarFixa();
      atualizarAtual();
    });
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  onScroll();
})();

/* ---------- 6. animação de entrada das seções ---------- */
(function revelar() {
  const itens = document.querySelectorAll("[data-revelar]");
  if (!("IntersectionObserver" in window) || reducedMQ.matches) {
    itens.forEach((el) => el.classList.add("is-visivel"));
    return;
  }
  // itens lado a lado entram um pouco depois do outro
  document.querySelectorAll(".pilares, .etapas, .planos, .projetos, .depoimentos").forEach((grupo) => {
    grupo.querySelectorAll(":scope > [data-revelar]").forEach((el, i) => el.style.setProperty("--atraso", i * 0.08 + "s"));
  });
  const io = new IntersectionObserver(
    (entradas) => {
      entradas.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add("is-visivel");
        io.unobserve(e.target);
      });
    },
    { rootMargin: "0px 0px -10% 0px" },
  );
  itens.forEach((el) => io.observe(el));
})();

/* ---------- 7. contato ----------
   Os links de WhatsApp já vêm prontos do Django. Aqui ficam só os detalhes de uso. */

// esconde o botão flutuante quando a seção de contato está na tela
(function botaoFlutuante() {
  const botao = document.querySelector(".whatsapp-flutuante");
  const contato = document.getElementById("contato");
  if (!botao || !contato || !("IntersectionObserver" in window)) return;
  new IntersectionObserver(([e]) => botao.classList.toggle("is-oculto", e.isIntersecting), {
    threshold: 0.25,
  }).observe(contato);
})();

// botões dos planos já escolhem o serviço no formulário
document.querySelectorAll("[data-servico]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const select = document.getElementById("f-servico");
    if (select) select.value = btn.dataset.servico;
  });
});

// formulário: confere os campos antes de enviar (o Django valida de novo no servidor)
(function formulario() {
  const form = document.getElementById("formulario-contato");
  if (!form) return;
  const erro = document.getElementById("formulario-erro");
  const nomeDoCampo = (c) => form.querySelector(`label[for="${c.id}"]`).childNodes[0].textContent.trim();

  form.addEventListener("submit", (e) => {
    const campos = [...form.querySelectorAll("[required]")];
    const vazios = campos.filter((c) => !c.value.trim());
    campos.forEach((c) => {
      if (vazios.includes(c)) c.setAttribute("aria-invalid", "true");
    });
    if (!vazios.length) return; // tudo certo: segue o envio normal

    e.preventDefault();
    erro.textContent = "Preencha os campos: " + vazios.map(nomeDoCampo).join(", ") + ".";
    erro.hidden = false;
    vazios[0].focus();
  });

  form.addEventListener("input", (e) => {
    if (e.target.value.trim()) e.target.removeAttribute("aria-invalid");
  });
})();

// depois de enviar: leva o foco para a confirmação (leitores de tela anunciam)
document.getElementById("pedido-enviado")?.focus({ preventScroll: true });

// ano atual no rodapé
document.querySelectorAll("[data-ano]").forEach((el) => (el.textContent = new Date().getFullYear()));
