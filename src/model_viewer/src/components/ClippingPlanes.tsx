import { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame, useThree } from '@react-three/fiber';
import { useMeasurementStore } from '@/store/useMeasurementStore';

const BOUNDS_SIZE = 60;

export function ClippingPlanes() {
  const { gl } = useThree();
  const { clipping } = useMeasurementStore();
  const planesRef = useRef<THREE.Plane[] | null>(null);

  const planes = useMemo(() => {
    const p = [
      new THREE.Plane(new THREE.Vector3(1, 0, 0), 0),
      new THREE.Plane(new THREE.Vector3(-1, 0, 0), 0),
      new THREE.Plane(new THREE.Vector3(0, 1, 0), 0),
      new THREE.Plane(new THREE.Vector3(0, -1, 0), 0),
      new THREE.Plane(new THREE.Vector3(0, 0, 1), 0),
      new THREE.Plane(new THREE.Vector3(0, 0, -1), 0),
    ];
    planesRef.current = p;
    return p;
  }, []);

  useFrame(() => {
    if (!planesRef.current) return;
    const half = BOUNDS_SIZE / 2;
    const xMin = Math.min(clipping.xMin, clipping.xMax) * half;
    const xMax = Math.max(clipping.xMin, clipping.xMax) * half;
    const yMin = Math.min(clipping.yMin, clipping.yMax) * half;
    const yMax = Math.max(clipping.yMin, clipping.yMax) * half;
    const zMin = Math.min(clipping.zMin, clipping.zMax) * half;
    const zMax = Math.max(clipping.zMin, clipping.zMax) * half;

    const [pxMin, pxMax, pyMin, pyMax, pzMin, pzMax] = planesRef.current;
    pxMin.constant = -xMin;
    pxMax.constant = xMax;
    pyMin.constant = -yMin;
    pyMax.constant = yMax;
    pzMin.constant = -zMin;
    pzMax.constant = zMax;

    gl.clippingPlanes = clipping.enabled ? planes : [];
  });

  return null;
}
