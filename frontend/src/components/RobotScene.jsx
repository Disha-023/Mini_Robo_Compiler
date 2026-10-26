import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

// Convert 2D robot grid coordinates (x, y) to Three.js (X, Y_elevation, Z)
// Robot coords: North = +Y, East = +X, South = -Y, West = -X
// Three.js coords: Y is UP. North = -Z, East = +X, South = +Z, West = -X
function gridToThree(x, y, elevation = 0) {
  const SCALE = 2.0; // 1 robot step = 2 Three.js world units
  return new THREE.Vector3(x * SCALE, elevation, -y * SCALE);
}

export default function RobotScene({
  history = [],
  finalState = null,
  playbackState, // { isPlaying, currentEventIndex, speedMultiplier }
  onProgressUpdate,
  onPlaybackComplete,
}) {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const controlsRef = useRef(null);
  const robotGroupRef = useRef(null);
  const wheelsRef = useRef([]);
  const trailsGroupRef = useRef(null);
  const animFrameIdRef = useRef(null);

  // Keep latest props in refs so the animation render loop never has stale closures
  const historyRef = useRef(history);
  const playbackStateRef = useRef(playbackState);
  const onProgressUpdateRef = useRef(onProgressUpdate);
  const onPlaybackCompleteRef = useRef(onPlaybackComplete);

  useEffect(() => {
    historyRef.current = history;
  }, [history]);

  useEffect(() => {
    playbackStateRef.current = playbackState;
  }, [playbackState]);

  useEffect(() => {
    onProgressUpdateRef.current = onProgressUpdate;
  }, [onProgressUpdate]);

  useEffect(() => {
    onPlaybackCompleteRef.current = onPlaybackComplete;
  }, [onPlaybackComplete]);

  // Animation timeline state
  const timelineRef = useRef({
    eventIdx: 0,
    eventProgress: 0,
    currentPos: new THREE.Vector3(0, 0, 0),
    currentYaw: 0, // In radians. 0 = North (-Z), -PI/2 = East (+X)
    startPos: new THREE.Vector3(0, 0, 0),
    targetPos: new THREE.Vector3(0, 0, 0),
    startYaw: 0,
    targetYaw: 0,
    penDown: false,
    speed: 1,
    isComplete: false,
  });

  const [cameraMode, setCameraMode] = useState('orbit');

  // Reset simulation animation state
  const resetSimulation = () => {
    timelineRef.current = {
      eventIdx: 0,
      eventProgress: 0,
      currentPos: new THREE.Vector3(0, 0, 0),
      currentYaw: 0,
      startPos: new THREE.Vector3(0, 0, 0),
      targetPos: new THREE.Vector3(0, 0, 0),
      startYaw: 0,
      targetYaw: 0,
      penDown: false,
      speed: 1,
      isComplete: false,
    };

    if (robotGroupRef.current) {
      robotGroupRef.current.position.set(0, 0, 0);
      robotGroupRef.current.rotation.y = 0;
    }

    // Clear previous drawn trails
    if (trailsGroupRef.current) {
      while (trailsGroupRef.current.children.length > 0) {
        const obj = trailsGroupRef.current.children[0];
        trailsGroupRef.current.remove(obj);
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) obj.material.dispose();
      }
    }
  };

  // Re-initialize when history changes
  useEffect(() => {
    resetSimulation();
  }, [history]);

  // Initialize Three.js Scene
  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // 1. Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x070b14);
    scene.fog = new THREE.FogExp2(0x070b14, 0.012);
    sceneRef.current = scene;

    // 2. Camera
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(16, 22, 26);
    cameraRef.current = camera;

    // 3. Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // 4. OrbitControls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.maxPolarAngle = Math.PI / 2 - 0.05; // Stay above ground plane
    controls.minDistance = 4;
    controls.maxDistance = 150;
    controls.target.set(0, 0.5, 0);
    controlsRef.current = controls;

    // 5. Lighting
    const ambientLight = new THREE.AmbientLight(0x283858, 1.4);
    scene.add(ambientLight);

    const hemiLight = new THREE.HemisphereLight(0x38bdf8, 0x0f172a, 0.9);
    scene.add(hemiLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.8);
    dirLight.position.set(24, 40, 24);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 1;
    dirLight.shadow.camera.far = 120;
    const d = 35;
    dirLight.shadow.camera.left = -d;
    dirLight.shadow.camera.right = d;
    dirLight.shadow.camera.top = d;
    dirLight.shadow.camera.bottom = -d;
    scene.add(dirLight);

    // Accent platform glow
    const pointLight = new THREE.PointLight(0x06b6d4, 2.5, 45);
    pointLight.position.set(0, 10, 0);
    scene.add(pointLight);

    // 6. Build Environment & Grid
    buildEnvironment(scene);

    // 7. Trails Group
    const trailsGroup = new THREE.Group();
    scene.add(trailsGroup);
    trailsGroupRef.current = trailsGroup;

    // 8. 3D Procedural Robot Rover
    const robotGroup = buildRobotRover();
    scene.add(robotGroup);
    robotGroupRef.current = robotGroup;

    // Handle Resize
    const handleResize = () => {
      if (!containerRef.current || !rendererRef.current || !cameraRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      cameraRef.current.aspect = w / h;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    // Main Animation Render Loop
    let lastTime = performance.now();
    const animate = (currentTime) => {
      animFrameIdRef.current = requestAnimationFrame(animate);
      const deltaSec = Math.min((currentTime - lastTime) / 1000, 0.1);
      lastTime = currentTime;

      // Update simulation physics using fresh ref values
      updatePlayback(deltaSec);

      // Follow camera if enabled
      if (cameraMode === 'follow' && robotGroupRef.current && controlsRef.current) {
        const rPos = robotGroupRef.current.position;
        controlsRef.current.target.lerp(new THREE.Vector3(rPos.x, rPos.y + 0.8, rPos.z), 0.1);
      }

      controls.update();
      renderer.render(scene, camera);
    };

    animFrameIdRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animFrameIdRef.current) cancelAnimationFrame(animFrameIdRef.current);
      renderer.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  function buildEnvironment(scene) {
    // Ground plane
    const planeGeo = new THREE.PlaneGeometry(240, 240);
    const planeMat = new THREE.MeshStandardMaterial({
      color: 0x090d18,
      roughness: 0.9,
      metalness: 0.1,
    });
    const floor = new THREE.Mesh(planeGeo, planeMat);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -0.01;
    floor.receiveShadow = true;
    scene.add(floor);

    // Primary Neon Grid (2 units per cell = 1 robot step)
    const gridHelper = new THREE.GridHelper(200, 100, 0x06b6d4, 0x182234);
    gridHelper.position.y = 0.01;
    scene.add(gridHelper);

    // Origin Launch Pad
    const padGeo = new THREE.CylinderGeometry(1.6, 1.7, 0.06, 32);
    const padMat = new THREE.MeshStandardMaterial({
      color: 0x0369a1,
      emissive: 0x0284c7,
      emissiveIntensity: 0.35,
      metalness: 0.8,
      roughness: 0.3,
    });
    const pad = new THREE.Mesh(padGeo, padMat);
    pad.position.set(0, 0.03, 0);
    pad.receiveShadow = true;
    scene.add(pad);

    // Glowing Neon Ring around Origin
    const ringGeo = new THREE.RingGeometry(1.75, 1.9, 32);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x22d3ee,
      side: THREE.DoubleSide,
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = -Math.PI / 2;
    ring.position.y = 0.04;
    scene.add(ring);

    // Primary Coordinate Axis Guides
    const createAxisLine = (start, end, colorHex) => {
      const mat = new THREE.LineBasicMaterial({ color: colorHex, linewidth: 3 });
      const geo = new THREE.BufferGeometry().setFromPoints([start, end]);
      return new THREE.Line(geo, mat);
    };
    scene.add(createAxisLine(new THREE.Vector3(0, 0.05, 0), new THREE.Vector3(0, 0.05, -40), 0x22d3ee)); // North +Y
    scene.add(createAxisLine(new THREE.Vector3(0, 0.05, 0), new THREE.Vector3(40, 0.05, 0), 0xf97316)); // East +X
  }

  function buildRobotRover() {
    const group = new THREE.Group();
    wheelsRef.current = [];

    // Materials
    const chassisMat = new THREE.MeshStandardMaterial({
      color: 0xf1f5f9,
      metalness: 0.6,
      roughness: 0.25,
    });
    const darkAccentMat = new THREE.MeshStandardMaterial({
      color: 0x0f172a,
      metalness: 0.8,
      roughness: 0.3,
    });
    const cyanGlowMat = new THREE.MeshStandardMaterial({
      color: 0x06b6d4,
      emissive: 0x00f0ff,
      emissiveIntensity: 1.3,
      roughness: 0.1,
    });
    const wheelMat = new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      metalness: 0.2,
      roughness: 0.8,
    });
    const rimMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      metalness: 0.9,
      roughness: 0.2,
    });

    // 1. Chassis
    const chassisGeo = new THREE.BoxGeometry(1.5, 0.6, 2.0);
    const chassis = new THREE.Mesh(chassisGeo, chassisMat);
    chassis.position.y = 0.65;
    chassis.castShadow = true;
    chassis.receiveShadow = true;
    group.add(chassis);

    // Glowing side trim
    const sideTrimGeo = new THREE.BoxGeometry(1.54, 0.16, 1.6);
    const sideTrim = new THREE.Mesh(sideTrimGeo, cyanGlowMat);
    sideTrim.position.y = 0.65;
    group.add(sideTrim);

    // 2. Robot Head / Turret
    const headGroup = new THREE.Group();
    headGroup.position.set(0, 1.15, -0.3);

    const headGeo = new THREE.BoxGeometry(0.9, 0.5, 0.8);
    const head = new THREE.Mesh(headGeo, darkAccentMat);
    head.castShadow = true;
    headGroup.add(head);

    // Glowing Cyan Visor Eyes (Front is -Z)
    const visorGeo = new THREE.BoxGeometry(0.7, 0.16, 0.08);
    const visor = new THREE.Mesh(visorGeo, cyanGlowMat);
    visor.position.set(0, 0.05, -0.42);
    headGroup.add(visor);

    // Visor Point Light
    const eyeLight = new THREE.PointLight(0x00f0ff, 1.8, 6);
    eyeLight.position.set(0, 0.05, -0.6);
    headGroup.add(eyeLight);

    // Antenna
    const antennaGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.4, 8);
    const antenna = new THREE.Mesh(antennaGeo, darkAccentMat);
    antenna.position.set(0.3, 0.4, 0.2);
    headGroup.add(antenna);

    const beaconGeo = new THREE.SphereGeometry(0.06, 16, 16);
    const beaconMat = new THREE.MeshStandardMaterial({
      color: 0xec4899,
      emissive: 0xf43f5e,
      emissiveIntensity: 1.5,
    });
    const beacon = new THREE.Mesh(beaconGeo, beaconMat);
    beacon.position.set(0.3, 0.6, 0.2);
    headGroup.add(beacon);

    group.add(headGroup);

    // 3. Direction Indicator Arrow on Chassis (Points forward to -Z)
    const arrowShape = new THREE.Shape();
    arrowShape.moveTo(0, 0.4);
    arrowShape.lineTo(0.25, -0.2);
    arrowShape.lineTo(0.08, -0.2);
    arrowShape.lineTo(0.08, -0.4);
    arrowShape.lineTo(-0.08, -0.4);
    arrowShape.lineTo(-0.08, -0.2);
    arrowShape.lineTo(-0.25, -0.2);
    arrowShape.closePath();

    const arrowGeo = new THREE.ExtrudeGeometry(arrowShape, { depth: 0.04, bevelEnabled: false });
    const arrowMesh = new THREE.Mesh(arrowGeo, cyanGlowMat);
    arrowMesh.rotation.x = -Math.PI / 2;
    arrowMesh.rotation.z = Math.PI; // Point towards -Z
    arrowMesh.position.set(0, 0.98, 0.3);
    group.add(arrowMesh);

    // 4. Wheels
    const wheelPositions = [
      { x: -0.9, y: 0.35, z: -0.65 },
      { x: 0.9, y: 0.35, z: -0.65 },
      { x: -0.9, y: 0.35, z: 0.65 },
      { x: 0.9, y: 0.35, z: 0.65 },
    ];

    wheelPositions.forEach((pos) => {
      const wheelGroup = new THREE.Group();
      wheelGroup.position.set(pos.x, pos.y, pos.z);

      const tireGeo = new THREE.CylinderGeometry(0.35, 0.35, 0.28, 24);
      const tire = new THREE.Mesh(tireGeo, wheelMat);
      tire.rotation.z = Math.PI / 2;
      tire.castShadow = true;
      wheelGroup.add(tire);

      const rimGeo = new THREE.CylinderGeometry(0.18, 0.18, 0.3, 16);
      const rim = new THREE.Mesh(rimGeo, rimMat);
      rim.rotation.z = Math.PI / 2;
      wheelGroup.add(rim);

      group.add(wheelGroup);
      wheelsRef.current.push(wheelGroup);
    });

    // 5. Headlight Spotlights
    const leftHeadlight = new THREE.SpotLight(0xa5f3fc, 3.5, 16, Math.PI / 7, 0.4, 1);
    leftHeadlight.position.set(-0.45, 0.65, -0.9);
    leftHeadlight.target.position.set(-0.45, 0, -6);
    group.add(leftHeadlight);
    group.add(leftHeadlight.target);

    const rightHeadlight = new THREE.SpotLight(0xa5f3fc, 3.5, 16, Math.PI / 7, 0.4, 1);
    rightHeadlight.position.set(0.45, 0.65, -0.9);
    rightHeadlight.target.position.set(0.45, 0, -6);
    group.add(rightHeadlight);
    group.add(rightHeadlight.target);

    group.position.set(0, 0, 0);
    return group;
  }

  // Draw glowing cyan ribbon segment on the ground
  function addTrailSegment(p1, p2) {
    if (!trailsGroupRef.current) return;
    const dir = new THREE.Vector3().subVectors(p2, p1);
    const len = dir.length();
    if (len < 0.001) return;

    const ribbonGeo = new THREE.BoxGeometry(0.2, 0.04, len);
    const ribbonMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
    });
    const ribbon = new THREE.Mesh(ribbonGeo, ribbonMat);

    const mid = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
    ribbon.position.set(mid.x, 0.03, mid.z);
    ribbon.lookAt(p2.x, 0.03, p2.z);
    trailsGroupRef.current.add(ribbon);
  }

  // Kinematic Playback Engine
  function updatePlayback(deltaSec) {
    const historyList = historyRef.current || [];
    const state = playbackStateRef.current || {};
    const isPlaying = state.isPlaying ?? false;
    const speedMult = state.speedMultiplier ?? 1.0;
    const t = timelineRef.current;

    if (historyList.length === 0) {
      if (robotGroupRef.current) {
        robotGroupRef.current.position.set(0, 0, 0);
        robotGroupRef.current.rotation.y = 0;
      }
      return;
    }

    if (!isPlaying) {
      return; // Paused
    }

    if (t.eventIdx >= historyList.length) {
      if (!t.isComplete) {
        t.isComplete = true;
        if (onPlaybackCompleteRef.current) onPlaybackCompleteRef.current();
      }
      return;
    }

    const event = historyList[t.eventIdx];
    const eventType = event.type;

    // Report live telemetry to dashboard
    if (onProgressUpdateRef.current) {
      onProgressUpdateRef.current({
        eventIndex: t.eventIdx,
        totalEvents: historyList.length,
        currentEvent: event,
        progressFraction: (t.eventIdx + t.eventProgress) / Math.max(historyList.length, 1),
        currentPos: {
          x: Math.round(t.currentPos.x / 2.0),
          y: Math.round(-t.currentPos.z / 2.0),
        },
        direction: event.direction || event.to_dir || (finalState?.direction ?? 'NORTH'),
        penDown: t.penDown,
        speed: t.speed,
      });
    }

    // Determine event duration based on event type
    let baseDuration = 0.4;
    if (eventType === 'MOVE' || eventType === 'BACK') {
      baseDuration = Math.max(0.35, 0.12 * (event.steps || 1));
    } else if (eventType === 'TURN') {
      baseDuration = 0.35;
    } else {
      // Instant actions: PEN_UP, PEN_DOWN, SPEED, POSITION
      baseDuration = 0.04;
    }

    const effectiveDuration = Math.max(0.02, baseDuration / speedMult);
    t.eventProgress += deltaSec / effectiveDuration;

    if (eventType === 'MOVE' || eventType === 'BACK') {
      const fromP = gridToThree(event.from[0], event.from[1]);
      const toP = gridToThree(event.to[0], event.to[1]);
      const fraction = Math.min(1.0, t.eventProgress);

      const oldPos = t.currentPos.clone();
      const newPos = new THREE.Vector3().lerpVectors(fromP, toP, fraction);
      t.currentPos.copy(newPos);

      // Rotate wheels during movement
      const moveDistance = newPos.distanceTo(oldPos);
      const wheelDirection = eventType === 'MOVE' ? 1 : -1;
      wheelsRef.current.forEach((w) => {
        w.children.forEach((child) => {
          child.rotation.x += moveDistance * 2.5 * wheelDirection;
        });
      });

      // Draw trail if pen is active
      if (event.pen_down) {
        addTrailSegment(oldPos, newPos);
      }

      if (robotGroupRef.current) {
        robotGroupRef.current.position.copy(t.currentPos);
      }
    } else if (eventType === 'TURN') {
      // Smooth 90-degree turn
      const turnDelta = event.direction === 'RIGHT' ? -Math.PI / 2 : Math.PI / 2;
      const fraction = Math.min(1.0, t.eventProgress);
      const angle = t.startYaw + turnDelta * fraction;

      if (robotGroupRef.current) {
        robotGroupRef.current.rotation.y = angle;
      }
    } else if (eventType === 'PEN_DOWN') {
      t.penDown = true;
    } else if (eventType === 'PEN_UP') {
      t.penDown = false;
    } else if (eventType === 'SPEED') {
      t.speed = event.value || 1;
    }

    // Advance event when complete
    if (t.eventProgress >= 1.0) {
      if (eventType === 'MOVE' || eventType === 'BACK') {
        const toP = gridToThree(event.to[0], event.to[1]);
        t.currentPos.copy(toP);
        if (robotGroupRef.current) {
          robotGroupRef.current.position.copy(toP);
        }
      } else if (eventType === 'TURN') {
        const turnDelta = event.direction === 'RIGHT' ? -Math.PI / 2 : Math.PI / 2;
        t.currentYaw = t.startYaw + turnDelta;
        t.startYaw = t.currentYaw;
        if (robotGroupRef.current) {
          robotGroupRef.current.rotation.y = t.currentYaw;
        }
      }

      t.eventIdx += 1;
      t.eventProgress = 0;

      // Prepare startYaw for next turn if next is turn
      if (t.eventIdx < historyList.length && historyList[t.eventIdx].type === 'TURN') {
        t.startYaw = t.currentYaw;
      }
    }
  }

  const setCameraView = (view) => {
    if (!cameraRef.current || !controlsRef.current) return;
    const target = robotGroupRef.current ? robotGroupRef.current.position : new THREE.Vector3(0, 0, 0);

    if (view === 'top') {
      setCameraMode('top');
      cameraRef.current.position.set(target.x, 38, target.z + 0.01);
      controlsRef.current.target.set(target.x, 0, target.z);
    } else if (view === 'iso') {
      setCameraMode('orbit');
      cameraRef.current.position.set(target.x + 18, 22, target.z + 26);
      controlsRef.current.target.set(target.x, 0.5, target.z);
    } else if (view === 'follow') {
      setCameraMode('follow');
    }
  };

  return (
    <div className="relative w-full h-full min-h-[420px] rounded-xl overflow-hidden border border-cyan-500/20 bg-slate-950 shadow-2xl flex flex-col">
      <div ref={containerRef} className="w-full h-full flex-1 cursor-grab active:cursor-grabbing" />

      {/* Top Left Badge */}
      <div className="absolute top-3 left-3 flex items-center gap-2 pointer-events-none">
        <div className="glass-panel px-3 py-1.5 rounded-lg flex items-center gap-2 shadow-lg">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span className="text-xs font-semibold text-cyan-300 tracking-wide uppercase">
            3D Simulation Field
          </span>
          <span className="text-[10px] text-slate-400 font-mono">(WebGL)</span>
        </div>
      </div>

      {/* Camera View Switcher Buttons */}
      <div className="absolute top-3 right-3 flex items-center gap-1.5 glass-panel p-1 rounded-lg shadow-lg">
        <button
          onClick={() => setCameraView('iso')}
          className={`px-2 py-1 text-[11px] rounded font-medium transition-colors ${
            cameraMode === 'orbit' ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Isometric
        </button>
        <button
          onClick={() => setCameraView('top')}
          className={`px-2 py-1 text-[11px] rounded font-medium transition-colors ${
            cameraMode === 'top' ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Top View
        </button>
        <button
          onClick={() => setCameraView('follow')}
          className={`px-2 py-1 text-[11px] rounded font-medium transition-colors ${
            cameraMode === 'follow' ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Follow
        </button>
      </div>

      {/* Bottom Grid Legend */}
      <div className="absolute bottom-3 left-3 glass-panel px-2.5 py-1.5 rounded-lg text-[10px] text-slate-400 flex items-center gap-3">
        <div className="flex items-center gap-1">
          <span className="w-2 h-0.5 bg-cyan-400 rounded" />
          <span>North (+Y)</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2 h-0.5 bg-orange-400 rounded" />
          <span>East (+X)</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
          <span>Origin (0,0)</span>
        </div>
      </div>

      <div className="absolute bottom-3 right-3 glass-panel px-2.5 py-1 rounded-md text-[10px] text-slate-400 hidden sm:block">
        Left Click: Rotate • Right Click: Pan • Scroll: Zoom
      </div>
    </div>
  );
}
