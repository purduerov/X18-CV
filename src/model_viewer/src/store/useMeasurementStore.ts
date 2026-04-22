import { create } from 'zustand';
import * as THREE from 'three';

export type AppMode = 'orbit' | 'slice' | 'measure' | 'calibrate';

export interface MeasurementPoint {
  id: string;
  position: THREE.Vector3;
}

export interface Measurement {
  id: string;
  pointA: MeasurementPoint;
  pointB: MeasurementPoint;
  rawDistance: number;
  calibratedDistance: number | null;
}

export interface ClippingState {
  enabled: boolean;
  xMin: number;
  xMax: number;
  yMin: number;
  yMax: number;
  zMin: number;
  zMax: number;
}

interface MeasurementState {
  scaleFactor: number;
  isCalibrated: boolean;
  calibrationKnownDistance: number | null;
  measurements: Measurement[];
  activeMeasurementPoints: MeasurementPoint[];
  clipping: ClippingState;
  gridVisible: boolean;
  mode: AppMode;
  setMode: (mode: AppMode) => void;
  addMeasurementPoint: (position: THREE.Vector3) => void;
  completeMeasurement: () => void;
  clearMeasurements: () => void;
  removeMeasurement: (id: string) => void;
  applyCalibration: (rawDistance: number, knownRealWorldMeters: number) => void;
  resetCalibration: () => void;
  setClipping: (partial: Partial<ClippingState>) => void;
  setGridVisible: (visible: boolean) => void;
  getCalibratedDistance: (rawDistance: number) => number;
  getDisplayDistance: (m: Measurement) => string;
}

const DEFAULT_SCALE = 1;

export const useMeasurementStore = create<MeasurementState>((set, get) => ({
  scaleFactor: DEFAULT_SCALE,
  isCalibrated: false,
  calibrationKnownDistance: null,
  measurements: [],
  activeMeasurementPoints: [],
  clipping: {
    enabled: false,
    xMin: -1,
    xMax: 1,
    yMin: -1,
    yMax: 1,
    zMin: -1,
    zMax: 1,
  },
  gridVisible: true,
  mode: 'orbit',
  setMode: (mode) => set({ mode }),

  addMeasurementPoint: (position) => {
    const { activeMeasurementPoints } = get();
    if (activeMeasurementPoints.length >= 2) return;
    const id = `pt-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    const point: MeasurementPoint = { id, position: position.clone() };
    set({ activeMeasurementPoints: [...activeMeasurementPoints, point] });
  },

  completeMeasurement: () => {
    const { activeMeasurementPoints, scaleFactor, isCalibrated } = get();
    if (activeMeasurementPoints.length !== 2) return;
    const [a, b] = activeMeasurementPoints;
    const rawDistance = a.position.distanceTo(b.position);
    const calibratedDistance = isCalibrated ? rawDistance / scaleFactor : null;
    const m: Measurement = { id: `m-${Date.now()}`, pointA: a, pointB: b, rawDistance, calibratedDistance };
    set({ measurements: [...get().measurements, m], activeMeasurementPoints: [] });
  },

  clearMeasurements: () => set({ measurements: [], activeMeasurementPoints: [] }),

  removeMeasurement: (id) => set({ measurements: get().measurements.filter((m) => m.id !== id) }),

  applyCalibration: (rawDistance, knownRealWorldMeters) => {
    if (rawDistance <= 0 || knownRealWorldMeters <= 0) return;
    const scaleFactor = rawDistance / knownRealWorldMeters;
    const { measurements } = get();
    const updatedMeasurements = measurements.map((m) => ({
      ...m,
      calibratedDistance: m.rawDistance / scaleFactor,
    }));
    set({
      scaleFactor,
      isCalibrated: true,
      calibrationKnownDistance: knownRealWorldMeters,
      measurements: updatedMeasurements,
      activeMeasurementPoints: [],
    });
  },

  resetCalibration: () =>
    set({
      scaleFactor: DEFAULT_SCALE,
      isCalibrated: false,
      calibrationKnownDistance: null,
      measurements: get().measurements.map((m) => ({ ...m, calibratedDistance: null })),
    }),

  setClipping: (partial) => set((s) => ({ clipping: { ...s.clipping, ...partial } })),

  setGridVisible: (visible) => set({ gridVisible: visible }),

  getCalibratedDistance: (rawDistance) => {
    const { scaleFactor, isCalibrated } = get();
    if (!isCalibrated) return rawDistance;
    return rawDistance / scaleFactor;
  },

  getDisplayDistance: (m) => {
    const { isCalibrated } = get();
    if (isCalibrated && m.calibratedDistance != null) return `${m.calibratedDistance.toFixed(4)} m`;
    return `${m.rawDistance.toFixed(4)} units`;
  },
}));
