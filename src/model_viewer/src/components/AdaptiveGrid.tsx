import { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { useMeasurementStore } from '@/store/useMeasurementStore';
import { CONFIG } from '@/config';

export function AdaptiveGrid() {
  const lineRef = useRef<THREE.LineSegments>(null);
  const { gridVisible } = useMeasurementStore();
  const { baseSize, baseDivisions, minOpacity, maxOpacity, zoomOpacityFalloff } = CONFIG.grid;

  const { geometry, material } = useMemo(() => {
    const size = baseSize / 2;
    const step = baseSize / baseDivisions;
    const positions: number[] = [];

    for (let i = 0; i <= baseDivisions; i++) {
      for (let j = 0; j <= baseDivisions; j++) {
        const y = -size + i * step;
        const z = -size + j * step;
        positions.push(-size, y, z, size, y, z);
      }
    }
    for (let i = 0; i <= baseDivisions; i++) {
      for (let j = 0; j <= baseDivisions; j++) {
        const x = -size + i * step;
        const z = -size + j * step;
        positions.push(x, -size, z, x, size, z);
      }
    }
    for (let i = 0; i <= baseDivisions; i++) {
      for (let j = 0; j <= baseDivisions; j++) {
        const x = -size + i * step;
        const y = -size + j * step;
        positions.push(x, y, -size, x, y, size);
      }
    }

    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    g.computeBoundingSphere();

    const m = new THREE.LineBasicMaterial({
      color: 0x888888,
      transparent: true,
      opacity: minOpacity,
    });

    return { geometry: g, material: m };
  }, [baseSize, baseDivisions, minOpacity]);

  useFrame((state) => {
    if (!lineRef.current) return;
    const distance = state.camera.position.length();
    const opacity = Math.max(
      minOpacity,
      Math.min(maxOpacity, 1 - distance * zoomOpacityFalloff * 0.01)
    );
    material.opacity = opacity;
  });

  if (!gridVisible) return null;

  return (
    <group position={[0, 0, 0]}>
      <lineSegments ref={lineRef} geometry={geometry} material={material} />
    </group>
  );
}
