import { X } from 'lucide-react';
import type { NavigationResponse } from '../types/api';

interface RouteInfoProps {
  navigationData: NavigationResponse | null;
  onClose: () => void;
}

const RouteInfo = ({ navigationData, onClose }: RouteInfoProps) => {
  if (!navigationData) return null;

  const { success, message, schools_detected, total_route_distance, detailed_instructions } = navigationData;

  const parseMarkdown = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        const boldText = part.slice(2, -2);
        return <strong key={index}>{boldText}</strong>;
      }
      return part;
    });
  };

  if (!success) {
    return (
      <div className="route-info error">
        <div className="route-info-header">
          <h3>⚠️ Error</h3>
          <button onClick={onClose} className="close-button">
            <X size={20} />
          </button>
        </div>
        <p>{message}</p>
      </div>
    );
  }

  return (
    <div className="route-info">
      <button onClick={onClose} className="close-button-top">
        <X size={20} />
      </button>

      <div className="distance-section">
        <h4>📏 Distancia total: {total_route_distance.toFixed(2)} metros</h4>
      </div>

      <div className="schools-detected">
        <h4>Recorrido</h4>
        <div className="schools-list-horizontal">
          {schools_detected.map((school, index) => (
            <div key={index} className="school-item-horizontal">
              <div className="school-number">{index + 1}</div>
              <div className="school-name-horizontal">{school}</div>
            </div>
          ))}
        </div>
      </div>

      {detailed_instructions && (
        <div className="navigation-instructions">
          <h4>🧭 Instrucciones de Navegación</h4>
          <div className="instructions-content">
            {detailed_instructions.split('\n').map((line, index) => (
              <p key={index} className="instruction-line">
                {parseMarkdown(line)}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RouteInfo;
