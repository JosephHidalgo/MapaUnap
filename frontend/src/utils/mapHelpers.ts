import type { PathStep } from '../types/api';

// Colores para las rutas
export const ROUTE_COLORS = [
  '#FF6B6B', // Rojo
  '#4ECDC4', // Turquesa
  '#45B7D1', // Azul
  '#FFA07A', // Salmón
  '#98D8C8', // Verde menta
  '#F7DC6F', // Amarillo
];

// Obtener color para una ruta específica
export const getRouteColor = (index: number): string => {
  return ROUTE_COLORS[index % ROUTE_COLORS.length];
};

// Convertir pasos a coordenadas para GeoJSON
export const pathStepsToCoordinates = (steps: PathStep[]): [number, number][] => {
  return steps.map(step => [step.longitude, step.latitude]);
};

// Calcular el centro de un conjunto de coordenadas
export const calculateCenter = (coordinates: [number, number][]): [number, number] => {
  if (coordinates.length === 0) return [-70.017, -15.825]; // Centro por defecto (UNAP)

  const sum = coordinates.reduce(
    (acc, coord) => [acc[0] + coord[0], acc[1] + coord[1]],
    [0, 0]
  );

  return [sum[0] / coordinates.length, sum[1] / coordinates.length];
};

// Calcular bounds para un conjunto de coordenadas
export const calculateBounds = (
  coordinates: [number, number][]
): [[number, number], [number, number]] => {
  if (coordinates.length === 0) {
    return [[-70.020, -15.828], [-70.014, -15.822]]; // Bounds por defecto
  }

  const lngs = coordinates.map(c => c[0]);
  const lats = coordinates.map(c => c[1]);

  return [
    [Math.min(...lngs), Math.min(...lats)],
    [Math.max(...lngs), Math.max(...lats)],
  ];
};

// Formatear distancia
export const formatDistance = (meters: number): string => {
  if (meters < 1000) {
    return `${meters.toFixed(0)} m`;
  }
  return `${(meters / 1000).toFixed(2)} km`;
};

// Crear GeoJSON para una línea
export const createLineGeoJSON = (coordinates: [number, number][]) => {
  return {
    type: 'Feature' as const,
    properties: {},
    geometry: {
      type: 'LineString' as const,
      coordinates,
    },
  };
};
