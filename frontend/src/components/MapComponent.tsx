import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { PathStep, Node, Edge } from '../types/api';

interface MapComponentProps {
  paths: PathStep[][];
  nodes: Node[];
  edges: Edge[];
  onMapLoad?: (map: maplibregl.Map) => void;
}

const SCHOOL_COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
  '#DFE6E9', '#74B9FF', '#A29BFE', '#FD79A8', '#FDCB6E',
  '#6C5CE7', '#00B894', '#00CEC9', '#0984E3', '#E17055',
  '#D63031', '#FDCB6E', '#E84393', '#9B59B6', '#3498DB',
  '#1ABC9C', '#F39C12', '#E74C3C', '#95A5A6', '#34495E',
  '#16A085', '#27AE60', '#2980B9', '#8E44AD', '#F1C40F'
];

const MapComponent = ({ paths, nodes, edges, onMapLoad }: MapComponentProps) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markers = useRef<maplibregl.Marker[]>([]);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    const styleUrl = import.meta.env.VITE_MAPTILER_STYLE;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: styleUrl,
      center: [-70.016, -15.8244], // Centro del campus UNAP
      zoom: 16,
      pitch: 0,
      bearing: 0,
      interactive: false,
      dragPan: false,
      scrollZoom: false,
      boxZoom: false,
      dragRotate: false,
      keyboard: false,
      doubleClickZoom: false,
      touchZoomRotate: false,
      touchPitch: false,
    });

    map.current.addControl(
      new maplibregl.ScaleControl({ maxWidth: 100, unit: 'metric' }),
      'bottom-left'
    );

    map.current.on('load', () => {
      setMapLoaded(true);
      if (onMapLoad && map.current) {
        onMapLoad(map.current);
      }
    });

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, [onMapLoad]);

  // Renderizar aristas del grafo
  useEffect(() => {
    if (!map.current || !mapLoaded || edges.length === 0) return;

    const currentMap = map.current;

    if (currentMap.getLayer('graph-edges')) {
      currentMap.removeLayer('graph-edges');
    }
    if (currentMap.getSource('graph-edges')) {
      currentMap.removeSource('graph-edges');
    }

    const edgeFeatures = edges.map(edge => ({
      type: 'Feature' as const,
      properties: { weight: edge.weight },
      geometry: {
        type: 'LineString' as const,
        coordinates: [edge.source_coords, edge.target_coords]
      }
    }));

    currentMap.addSource('graph-edges', {
      type: 'geojson',
      data: {
        type: 'FeatureCollection',
        features: edgeFeatures
      }
    });

    currentMap.addLayer({
      id: 'graph-edges',
      type: 'line',
      source: 'graph-edges',
      layout: {},
      paint: {
        'line-color': '#94A3B8',
        'line-width': 2,
        'line-opacity': 0.5
      }
    });

    return () => {
      if (currentMap.getLayer('graph-edges')) {
        currentMap.removeLayer('graph-edges');
      }
      if (currentMap.getSource('graph-edges')) {
        currentMap.removeSource('graph-edges');
      }
    };
  }, [edges, mapLoaded]);

  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    markers.current.forEach(marker => marker.remove());
    markers.current = [];

    const schools = nodes.filter(n => n.is_school && n.school_name);
    const schoolColorMap = new Map<string, string>();
    schools.forEach((school, index) => {
      if (school.school_name) {
        schoolColorMap.set(school.school_name, SCHOOL_COLORS[index % SCHOOL_COLORS.length]);
      }
    });

    nodes.forEach(node => {
      const el = document.createElement('div');
      
      if (node.is_school && node.school_name) {
        el.className = 'node-marker school-node';
        const color = schoolColorMap.get(node.school_name);
        if (color) {
          el.style.backgroundColor = color;
        }
        
        const popup = new maplibregl.Popup({
          closeButton: false,
          closeOnClick: false,
          offset: 15
        }).setHTML(`<div class="school-popup">${node.school_name}</div>`);

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([node.longitude, node.latitude])
          .setPopup(popup)
          .addTo(map.current!);

        // Mostrar popup al pasar el cursor
        el.addEventListener('mouseenter', () => {
          popup.addTo(map.current!);
        });
        el.addEventListener('mouseleave', () => {
          popup.remove();
        });

        markers.current.push(marker);
      } else {
        el.className = 'node-marker regular-node';
        
        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([node.longitude, node.latitude])
          .addTo(map.current!);

        markers.current.push(marker);
      }
    });
  }, [nodes, mapLoaded]);

  // Dibujar rutas en el mapa
  useEffect(() => {
    if (!map.current || !mapLoaded || paths.length === 0) return;

    const currentMap = map.current;

    // Eliminar capas y fuentes anteriores
    if (currentMap.getLayer('route')) {
      currentMap.removeLayer('route');
    }
    if (currentMap.getLayer('route-points')) {
      currentMap.removeLayer('route-points');
    }
    if (currentMap.getSource('route')) {
      currentMap.removeSource('route');
    }
    
    // Limpiar marcadores de ruta anteriores
    document.querySelectorAll('.route-label-marker').forEach(el => el.remove());

    // Combinar todos los paths en una sola ruta
    const allCoordinates: [number, number][] = [];
    const allPoints: GeoJSON.Feature[] = [];
    
    // Recopilar todas las escuelas únicas en el orden de la ruta
    const allSchools: Array<{ name: string; coords: [number, number]; index: number }> = [];
    const seenSchools = new Set<string>();
    
    paths.forEach((path) => {
      path.forEach((step) => {
        if (step.is_school && step.school_name && !seenSchools.has(step.school_name)) {
          seenSchools.add(step.school_name);
          allSchools.push({
            name: step.school_name,
            coords: [step.longitude, step.latitude],
            index: allSchools.length
          });
        }
      });
    });
    
    // Colores para etiquetas intermedias
    const intermediateColors = ['#FF9800', '#9C27B0', '#00BCD4', '#FF5722', '#795548'];

    allSchools.forEach((school, index) => {
      const label = document.createElement('div');
      let labelClass = 'route-label-marker';
      let labelText = '';
      
      if (index === 0) {
        // Primera escuela - INICIO (verde)
        labelClass += ' start-label';
        labelText = `Inicio: ${school.name}`;
      } else if (index === allSchools.length - 1) {
        // Última escuela - FIN (rojo)
        labelClass += ' end-label';
        labelText = `Destino: ${school.name}`;
      } else {
        // Escuelas intermedias
        labelClass += ' intermediate-label';
        const position = index === 1 ? 'Segundo destino' : index === 2 ? 'Tercer destino' : `${index + 1}º destino`;
        labelText = `${position}: ${school.name}`;
        label.style.backgroundColor = intermediateColors[(index - 1) % intermediateColors.length];
      }
      
      label.className = labelClass;
      label.innerHTML = `<div class="label-text">${labelText}</div>`;
      
      new maplibregl.Marker({ element: label, anchor: 'bottom' })
        .setLngLat(school.coords)
        .addTo(currentMap);
    });

    paths.forEach((path, pathIndex) => {
      const coordinates: [number, number][] = path.map(step => [
        step.longitude,
        step.latitude
      ]);
      
      allCoordinates.push(...coordinates);

      // Crear puntos para cada paso
      path.forEach((step, stepIndex) => {
        allPoints.push({
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [step.longitude, step.latitude]
          },
          properties: {
            name: step.school_name || `Punto ${stepIndex + 1}`,
            isSchool: step.is_school,
            pathIndex,
            stepIndex
          }
        });
      });
    });

    // Agregar la ruta como GeoJSON
    const geojson: GeoJSON.FeatureCollection = {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: allCoordinates
          },
          properties: {}
        }
      ]
    };

    map.current.addSource('route', {
      type: 'geojson',
      data: geojson
    });

    // Agregar la capa de línea
    map.current.addLayer({
      id: 'route',
      type: 'line',
      source: 'route',
      layout: {
        'line-join': 'round',
        'line-cap': 'round'
      },
      paint: {
        'line-color': '#3b82f6',
        'line-width': 4,
        'line-opacity': 0.8
      }
    });

    // Agregar puntos de la ruta
    const pointsGeojson: GeoJSON.FeatureCollection = {
      type: 'FeatureCollection',
      features: allPoints
    };

    map.current.addSource('route-points', {
      type: 'geojson',
      data: pointsGeojson
    });

    map.current.addLayer({
      id: 'route-points',
      type: 'circle',
      source: 'route-points',
      paint: {
        'circle-radius': 6,
        'circle-color': '#3b82f6',
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': 2
      }
    });

    // Ajustar el mapa para mostrar toda la ruta
    if (allCoordinates.length > 0) {
      const bounds = allCoordinates.reduce(
        (bounds, coord) => bounds.extend(coord as [number, number]),
        new maplibregl.LngLatBounds(allCoordinates[0], allCoordinates[0])
      );

      map.current.fitBounds(bounds, {
        padding: 100,
        maxZoom: 17
      });
    }
  }, [paths, mapLoaded]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <div 
        ref={mapContainer} 
        style={{ 
          width: '100%', 
          height: '100%',
          position: 'absolute',
          top: 0,
          left: 0
        }}
      />
    </div>
  );
};

export default MapComponent;
