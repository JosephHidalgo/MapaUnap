import { useState } from 'react';
import { Search, Loader2, Navigation } from 'lucide-react';

interface SearchBoxProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
  hasResults?: boolean;
}

const SearchBox = ({ onSearch, isLoading, hasResults }: SearchBoxProps) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  const examples = [
    'Estoy en Medicina Humana y quiero ir a Biología',
    'Necesito ir de Educación a Administración',
    'Quiero ir desde Ingeniería Mecánica hasta Enfermería'
  ];

  return (
    <div className="search-box">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-container">
          <Search size={20} className="input-icon" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="¿A dónde quieres ir? Ej: Estoy en Medicina y quiero ir a Biología"
            className="search-input"
            disabled={isLoading}
          />
        </div>

        <button 
          type="submit" 
          className="search-button"
          disabled={isLoading || !query.trim()}
        >
          {isLoading ? (
            <>
              <Loader2 size={20} className="spin" />
              <span>Calculando ruta...</span>
            </>
          ) : (
            <>
              <Navigation size={20} />
              <span>Buscar Ruta</span>
            </>
          )}
        </button>
      </form>

      {!hasResults && (
        <div className="search-examples">
          <p className="examples-title">Ejemplos:</p>
          {examples.map((example, index) => (
            <button
              key={index}
              className="example-button"
              onClick={() => setQuery(example)}
              disabled={isLoading}
            >
              {example}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchBox;
