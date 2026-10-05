"use client";

import React, { useEffect, useRef } from "react";
import * as THREE from "three";

interface Shelter3DProps {
  length?: number;
  width?: number;
  height?: number;
  roofAngle?: number;
  orientationDeg?: number;
  solarKw?: number;
  wallColor?: string;
  roofColor?: string;
}

export const Shelter3D: React.FC<Shelter3DProps> = ({
  length = 8,
  width = 6,
  height = 3,
  roofAngle = 35,
  orientationDeg = 180,
  solarKw = 10,
  wallColor = "#334155",
  roofColor = "#1e293b"
}) => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const container = mountRef.current;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x090d16);

    const camera = new THREE.PerspectiveCamera(
      45,
      container.clientWidth / container.clientHeight,
      0.1,
      100
    );
    camera.position.set(12, 10, 14);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    container.innerHTML = "";
    container.appendChild(renderer.domElement);

    // Grid Floor
    const gridHelper = new THREE.GridHelper(24, 24, 0x00adb5, 0x1e293b);
    gridHelper.position.y = 0;
    scene.add(gridHelper);

    // Sun / Directional Light
    const sunLight = new THREE.DirectionalLight(0xfff7ed, 1.8);
    sunLight.position.set(15, 20, 10);
    sunLight.castShadow = true;
    scene.add(sunLight);

    const ambientLight = new THREE.AmbientLight(0x94a3b8, 0.6);
    scene.add(ambientLight);

    // Group for shelter to rotate based on orientation
    const shelterGroup = new THREE.Group();

    // Scale factors to fit in viewport
    const scale = 0.8;
    const l = length * scale;
    const w = width * scale;
    const h = height * scale;

    // Main Shelter Walls
    const wallGeo = new THREE.BoxGeometry(l, h, w);
    const wallMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(wallColor),
      roughness: 0.5,
      metalness: 0.2
    });
    const wallMesh = new THREE.Mesh(wallGeo, wallMat);
    wallMesh.position.y = h / 2;
    wallMesh.castShadow = true;
    wallMesh.receiveShadow = true;
    shelterGroup.add(wallMesh);

    // Pitched Roof
    const pitchRad = (roofAngle * Math.PI) / 180;
    const roofPeakHeight = (w / 2) * Math.tan(pitchRad);
    const roofGeo = new THREE.ConeGeometry(w * 0.75, roofPeakHeight, 4);
    const roofMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(roofColor),
      roughness: 0.3,
      metalness: 0.4
    });
    const roofMesh = new THREE.Mesh(roofGeo, roofMat);
    roofMesh.position.y = h + roofPeakHeight / 2;
    roofMesh.rotation.y = Math.PI / 4;
    roofMesh.castShadow = true;
    shelterGroup.add(roofMesh);

    // South Passive Windows (Glossy blue-tinted glass)
    const winGeo = new THREE.PlaneGeometry(l * 0.4, h * 0.4);
    const winMat = new THREE.MeshPhysicalMaterial({
      color: 0x38bdf8,
      transmission: 0.7,
      opacity: 0.9,
      transparent: true,
      roughness: 0.1
    });
    const winMesh = new THREE.Mesh(winGeo, winMat);
    winMesh.position.set(0, h * 0.5, w / 2 + 0.05);
    shelterGroup.add(winMesh);

    // Solar PV Array on South-Facing Roof Pitch
    const panelCols = 4;
    const panelRows = 2;
    const panelW = (l * 0.7) / panelCols;
    const panelH = 0.8;
    const pvMat = new THREE.MeshStandardMaterial({
      color: 0x0284c7,
      metalness: 0.8,
      roughness: 0.2
    });

    for (let c = 0; c < panelCols; c++) {
      for (let r = 0; r < panelRows; r++) {
        const pvGeo = new THREE.BoxGeometry(panelW * 0.9, 0.04, panelH * 0.9);
        const pvMesh = new THREE.Mesh(pvGeo, pvMat);
        const posX = -l * 0.35 + c * panelW + panelW / 2;
        const posZ = w * 0.25 - r * (panelH * 0.6);
        pvMesh.position.set(posX, h + 0.3 + r * 0.2, posZ);
        pvMesh.rotation.x = -pitchRad * 0.7;
        shelterGroup.add(pvMesh);
      }
    }

    // Apply orientation azimuth
    shelterGroup.rotation.y = ((orientationDeg - 180) * Math.PI) / 180;
    scene.add(shelterGroup);

    // Interactive mouse rotation
    let isDragging = false;
    let prevMouseX = 0;
    let prevMouseY = 0;

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const deltaX = e.clientX - prevMouseX;
      const deltaY = e.clientY - prevMouseY;
      shelterGroup.rotation.y += deltaX * 0.01;
      camera.position.y = Math.max(3, Math.min(22, camera.position.y - deltaY * 0.05));
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    };

    const onMouseUp = () => {
      isDragging = false;
    };

    container.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);

    camera.lookAt(0, h * 0.6, 0);

    let animationFrameId: number;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      if (!isDragging) {
        shelterGroup.rotation.y += 0.002; // Gentle orbit rotation
      }
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      container.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
      renderer.dispose();
    };
  }, [length, width, height, roofAngle, orientationDeg, solarKw, wallColor, roofColor]);

  return (
    <div className="relative w-full h-[420px] rounded-xl overflow-hidden border border-slate-800 bg-slate-950 shadow-inner">
      <div ref={mountRef} className="w-full h-full cursor-grab active:cursor-grabbing" />
      <div className="absolute top-3 left-3 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700 text-xs font-mono text-cyan-400">
        3D Interactive Model • Drag to Orbit
      </div>
      <div className="absolute bottom-3 right-3 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700 text-xs text-slate-300">
        Orient: <span className="text-cyan-400 font-bold">{orientationDeg}°</span> | Pitch: <span className="text-amber-400 font-bold">{roofAngle}°</span> | Solar: <span className="text-emerald-400 font-bold">{solarKw} kW</span>
      </div>
    </div>
  );
};
