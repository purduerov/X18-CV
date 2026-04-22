import { Suspense, useRef } from 'react';
import { Canvas, ThreeEvent } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { useOBJWithMTL } from '@/hooks/useOBJWithMTL';
import { useMeasurementStore } from '@/store/useMeasurementStore';
import { ClippingPlanes } from './ClippingPlanes';
import { AdaptiveGrid } from './AdaptiveGrid';
import { MeasurementTool } from './MeasurementTool';
import { CalibrationController } from './CalibrationController';
import { CONFIG } from '@/config';

const NEUTRAL_BG = '#1a1a2e';

interface LoadedModelProps {
  url: string;
}

function LoadedModel({ url }: LoadedModelProps) {
  const group = useRef<THREE.Group>(null);
  const object = useOBJWithMTL(url);
  const { mode, addMeasurementPoint } = useMeasurementStore();
  const isMeasuring = mode === 'measure' || mode === 'calibrate';

  const handlePointerDown = (e: ThreeEvent<PointerEvent>) => {
    if (!isMeasuring) return;
    e.stopPropagation();
    addMeasurementPoint(e.point.clone());
  };

  return (
    <group ref={group} onPointerDown={handlePointerDown}>
      <primitive object={object} />
    </group>
  );
}

function SceneContent({ modelUrl }: { modelUrl: string }) {
  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 10, 10]} intensity={1} castShadow />
      <directionalLight position={[-5, 5, -5]} intensity={0.3} />
      <Suspense
        fallback={
          <mesh>
            <boxGeometry args={[1, 1, 1]} />
            <meshStandardMaterial color="#444" />
          </mesh>
        }
      >
        <LoadedModel url={modelUrl} />
      </Suspense>
      <AdaptiveGrid />
      <ClippingPlanes />
      <MeasurementTool />
      <CalibrationController />
      <OrbitControls
        makeDefault
        minDistance={CONFIG.camera.controls.minDistance}
        maxDistance={CONFIG.camera.controls.maxDistance}
        enablePan
      />
    </>
  );
}

export function ModelScene() {
  const modelUrl = CONFIG.model.defaultPath;

  return (
    <div style={{ width: '100vw', height: '100vh', background: NEUTRAL_BG }}>
      <Canvas
        shadows
        dpr={[1, 2]}
        camera={{
          fov: CONFIG.camera.fov,
          near: CONFIG.camera.near,
          far: CONFIG.camera.far,
          position: CONFIG.camera.initialPosition,
        }}
        gl={{
          antialias: true,
          alpha: false,
          powerPreference: 'high-performance',
        }}
      >
        <SceneContent modelUrl={modelUrl} />
      </Canvas>
    </div>
  );
}
