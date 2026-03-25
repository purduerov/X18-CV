import { useMemo } from 'react';
import * as THREE from 'three';
import { Html } from '@react-three/drei';
import { useMeasurementStore } from '@/store/useMeasurementStore';
import { CONFIG } from '@/config';

const { markerRadius } = CONFIG.measurement;

function MeasurementLine({ start, end }: { start: THREE.Vector3; end: THREE.Vector3 }) {
  const lineGeometry = useMemo(() => {
    const g = new THREE.BufferGeometry().setFromPoints([start, end]);
    return g;
  }, [start.x, start.y, start.z, end.x, end.y, end.z]);

  return (
    <line geometry={lineGeometry}>
      <lineBasicMaterial color="#e94560" linewidth={2} />
    </line>
  );
}

function MeasurementMarker({ position }: { position: THREE.Vector3 }) {
  return (
    <mesh position={position}>
      <sphereGeometry args={[markerRadius, 16, 16]} />
      <meshBasicMaterial color="#e94560" />
    </mesh>
  );
}

function MeasurementLabel({ position, text }: { position: THREE.Vector3; text: string }) {
  return (
    <Html position={position} center distanceFactor={8} style={{ pointerEvents: 'none' }}>
      <div
        style={{
          background: 'rgba(0,0,0,0.7)',
          color: '#fff',
          padding: '4px 8px',
          borderRadius: 4,
          fontSize: 12,
          fontFamily: 'monospace',
          whiteSpace: 'nowrap',
        }}
      >
        {text}
      </div>
    </Html>
  );
}

export function MeasurementTool() {
  const {
    measurements,
    activeMeasurementPoints,
    getDisplayDistance,
    isCalibrated,
    getCalibratedDistance,
  } = useMeasurementStore();

  return (
    <group>
      {measurements.map((m) => (
        <group key={m.id}>
          <MeasurementLine start={m.pointA.position} end={m.pointB.position} />
          <MeasurementMarker position={m.pointA.position} />
          <MeasurementMarker position={m.pointB.position} />
          <MeasurementLabel
            position={m.pointA.position.clone().add(m.pointB.position).multiplyScalar(0.5)}
            text={getDisplayDistance(m)}
          />
        </group>
      ))}
      {activeMeasurementPoints.map((p) => (
        <MeasurementMarker key={p.id} position={p.position} />
      ))}
      {activeMeasurementPoints.length === 2 && (
        <group>
          <MeasurementLine
            start={activeMeasurementPoints[0].position}
            end={activeMeasurementPoints[1].position}
          />
          <MeasurementLabel
            position={activeMeasurementPoints[0].position
              .clone()
              .add(activeMeasurementPoints[1].position)
              .multiplyScalar(0.5)}
            text={
              isCalibrated
                ? `${getCalibratedDistance(
                    activeMeasurementPoints[0].position.distanceTo(activeMeasurementPoints[1].position)
                  ).toFixed(4)} m`
                : `${activeMeasurementPoints[0].position
                    .distanceTo(activeMeasurementPoints[1].position)
                    .toFixed(4)} units`
            }
          />
        </group>
      )}
    </group>
  );
}
