/**
 * Application configuration - no hardcoded magic numbers in components
 */
export const CONFIG = {
  model: {
    defaultPath: '/object_3d/LectureHallPVC/result.obj',
  },
  grid: {
    baseSize: 50,
    baseDivisions: 50,
    minOpacity: 0.08,
    maxOpacity: 0.2,
    zoomOpacityFalloff: 0.15,
    unitLabel: 'm',
  },
  measurement: {
    markerRadius: 0.02,
    lineWidth: 2,
    labelOffset: 0.1,
    precision: 4,
  },
  clipping: {
    defaultNormalizedRange: { min: -1, max: 1 },
  },
  camera: {
    fov: 45,
    near: 0.1,
    far: 10000,
    initialPosition: [5, 5, 5] as [number, number, number],
    controls: {
      minDistance: 0.5,
      maxDistance: 500,
    },
  },
} as const;
