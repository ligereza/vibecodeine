/*! 3d-scene.js — Three.js procedural mesh for "MALLA REACTIVA" */
document.addEventListener('DOMContentLoaded', initScene);

function initScene() {
  const container = document.getElementById('canvas');
  if (!container || typeof THREE === 'undefined') return;

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x0b0a09, 0.0015);

  const camera = new THREE.PerspectiveCamera(72, innerWidth / innerHeight, 0.1, 1000);
  camera.position.set(0, 50, 150);
  camera.lookAt(0, 0, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  const segments = innerWidth > 768 ? 140 : 70;
  const geo = new THREE.PlaneGeometry(420, 420, segments, segments);
  geo.rotateX(-Math.PI / 2);

  const pos = geo.attributes.position;
  const vertex = new THREE.Vector3();
  const original = [];
  for (let i = 0; i < pos.count; i++) {
    vertex.fromBufferAttribute(pos, i);
    original.push(vertex.clone());
  }

  const mat = new THREE.MeshStandardMaterial({
    color: 0xf4f1ec, wireframe: true, emissive: 0x111111,
    roughness: 0.85, metalness: 0.15,
  });
  const mesh = new THREE.Mesh(geo, mat);
  scene.add(mesh);

  scene.add(new THREE.AmbientLight(0x404040));
  const dir = new THREE.DirectionalLight(0xffffff, 0.9);
  dir.position.set(0, 100, 50);
  scene.add(dir);
  const point = new THREE.PointLight(0xf4f1ec, 1.4, 220);
  scene.add(point);

  const simplex = new SimplexNoise();
  let time = 0, mx = 0, my = 0, scrollY = window.scrollY;

  addEventListener('mousemove', e => { mx = e.clientX - innerWidth / 2; my = e.clientY - innerHeight / 2; });
  addEventListener('scroll', () => { scrollY = window.scrollY; }, { passive: true });

  const clock = new THREE.Clock();
  function tick() {
    requestAnimationFrame(tick);
    time += clock.getDelta() * 0.5;

    mesh.rotation.y += 0.05 * (mx * 0.0005 - mesh.rotation.y);
    mesh.rotation.x += 0.05 * (my * 0.0005 - mesh.rotation.x);
    point.position.x += (mx * 0.5 - point.position.x) * 0.05;
    point.position.z += (-my * 0.5 - point.position.z) * 0.05;
    point.position.y = 30;

    const factor = Math.min(scrollY / innerHeight, 1.0);
    const intensity = 10 + factor * 30;
    const speed = 0.015 + factor * 0.02;

    for (let i = 0; i < pos.count; i++) {
      const o = original[i];
      const n = simplex.noise3D(o.x * speed + time, o.z * speed + time, time * 0.5);
      pos.setY(i, o.y + n * intensity);
    }
    pos.needsUpdate = true;
    geo.computeVertexNormals();

    camera.position.y = 50 - scrollY * 0.05;
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
  }
  tick();

  addEventListener('resize', () => {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
  });
}
