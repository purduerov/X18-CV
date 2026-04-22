import { useState } from 'react';
import { useMeasurementStore } from '@/store/useMeasurementStore';
import type { AppMode } from '@/store/useMeasurementStore';

const MODES: { id: AppMode; label: string }[] = [
  { id: 'orbit', label: 'Orbit' },
  { id: 'slice', label: 'Slice' },
  { id: 'measure', label: 'Measure' },
  { id: 'calibrate', label: 'Calibrate' },
];

export function ControlPanel() {
  const {
    mode,
    setMode,
    measurements,
    activeMeasurementPoints,
    completeMeasurement,
    clearMeasurements,
    removeMeasurement,
    applyCalibration,
    resetCalibration,
    clipping,
    setClipping,
    isCalibrated,
    gridVisible,
    setGridVisible,
  } = useMeasurementStore();

  const [knownDistance, setKnownDistance] = useState('0.5');
  const [clippingVisible, setClippingVisible] = useState(false);

  const rawDistance =
    activeMeasurementPoints.length === 2
      ? activeMeasurementPoints[0].position.distanceTo(activeMeasurementPoints[1].position)
      : 0;

  const handleApplyCalibration = () => {
    const known = parseFloat(knownDistance);
    if (!Number.isFinite(known) || known <= 0) return;
    applyCalibration(rawDistance, known);
  };

  const toggleClipping = () => {
    const next = !clippingVisible;
    setClippingVisible(next);
    setClipping({ enabled: next });
  };

  return (
    <div
      style={{
        position: 'absolute',
        top: 16,
        left: 16,
        background: 'rgba(0,0,0,0.85)',
        color: '#fff',
        padding: 16,
        borderRadius: 8,
        fontFamily: 'system-ui, sans-serif',
        fontSize: 13,
        minWidth: 240,
        zIndex: 10,
      }}
    >
      <div style={{ fontWeight: 600, marginBottom: 12 }}>Controls</div>

      <div style={{ marginBottom: 12 }}>
        <div style={{ opacity: 0.8, marginBottom: 6 }}>Mode</div>
        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
          {MODES.map((m) => (
            <button
              key={m.id}
              onClick={() => setMode(m.id)}
              style={{
                padding: '6px 10px',
                borderRadius: 4,
                border: mode === m.id ? '1px solid #e94560' : '1px solid #444',
                background: mode === m.id ? 'rgba(233,69,96,0.2)' : 'transparent',
                color: '#fff',
                cursor: 'pointer',
                fontSize: 12,
              }}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {mode === 'calibrate' && activeMeasurementPoints.length === 2 && (
        <div
          style={{
            marginBottom: 12,
            padding: 10,
            background: 'rgba(233,69,96,0.1)',
            borderRadius: 6,
            border: '1px solid rgba(233,69,96,0.3)',
          }}
        >
          <div style={{ marginBottom: 6 }}>Raw distance: {rawDistance.toFixed(4)} units</div>
          <div style={{ marginBottom: 6 }}>Known distance (m):</div>
          <input
            type="number"
            value={knownDistance}
            onChange={(e) => setKnownDistance(e.target.value)}
            step="0.1"
            min="0.001"
            style={{
              width: '100%',
              padding: 6,
              borderRadius: 4,
              border: '1px solid #444',
              background: '#1a1a2e',
              color: '#fff',
              marginBottom: 8,
            }}
          />
          <button
            onClick={handleApplyCalibration}
            style={{
              width: '100%',
              padding: 8,
              background: '#e94560',
              border: 'none',
              borderRadius: 4,
              color: '#fff',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            Apply calibration
          </button>
        </div>
      )}

      {isCalibrated && (
        <div style={{ marginBottom: 12, opacity: 0.9 }}>
          <span style={{ color: '#4ade80' }}>● Calibrated</span>
          <button
            onClick={resetCalibration}
            style={{
              marginLeft: 8,
              padding: '2px 8px',
              fontSize: 11,
              background: 'transparent',
              border: '1px solid #666',
              borderRadius: 4,
              color: '#aaa',
              cursor: 'pointer',
            }}
          >
            Reset
          </button>
        </div>
      )}

      {mode === 'measure' && activeMeasurementPoints.length === 2 && (
        <button
          onClick={completeMeasurement}
          style={{
            width: '100%',
            padding: 8,
            background: '#4ade80',
            border: 'none',
            borderRadius: 4,
            color: '#000',
            cursor: 'pointer',
            fontWeight: 600,
            marginBottom: 12,
          }}
        >
          Complete measurement
        </button>
      )}

      <div style={{ marginBottom: 12 }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
          <input type="checkbox" checked={gridVisible} onChange={(e) => setGridVisible(e.target.checked)} />
          <span>3D grid</span>
        </label>
      </div>

      <div style={{ marginBottom: 12 }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
          <input type="checkbox" checked={clippingVisible} onChange={toggleClipping} />
          <span>Clipping planes</span>
        </label>
      </div>

      {clipping.enabled && (
        <div style={{ marginBottom: 12, paddingLeft: 4 }}>
          <div style={{ opacity: 0.8, marginBottom: 4 }}>Plane offsets (-1 to 1)</div>
          {(
            [
              { key: 'xMin', label: 'X min' },
              { key: 'xMax', label: 'X max' },
              { key: 'yMin', label: 'Y min' },
              { key: 'yMax', label: 'Y max' },
              { key: 'zMin', label: 'Z min' },
              { key: 'zMax', label: 'Z max' },
            ] as const
          ).map(({ key, label }) => (
            <div key={key} style={{ marginBottom: 6 }}>
              <span style={{ marginRight: 8, minWidth: 44, display: 'inline-block' }}>{label}</span>
              <input
                type="range"
                min={-1}
                max={1}
                step={0.01}
                value={clipping[key]}
                onChange={(e) => setClipping({ [key]: parseFloat(e.target.value) })}
                style={{ width: 100 }}
              />
              <span style={{ marginLeft: 6, fontFamily: 'monospace', fontSize: 11 }}>
                {clipping[key].toFixed(2)}
              </span>
            </div>
          ))}
        </div>
      )}

      {measurements.length > 0 && (
        <div style={{ marginTop: 12, borderTop: '1px solid #333', paddingTop: 12 }}>
          <div style={{ marginBottom: 8 }}>Measurements</div>
          {measurements.map((m) => (
            <div
              key={m.id}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '4px 0',
                fontFamily: 'monospace',
                fontSize: 12,
              }}
            >
              <span>
                {m.calibratedDistance != null
                  ? `${m.calibratedDistance.toFixed(4)} m`
                  : `${m.rawDistance.toFixed(4)} units`}
              </span>
              <button
                onClick={() => removeMeasurement(m.id)}
                style={{
                  padding: '2px 6px',
                  fontSize: 10,
                  background: 'transparent',
                  border: '1px solid #666',
                  borderRadius: 4,
                  color: '#888',
                  cursor: 'pointer',
                }}
              >
                Remove
              </button>
            </div>
          ))}
          <button
            onClick={clearMeasurements}
            style={{
              marginTop: 8,
              padding: '6px 10px',
              fontSize: 11,
              background: 'transparent',
              border: '1px solid #666',
              borderRadius: 4,
              color: '#aaa',
              cursor: 'pointer',
              width: '100%',
            }}
          >
            Clear all
          </button>
        </div>
      )}
    </div>
  );
}
