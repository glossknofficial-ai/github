/* Real-time Power Cleanse bottle for the product gallery's 3D view (loads on first open). */
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

let started = false;
addEventListener("glosskn:3d", () => { if (!started) { started = true; start(document.getElementById("s3d")); } });

function start(host) {
  if (!host) return;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  host.prepend(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 50); camera.position.set(0, 0.15, 7.6);
  scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
  const key = new THREE.DirectionalLight(0xffffff, 1.4); key.position.set(-3, 4, 5); scene.add(key);
  const rim = new THREE.DirectionalLight(0xefe9f1, 2.2); rim.position.set(4, 2, -3); scene.add(rim);

  // label: wording and layout of the printed Power Cleanse label
  const lc = document.createElement("canvas"); lc.width = 1400; lc.height = 1000;
  const tex = new THREE.CanvasTexture(lc); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const logo = new Image(); logo.src = "assets/logo.png";
  const draw = () => {
    const g = lc.getContext("2d"), ls = v => { if ("letterSpacing" in g) g.letterSpacing = v; };
    g.fillStyle = "#FFFFFF"; g.fillRect(0, 0, 1400, 1000);
    g.strokeStyle = "#404040"; g.lineWidth = 4; g.strokeRect(390, 70, 620, 860);
    if (logo.complete && logo.naturalWidth) { const w = 470, h = w * logo.naturalHeight / logo.naturalWidth; g.drawImage(logo, 700 - w / 2, 190, w, h); }
    g.textAlign = "center"; g.fillStyle = "#000000";
    g.font = "600 56px Jost, Helvetica, Arial, sans-serif"; ls("2px"); g.fillText("POWER", 700, 500); g.fillText("CLEANSE", 700, 562);
    g.font = "500 27px Jost, Helvetica, Arial, sans-serif"; ls("1px"); g.fillText("MAKE-UP REMOVING", 700, 625); g.fillText("FACE WASH", 700, 660);
    g.font = "500 25px Jost, Helvetica, Arial, sans-serif"; g.fillText("GENTLE ON EYES • EYELASH FRIENDLY", 700, 770); g.fillText("100 ml | 3.38 Fl/oz", 700, 810);
    tex.needsUpdate = true;
  };
  draw(); logo.onload = draw; document.fonts?.load("600 56px Jost").then(draw).catch(() => {});

  const Y = 1.25, LIFT = 1.74 * (Y - 1);
  const lathe = pts => new THREE.LatheGeometry(new THREE.SplineCurve(pts.map(([r, y]) => new THREE.Vector2(r, y * Y))).getPoints(90), 96);
  const bottle = new THREE.Group(), inner = new THREE.Group(); bottle.add(inner); inner.position.y = -1.42; scene.add(bottle);
  const shell = new THREE.Mesh(lathe([[0, 0], [0.48, 0], [0.58, 0.02], [0.62, 0.09], [0.625, 0.3], [0.625, 1.1], [0.6, 1.28], [0.5, 1.44], [0.33, 1.55], [0.22, 1.6], [0.2, 1.66], [0.2, 1.74]]),
    new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.05, transparent: true, opacity: 0.3, clearcoat: 1, envMapIntensity: 1.6, depthWrite: false, side: THREE.DoubleSide }));
  shell.renderOrder = 3;
  const cream = new THREE.Mesh(lathe([[0, 0.03], [0.5, 0.03], [0.585, 0.08], [0.6, 0.3], [0.6, 1.1], [0.585, 1.22], [0.5, 1.3], [0.2, 1.33], [0, 1.33]]),
    new THREE.MeshPhysicalMaterial({ color: 0xf8f5f6, roughness: 0.45, sheen: 0.5, sheenColor: new THREE.Color(0xefe9f1) }));
  const LT = 2.15, label = new THREE.Mesh(new THREE.CylinderGeometry(0.632, 0.632, 0.98 * Y, 96, 1, true, -LT / 2, LT), new THREE.MeshPhysicalMaterial({ map: tex, roughness: 0.4, clearcoat: 0.4 }));
  label.position.y = 0.66 * Y; label.renderOrder = 2;
  inner.add(cream, label, shell);
  const pm = new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.28, clearcoat: 0.8 });
  const part = (geo, y, x = 0, rz = 0) => { const m = new THREE.Mesh(geo, pm); m.position.set(x, y + LIFT, 0); m.rotation.z = rz; inner.add(m); return m; };
  part(new THREE.CylinderGeometry(0.255, 0.265, 0.24, 64), 1.82);
  part(new THREE.CylinderGeometry(0.1, 0.1, 0.22, 32), 2.03);
  part(new THREE.CylinderGeometry(0.2, 0.21, 0.32, 64), 2.28);
  part(new THREE.CylinderGeometry(0.065, 0.07, 0.42, 32), 2.37, 0.36, Math.PI / 2);
  part(new THREE.SphereGeometry(0.065, 24, 16), 2.37, 0.57);

  let rot = -0.4, vel = 0, drag = false, lx = 0, spin = 0;
  const el = renderer.domElement;
  el.addEventListener("pointerdown", e => { drag = true; lx = e.clientX; el.setPointerCapture(e.pointerId); });
  el.addEventListener("pointermove", e => { if (drag) { const d = (e.clientX - lx) * 0.012; rot += d; vel = d; lx = e.clientX; } });
  const end = () => { drag = false; }; el.addEventListener("pointerup", end); el.addEventListener("pointercancel", end);
  addEventListener("glosskn:add", e => { if (e.detail === "cleanse") spin += Math.PI * 2; });
  const size = () => { const w = host.clientWidth, h = host.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); };
  new ResizeObserver(size).observe(host); size();
  let visible = true; new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(host);
  const clock = new THREE.Clock();
  (function frame() {
    requestAnimationFrame(frame); if (!visible) return;
    const dt = Math.min(clock.getDelta(), 0.05), t = clock.elapsedTime;
    if (!drag) { vel *= 0.94; rot += vel + (reduce ? 0 : dt * 0.25); }
    spin *= 0.93;
    bottle.rotation.set(0.05, rot + spin, 0); bottle.position.y = reduce ? 0 : Math.sin(t * 1.1) * 0.05;
    renderer.render(scene, camera);
  })();
}
