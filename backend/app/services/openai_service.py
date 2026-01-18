import os
from typing import List
from openai import OpenAI
from ..config import OPENAI_API_KEY, OPENAI_MODEL


class OpenAIService:
    """Servicio para procesar consultas de navegación con OpenAI GPT-4o mini"""
    
    def __init__(self, required: bool = True):
        """
        Inicializa el cliente de OpenAI
        
        Args:
            required: Si es True, lanza error si no hay API key. Si es False, solo advierte.
        """
        self.api_key_configured = bool(
            OPENAI_API_KEY and OPENAI_API_KEY != "tu_api_key_de_openai_aqui"
        )
        
        if not self.api_key_configured:
            if required:
                raise ValueError(
                    "OPENAI_API_KEY no está configurada correctamente. "
                    "Por favor, configura la variable de entorno en el archivo .env en la raíz del proyecto"
                )
            else:
                print("⚠️  OpenAI API Key no configurada - usando modo simulado")
                self.client = None
                self.model = None
                return
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    def extract_schools_from_query(self, query: str, available_schools: List[str]) -> List[str]:
        """
        Extrae y ordena las escuelas profesionales mencionadas en la consulta
        
        Args:
            query: Consulta del usuario en lenguaje natural
            available_schools: Lista de escuelas disponibles en el sistema
            
        Returns:
            Lista de nombres de escuelas en el orden mencionado
        """
        if not self.api_key_configured:
            return self._extract_schools_fallback(query, available_schools)
        
        schools_list = "\n".join([f"- {school}" for school in available_schools])
        
        system_prompt = f"""Eres un asistente especializado en identificar escuelas profesionales de la UNAP y ayudar con la navegación en el campus.

Escuelas disponibles en el sistema:
{schools_list}

IMPORTANTE:
- Identifica las escuelas profesionales mencionadas en el mensaje del usuario
- Identifica dónde está el usuario actualmente (origen) y a dónde quiere ir (destino)
- El usuario puede decir "estoy en", "me encuentro en", "desde", etc. para indicar su ubicación actual
- El usuario puede decir "quiero ir a", "necesito llegar a", "hacia", etc. para indicar su destino
- Si menciona múltiples destinos, respeta el orden en que los menciona
- Devuelve los nombres EXACTAMENTE como aparecen en la lista de escuelas disponibles
- Si una escuela mencionada no existe, intenta encontrar la más similar
- Separa los nombres con comas en el ORDEN: origen primero, luego destinos
- NO agregues explicaciones, solo los nombres
- Si no identificas ninguna escuela, devuelve "NINGUNA"

Ejemplos:
Usuario: "Estoy en Medicina Humana y quiero ir a Ingeniería Civil"
Respuesta: Medicina Humana, Ingeniería Civil

Usuario: "Me encuentro en Educación y necesito ir a Biología"
Respuesta: Educación, Biología

Usuario: "Desde Administración hasta Enfermería"
Respuesta: Administración, Enfermería

Usuario: "Quiero ir de Derecho a Contabilidad y luego a Ingeniería de Sistemas"
Respuesta: Derecho, Contabilidad, Ingeniería de Sistemas
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            
            # Si no se encontraron escuelas
            if result.upper() == "NINGUNA":
                return []
            
            # Separar los nombres y limpiar espacios
            schools = [school.strip() for school in result.split(',')]
            
            return schools
            
        except Exception as e:
            print(f"Error al procesar la consulta con OpenAI: {e}")
            return []
    
    def _extract_schools_fallback(self, query: str, available_schools: List[str]) -> List[str]:
        """
        Método de fallback para extraer escuelas sin usar OpenAI
        Usa coincidencia de texto simple
        
        Args:
            query: Consulta del usuario
            available_schools: Lista de escuelas disponibles
            
        Returns:
            Lista de escuelas encontradas
        """
        query_lower = query.lower()
        found_schools = []
        
        for school in available_schools:
            school_lower = school.lower()
            # Buscar palabras clave de la escuela en la consulta
            words = school_lower.split()
            
            if school_lower in query_lower:
                found_schools.append(school)
            else:
                matches = sum(1 for word in words if len(word) > 3 and word in query_lower)
                if matches >= min(2, len(words)):
                    found_schools.append(school)
        
        return found_schools
    
    def generate_detailed_navigation_instructions(
        self,
        path_steps: List[dict],
        origin_name: str,
        destination_name: str,
        total_distance: float
    ) -> str:
        """
        Genera instrucciones de navegación detalladas paso a paso
        
        Args:
            path_steps: Lista de pasos de la ruta con coordenadas y nombres
            origin_name: Nombre de la escuela de origen
            destination_name: Nombre de la escuela de destino
            total_distance: Distancia total en metros
            
        Returns:
            Instrucciones detalladas en lenguaje natural
        """
        if not self.api_key_configured:
            return self._generate_instructions_fallback(
                path_steps, origin_name, destination_name, total_distance
            )
        
        try:
            route_description = self._build_route_description(path_steps)
            
            system_prompt = """Eres un asistente de navegación del campus universitario de la UNAP. 
