from fastapi import APIRouter, HTTPException
from typing import List
from ..models.schemas import (
    NavigationRequest, 
    NavigationResponse, 
    PathResponse, 
    PathStep,
    GraphInfo
)
from ..services.pathfinding import AStarPathfinder
from ..services.openai_service import OpenAIService

router = APIRouter(prefix="/api", tags=["navigation"])

pathfinder = AStarPathfinder()
openai_service = OpenAIService(required=False)


@router.post("/navigate", response_model=NavigationResponse)
async def navigate(request: NavigationRequest):
    """
    Procesa una consulta de navegación en lenguaje natural y calcula las rutas
    
    Args:
        request: Objeto con la consulta del usuario
        
    Returns:
        Respuesta con las rutas calculadas y la información de navegación
    """
    try:
        # Obtener todas las escuelas disponibles
        all_schools = pathfinder.get_all_schools()
        school_names = [school['name'] for school in all_schools]
        
        detected_schools = openai_service.extract_schools_from_query(
            request.query, 
            school_names
        )
        
        if not detected_schools:
            return NavigationResponse(
                success=False,
                message="No se pudieron identificar escuelas en tu consulta. Por favor, menciona las escuelas profesionales que deseas visitar.",
                schools_detected=[],
                paths=[],
                total_route_distance=0.0
            )
        
        if len(detected_schools) < 2:
            return NavigationResponse(
                success=False,
                message=f"Se necesitan al menos 2 escuelas para calcular una ruta. Solo se detectó: {', '.join(detected_schools)}",
                schools_detected=detected_schools,
                paths=[],
                total_route_distance=0.0
            )
        
        # Calcular rutas entre las escuelas consecutivas
        paths = []
        total_route_distance = 0.0
        
        for i in range(len(detected_schools) - 1):
            origin_name = detected_schools[i]
            destination_name = detected_schools[i + 1]
            
            # Encontrar IDs de los nodos
            origin_id = pathfinder.find_school_by_name(origin_name)
            destination_id = pathfinder.find_school_by_name(destination_name)
            
            if not origin_id or not destination_id:
                return NavigationResponse(
                    success=False,
                    message=f"No se pudo encontrar una de las escuelas: {origin_name} o {destination_name}",
                    schools_detected=detected_schools,
                    paths=[],
                    total_route_distance=0.0
                )
            
            # Calcular ruta con A*
            path_nodes, distance = pathfinder.find_path(origin_id, destination_id)
            
            if not path_nodes:
                return NavigationResponse(
                    success=False,
                    message=f"No se encontró una ruta entre {origin_name} y {destination_name}",
                    schools_detected=detected_schools,
                    paths=[],
                    total_route_distance=0.0
                )
            
            path_steps = []
            for j, node_id in enumerate(path_nodes):
                node_info = pathfinder.get_node_info(node_id)
                
                distance_from_prev = None
                if j > 0:
                    prev_node_id = path_nodes[j - 1]
                    for neighbor, weight in pathfinder.edges[prev_node_id]:
                        if neighbor == node_id:
                            distance_from_prev = weight
                            break
                
                path_steps.append(PathStep(
                    node_id=node_id,
                    latitude=node_info['latitude'],
                    longitude=node_info['longitude'],
                    is_school=node_info['is_school'],
                    school_name=node_info['school_name'],
                    distance_from_previous=distance_from_prev
                ))
            
            navigation_instructions = openai_service.generate_detailed_navigation_instructions(
                path_steps=[step.dict() for step in path_steps],
                origin_name=origin_name,
                destination_name=destination_name,
                total_distance=distance
            )            
            paths.append(PathResponse(
                origin=origin_name,
                destination=destination_name,
                path=path_steps,
                total_distance=distance,
                node_count=len(path_nodes),
                navigation_instructions=navigation_instructions
            ))
            
            total_route_distance += distance
        
        # Generar instrucciones completas para toda la ruta si hay múltiples tramos
        detailed_instructions = None
        if len(paths) > 0:
            if len(paths) == 1:
                detailed_instructions = paths[0].navigation_instructions
            else:
                # Combinar instrucciones de todos los tramos
                all_instructions = []
                for idx, path in enumerate(paths, 1):
                    all_instructions.append(f"Tramo {idx}: {path.origin} → {path.destination}")
                    all_instructions.append(path.navigation_instructions)
                    all_instructions.append("")
                detailed_instructions = "\n".join(all_instructions)
        
        return NavigationResponse(
            success=True,
            message=f"Ruta calculada exitosamente. Distancia total: {total_route_distance:.2f} metros",
            schools_detected=detected_schools,
            paths=paths,
            total_route_distance=total_route_distance,
            detailed_instructions=detailed_instructions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la navegación: {str(e)}")


@router.get("/graph/info", response_model=GraphInfo)
async def get_graph_info():
    """
    Obtiene información general del grafo
    
    Returns:
        Información sobre nodos, aristas y escuelas
    """
    try:
        stats = pathfinder.get_graph_stats()
        return GraphInfo(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener información del grafo: {str(e)}")


@router.get("/schools")
async def get_all_schools():
    """
    Obtiene la lista de todas las escuelas disponibles
    
    Returns:
        Lista de escuelas con su información
    """
    try:
        schools = pathfinder.get_all_schools()
        return {"schools": schools, "count": len(schools)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener escuelas: {str(e)}")


@router.get("/graph/nodes")
async def get_all_nodes():
    """
    Obtiene todos los nodos del grafo (escuelas y nodos regulares)
    
    Returns:
        Lista de todos los nodos con su información
    """
    try:
        nodes = pathfinder.get_all_nodes()
        return {"nodes": nodes, "count": len(nodes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener nodos: {str(e)}")


@router.get("/graph/edges")
async def get_all_edges():
    """
    Obtiene todas las aristas del grafo
    
    Returns:
        Lista de todas las aristas con sus coordenadas
    """
    try:
        edges = pathfinder.get_all_edges()
        return {"edges": edges, "count": len(edges)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener aristas: {str(e)}")


@router.get("/path/{origin_id}/{destination_id}")
async def calculate_path(origin_id: str, destination_id: str):
    """
    Calcula la ruta más corta entre dos nodos específicos
    
    Args:
        origin_id: ID del nodo de origen
        destination_id: ID del nodo de destino
        
    Returns:
        Información de la ruta calculada
    """
    try:
        origin_info = pathfinder.get_node_info(origin_id)
        destination_info = pathfinder.get_node_info(destination_id)
        
        if not origin_info or not destination_info:
            raise HTTPException(status_code=404, detail="Uno o ambos nodos no existen")
        
        # Calcular ruta
        path_nodes, distance = pathfinder.find_path(origin_id, destination_id)
        
        if not path_nodes:
            raise HTTPException(status_code=404, detail="No se encontró una ruta entre los nodos")
        
        # Construir respuesta
        path_steps = []
        for i, node_id in enumerate(path_nodes):
            node_info = pathfinder.get_node_info(node_id)
            
            distance_from_prev = None
            if i > 0:
                prev_node_id = path_nodes[i - 1]
                for neighbor, weight in pathfinder.edges[prev_node_id]:
                    if neighbor == node_id:
                        distance_from_prev = weight
                        break
            
            path_steps.append({
                "node_id": node_id,
                "latitude": node_info['latitude'],
                "longitude": node_info['longitude'],
                "is_school": node_info['is_school'],
                "school_name": node_info['school_name'],
                "distance_from_previous": distance_from_prev
            })
        
        return {
            "origin_id": origin_id,
            "destination_id": destination_id,
            "path": path_steps,
            "total_distance": distance,
            "node_count": len(path_nodes)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular la ruta: {str(e)}")
