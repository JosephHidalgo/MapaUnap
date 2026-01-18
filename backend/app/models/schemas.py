from pydantic import BaseModel, Field
from typing import List, Optional


class Node(BaseModel):
    """Modelo para representar un nodo del grafo"""
    id: str
    latitude: float
    longitude: float
    is_school: bool
    school_name: Optional[str] = None


class Edge(BaseModel):
    """Modelo para representar una arista del grafo"""
    source: str
    target: str
    weight: float
    source_coords: List[float]
    target_coords: List[float]


class NavigationRequest(BaseModel):
    """Modelo para la solicitud de navegación"""
    query: str = Field(..., description="Consulta del usuario en lenguaje natural")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Estoy en Medicina Humana y quiero ir a Ingeniería Civil"
            }
        }


class PathStep(BaseModel):
    """Modelo para representar un paso en la ruta"""
    node_id: str
    latitude: float
    longitude: float
    is_school: bool
    school_name: Optional[str] = None
    distance_from_previous: Optional[float] = None


class PathResponse(BaseModel):
    """Modelo para la respuesta de una ruta calculada"""
    origin: str
    destination: str
    path: List[PathStep]
    total_distance: float
    node_count: int
    navigation_instructions: Optional[str] = None  # Instrucciones detalladas de navegación


class NavigationResponse(BaseModel):
    """Modelo para la respuesta completa de navegación"""
    success: bool
    message: str
    schools_detected: List[str]
    paths: List[PathResponse]
    total_route_distance: float
    detailed_instructions: Optional[str] = None  # Instrucciones completas para toda la ruta


class GraphInfo(BaseModel):
    """Modelo para información general del grafo"""
    total_nodes: int
    total_edges: int
    schools_count: int
    schools: List[dict]
