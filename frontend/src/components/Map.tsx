import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { PathResponse, Node } from '../types/api';
import { 
  pathStepsToCoordinates, 
  calculateBounds, 
  getRouteColor 
} from '../utils/mapHelpers';

interface MapProps {
  paths: PathResponse[];
  nodes: Node[];
  onMapLoad?: (map: maplibregl.Map) => void;
}

const Map: React.FC<MapProps> = ({ paths, nodes, onMapLoad }) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markers = useRef<maplibregl.Marker[]>([]);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Inicializar mapa
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    const styleUrl = import.meta.env.VITE_MAPTILER_STYLE;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: styleUrl,
      center: [-70.017, -15.825], // Centro UNAP
      zoom: 16,
      pitch: 0,
      bearing: 0,
      // Deshabilitar todas las interacciones del usuario
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

    // Control de escala
    map.current.addControl(
      new maplibregl.ScaleControl({
        maxWidth: 100,
        unit: 'metric',
      }),
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

  // Agregar todos los nodos del grafo
  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    const currentMap = map.current;

    // Limpiar marcadores anteriores
    markers.current.forEach(marker => marker.remove());
    markers.current = [];

    // Agregar nodos regulares
    nodes.forEach(node => {
      if (!currentMap) return;

      const el = document.createElement('div');
      el.className = node.is_school ? 'node-marker school-node' : 'node-marker regular-node';
      
      if (node.is_school && node.school_name) {
        el.title = node.school_name;
      }

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([node.longitude, node.latitude])
        .addTo(currentMap);

      markers.current.push(marker);
    });

    return () => {
      markers.current.forEach(marker => marker.remove());
      markers.current = [];
    };
  }, [nodes, mapLoaded]);

  // Dibujar rutas
  useEffect(() => {
    if (!map.current || !mapLoaded || paths.length === 0) return;

    const currentMap = map.current;

    paths.forEach((pathData, index) => {
      const sourceId = `route-${index}`;
      const layerId = `route-layer-${index}`;
      const coordinates = pathStepsToCoordinates(pathData.path);

      // Remover capa y fuente si ya existen
      if (currentMap.getLayer(layerId)) {
        currentMap.removeLayer(layerId);
      }
      if (currentMap.getSource(sourceId)) {
        currentMap.removeSource(sourceId);
      }

      // Agregar fuente de datos
      currentMap.addSource(sourceId, {
        type: 'geojson',
        data: {
          type: 'Feature',
          properties: {},
          geometry: {
            type: 'LineString',
            coordinates,
          },
        },
      });

      // Agregar capa de línea
      currentMap.addLayer({
        id: layerId,
        type: 'line',
        source: sourceId,
        layout: {
          'line-join': 'round',
          'line-cap': 'round',
        },
        paint: {
          'line-color': getRouteColor(index),
          'line-width': 4,
          'line-opacity': 0.8,
        },
      });

      // Agregar marcadores de inicio y fin
      const start = pathData.path[0];
      const end = pathData.path[pathData.path.length - 1];

      // Marcador de inicio
      const startEl = document.createElement('div');
      startEl.className = 'route-marker start-marker';
      startEl.textContent = 'A';
      new maplibregl.Marker({ element: startEl })
        .setLngLat([start.longitude, start.latitude])
        .addTo(currentMap);

      // Marcador de fin
      const endEl = document.createElement('div');
      endEl.className = 'route-marker end-marker';
      endEl.textContent = 'B';
      new maplibregl.Marker({ element: endEl })
        .setLngLat([end.longitude, end.latitude])
        .addTo(currentMap);
    });

    if (paths.length > 0) {
      const allCoordinates = paths.flatMap(p => pathStepsToCoordinates(p.path));
      const bounds = calculateBounds(allCoordinates);
      
      // Habilitar temporalmente el movimiento para ajustar la vista
      currentMap.dragPan.enable();
      currentMap.fitBounds(bounds, {
        padding: { top: 100, bottom: 100, left: 100, right: 100 },
        maxZoom: 17,
      });
      setTimeout(() => {
        currentMap.dragPan.disable();
      }, 100);
    }

    return () => {
      paths.forEach((_, index) => {
        const layerId = `route-layer-${index}`;
        const sourceId = `route-${index}`;
        
        if (currentMap.getLayer(layerId)) {
          currentMap.removeLayer(layerId);
        }
        if (currentMap.getSource(sourceId)) {
          currentMap.removeSource(sourceId);
        }
      });
    };
  }, [paths, mapLoaded]);

  return (
    <div className="map-container">
      <div ref={mapContainer} className="map" />
    </div>
  );
};

export default Map;