Tu tarea es dar indicaciones claras y precisas para ayudar a los estudiantes a llegar a su destino.

Formato de respuesta:
- Usa un tono amigable y directo
- Menciona direcciones cardinales (norte, sur, este, oeste) cuando sea relevante
- Menciona giros (derecha, izquierda) cuando cambies de dirección
- Menciona escuelas profesionales que se encuentren en el camino como puntos de referencia
- Sé conciso pero claro
- Divide las instrucciones en pasos numerados si la ruta es larga
"""
            
            user_prompt = f"""Genera instrucciones de navegación para esta ruta:

Origen: {origin_name}
Destino: {destination_name}
Distancia total: {total_distance:.0f} metros

Ruta detallada:
{route_description}

Genera instrucciones claras paso a paso para que el usuario llegue a su destino."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error al generar instrucciones detalladas: {e}")
            return self._generate_instructions_fallback(
                path_steps, origin_name, destination_name, total_distance
            )
    
    def _build_route_description(self, path_steps: List[dict]) -> str:
        """Construye descripción de la ruta con direcciones cardinales"""
        description_parts = []
        
        for i, step in enumerate(path_steps):
            if i == 0:
                description_parts.append(f"Inicio en: {step['school_name'] or 'Nodo ' + step['node_id']}")
            elif i == len(path_steps) - 1:
                description_parts.append(f"Destino: {step['school_name'] or 'Nodo ' + step['node_id']}")
            else:
                prev_step = path_steps[i - 1]
                direction = self._calculate_direction(
                    prev_step['latitude'], prev_step['longitude'],
                    step['latitude'], step['longitude']
                )
                
                distance = step.get('distance_from_previous', 0)
                location = step['school_name'] or f"punto intermedio"
                
                if step['is_school']:
                    description_parts.append(
                        f"Paso {i}: Dirección {direction}, {distance:.0f}m - Pasas por {location}"
                    )
                else:
                    description_parts.append(
                        f"Paso {i}: Dirección {direction}, {distance:.0f}m"
                    )
        
        return "\n".join(description_parts)
    
    def _calculate_direction(self, lat1: float, lon1: float, lat2: float, lon2: float) -> str:
        """Calcula la dirección cardinal entre dos puntos"""
        import math
        
        delta_lon = lon2 - lon1
        
        x = math.cos(math.radians(lat2)) * math.sin(math.radians(delta_lon))
        y = (math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) -
             math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.cos(math.radians(delta_lon)))
        
        bearing = math.degrees(math.atan2(x, y))
        bearing = (bearing + 360) % 360
        
        if 337.5 <= bearing or bearing < 22.5:
            return "Norte"
        elif 22.5 <= bearing < 67.5:
            return "Noreste"
        elif 67.5 <= bearing < 112.5:
            return "Este"
        elif 112.5 <= bearing < 157.5:
            return "Sureste"
        elif 157.5 <= bearing < 202.5:
            return "Sur"
        elif 202.5 <= bearing < 247.5:
            return "Suroeste"
        elif 247.5 <= bearing < 292.5:
            return "Oeste"
        else:
            return "Noroeste"
    
    def _generate_instructions_fallback(
        self,
        path_steps: List[dict],
        origin_name: str,
        destination_name: str,
        total_distance: float
    ) -> str:
        """Genera instrucciones básicas cuando OpenAI no está disponible"""
        instructions = [f"Ruta desde {origin_name} hasta {destination_name}"]
        instructions.append(f"Distancia total: {total_distance:.0f} metros\n")
        
        # Mencionar escuelas en el camino
        schools_in_path = [
            step['school_name'] for step in path_steps 
            if step.get('is_school') and step.get('school_name')
        ]
        
        if len(schools_in_path) > 2:
            instructions.append(
                f"En tu recorrido pasarás por: {', '.join(schools_in_path[1:-1])}"
            )
        
        # Direcciones básicas
        if len(path_steps) > 2:
            mid_point = len(path_steps) // 2
            direction = self._calculate_direction(
                path_steps[0]['latitude'], path_steps[0]['longitude'],
                path_steps[mid_point]['latitude'], path_steps[mid_point]['longitude']
            )
            instructions.append(f"Dirígete hacia el {direction}.")
        
        return "\n".join(instructions)
