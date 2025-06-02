import json
import unicodedata
from difflib import SequenceMatcher

class NavigationHandler:
    """Maneja toda la lógica de navegación y búsqueda de escuelas"""
    
    def __init__(self):
        self.available_schools = []
        self.graph_widget = None
    
    def set_available_schools(self, schools):
        """Establece la lista de escuelas disponibles"""
        self.available_schools = schools
    
    def set_graph_widget(self, graph_widget):
        """Establece el widget del grafo"""
        self.graph_widget = graph_widget
    
    def normalize_text(self, text):
        """Normaliza texto removiendo acentos y convirtiendo a minúsculas"""
        if text is None:
            return ""
        # Normalizar unicode (NFD = Canonical Decomposition)
        text = unicodedata.normalize('NFD', text)
        # Remover caracteres de combinación (acentos)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        return text.lower().strip()

    def clean_school_name(self, text):
        """Limpia y normaliza nombres de escuelas para comparación"""
        if not text:
            return ""
        
        # Normalizar unicode
        text = self.normalize_text(text)
        
        # Remover palabras comunes que pueden causar ruido
        common_words = ['de', 'del', 'la', 'el', 'y', 'e', 'profesional']
        words = text.split()
        filtered_words = [word for word in words if word not in common_words]
        
        return ' '.join(filtered_words)

    def calculate_similarity(self, text1, text2):
        """Calcula similitud entre dos textos"""
        return SequenceMatcher(None, text1, text2).ratio()

    def find_school_nodes_robust(self, school_names):
        """Función robusta para encontrar escuelas con múltiples estrategias"""
        school_nodes = []
        
        print(f"\n=== BÚSQUEDA ROBUSTA DE ESCUELAS ===")
        print(f"Escuelas a buscar: {school_names}")
        
        for school_name in school_names:
            print(f"\n🔍 Buscando: '{school_name}'")
            
            # Preparar diferentes versiones del texto de búsqueda
            search_normalized = self.normalize_text(school_name)
            search_cleaned = self.clean_school_name(school_name)
            search_words = set(search_normalized.split())
            
            print(f"  - Normalizada: '{search_normalized}'")
            print(f"  - Limpia: '{search_cleaned}'")
            
            best_match = None
            best_score = 0
            matches_found = []
            
            for node in self.graph_widget.nodes:
                if not (node.get('is_school', False) and node.get('school_name')):
                    continue
                    
                node_name = node['school_name']
                node_normalized = self.normalize_text(node_name)
                node_cleaned = self.clean_school_name(node_name)
                node_words = set(node_normalized.split())
                
                # Estrategia 1: Coincidencia exacta normalizada
                if search_normalized == node_normalized:
                    print(f"  ✅ COINCIDENCIA EXACTA: '{node_name}'")
                    school_nodes.append({
                        'id': node['id'],
                        'school_name': node_name
                    })
                    break
                
                # Estrategia 2: Contención bidireccional
                if (search_normalized in node_normalized or 
                    node_normalized in search_normalized):
                    score = 0.9
                    matches_found.append((node, score, f"Contención: '{node_name}'"))
                
                # Estrategia 3: Contención con texto limpio
                elif (search_cleaned in node_cleaned or 
                    node_cleaned in search_cleaned):
                    score = 0.8
                    matches_found.append((node, score, f"Contención limpia: '{node_name}'"))
                
                # Estrategia 4: Palabras clave comunes
                common_words = search_words & node_words
                if len(common_words) >= min(2, len(search_words)):
                    word_ratio = len(common_words) / len(search_words | node_words)
                    score = 0.7 * word_ratio
                    matches_found.append((node, score, f"Palabras comunes ({len(common_words)}): '{node_name}'"))
                
                # Estrategia 5: Similitud general
                similarity = self.calculate_similarity(search_normalized, node_normalized)
                if similarity > 0.6:
                    matches_found.append((node, similarity * 0.6, f"Similitud ({similarity:.2f}): '{node_name}'"))
            
            # Si no hubo coincidencia exacta, usar la mejor coincidencia
            if len(school_nodes) == len([s for s in school_names[:school_names.index(school_name)]]):
                if matches_found:
                    # Ordenar por puntuación y tomar la mejor
                    matches_found.sort(key=lambda x: x[1], reverse=True)
                    best_node, best_score, description = matches_found[0]
                    
                    print(f"  🎯 MEJOR COINCIDENCIA ({best_score:.2f}): {description}")
                    
                    # Mostrar otras opciones para debug
                    for i, (node, score, desc) in enumerate(matches_found[1:3]):
                        print(f"     Alternativa {i+1} ({score:.2f}): {desc}")
                    
                    if best_score > 0.4:  # Umbral mínimo
                        school_nodes.append({
                            'id': best_node['id'],
                            'school_name': best_node['school_name']
                        })
                    else:
                        print(f"  ❌ NO ENCONTRADA: puntuación muy baja ({best_score:.2f})")
                else:
                    print(f"  ❌ NO ENCONTRADA: sin coincidencias")
        
        print(f"\n📊 RESULTADO: {len(school_nodes)} de {len(school_names)} escuelas encontradas")
        for node in school_nodes:
            print(f"  ✅ {node['school_name']} (ID: {node['id']})")
        
        return school_nodes

    def handle_schools_navigation(self, llm_response):
        """Procesa la navegación basada en escuelas extraídas del LLM"""
        try:
            # Extraer escuelas de la respuesta
            schools = [school.strip() for school in llm_response.split(',')]
            
            if not schools:
                return "❌ No se pudieron extraer escuelas de la respuesta."
            
            # Mostrar escuelas detectadas
            result = f"🎯 Escuelas detectadas: {', '.join(schools)}\n\n"
            
            # Buscar IDs de nodos correspondientes
            school_nodes = self.find_school_nodes_robust(schools)
            
            if len(school_nodes) < 2:
                missing_schools = [school for school in schools if school not in [node['school_name'] for node in school_nodes]]
                result += f"❌ No encontré algunas escuelas en el mapa: {', '.join(missing_schools)}\n\n"
                result += f"📋 Escuelas disponibles:\n"
                for i, school in enumerate(self.available_schools[:10]):  # Mostrar solo las primeras 10
                    result += f"   • {school}\n"
                if len(self.available_schools) > 10:
                    result += f"   ... y {len(self.available_schools) - 10} más"
                return result
            
            # Si hay exactamente 2 escuelas, usar A*
            if len(school_nodes) == 2:
                start_node = school_nodes[0]
                end_node = school_nodes[1]
                
                path = self.graph_widget.find_and_highlight_path(int(start_node['id']), int(end_node['id']))
                if path:
                    distance = self.calculate_path_distance(path)
                    result += f"✅ Ruta óptima encontrada:\n"
                    result += f"🏫 Desde: {start_node['school_name']}\n"
                    result += f"🏫 Hasta: {end_node['school_name']}\n"
                    result += f"📏 Distancia: {distance:.2f} unidades\n"
                    result += f"🗺️ Nodos en la ruta: {len(path)}\n"
                    result += f"📍 Ruta: {' → '.join(map(str, path))}"
                else:
                    result += f"❌ No se encontró ruta entre {start_node['school_name']} y {end_node['school_name']}"
            
            # Si hay más de 2 escuelas, crear ruta manual
            elif len(school_nodes) > 2:
                node_ids = [int(node['id']) for node in school_nodes]
                self.graph_widget.highlight_path(node_ids)
                distance = self.calculate_path_distance(node_ids)
                
                route_names = " → ".join([node['school_name'] for node in school_nodes])
                result += f"✅ Ruta personalizada creada:\n"
                result += f"🗺️ {route_names}\n"
                result += f"📏 Distancia total: {distance:.2f} unidades\n"
                result += f"📍 IDs de nodos: {node_ids}"
            
            return result
            
        except Exception as e:
            return f"❌ Error al procesar navegación: {str(e)}"

    def process_navigation_command(self, message):
        """Procesa comandos tradicionales /ruta"""
        try:
            parts = message.split()
            if len(parts) < 3:
                return (
                    "❌ Error: Se requieren al menos 2 nodos\n\n"
                    "📖 Formato correcto:\n"
                    "   • Ruta automática: /ruta [inicio] [fin]\n"
                    "   • Ruta manual: /ruta [nodo1] [nodo2] [nodo3] ...\n\n"
                    "💡 Ejemplo: /ruta 1 5"
                )
                
            node_ids = []
            for part in parts[1:]:
                try:
                    node_ids.append(int(part))
                except ValueError:
                    return f"❌ Error: '{part}' no es un número válido"
            
            if len(node_ids) == 2:
                start, end = node_ids
                path = self.graph_widget.find_and_highlight_path(start, end)
                if path:
                    distance = self.calculate_path_distance(path)
                    result = "✅ Ruta óptima encontrada:\n"
                    result += f"📍 Desde nodo: {start}\n"
                    result += f"📍 Hasta nodo: {end}\n"
                    result += f"📏 Distancia total: {distance:.2f} unidades\n"
                    result += f"🗺️ Nodos en la ruta: {len(path)}\n"
                    result += f"🛤️ Camino: {' → '.join(map(str, path))}"
                    return result
                else:
                    return f"❌ No se encontró ruta entre los nodos {start} y {end}"
            else:
                self.graph_widget.highlight_path(node_ids)
                distance = self.calculate_path_distance(node_ids)
                result = "✅ Ruta personalizada creada:\n"
                result += f"📍 Nodos: {' → '.join(map(str, node_ids))}\n"
                result += f"📏 Distancia total: {distance:.2f} unidades\n"
                result += f"🗺️ Total de puntos: {len(node_ids)}"
                return result
                
        except Exception as e:
            return (
                f"❌ Error al procesar comando: {str(e)}\n\n"
                "📖 Formato correcto:\n"
                "   • Ruta automática: /ruta [inicio] [fin]\n"
                "   • Ruta manual: /ruta [nodo1] [nodo2] [nodo3] ...\n\n"
                "💡 Ejemplo: /ruta 1 10"
            )

    def calculate_path_distance(self, path):
        """Calcula la distancia total de una ruta"""
        if not self.graph_widget or len(path) < 2:
            return 0
            
        distance = 0
        for i in range(len(path)-1):
            for edge in self.graph_widget.edges:
                if (edge['source'] == path[i] and edge['target'] == path[i+1]) or \
                   (edge['source'] == path[i+1] and edge['target'] == path[i]):
                    distance += edge['weight']
                    break
        return distance