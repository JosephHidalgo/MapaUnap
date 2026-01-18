export interface PathStep {
  node_id: string;
  latitude: number;
  longitude: number;
  is_school: boolean;
  school_name: string | null;
  distance_from_previous: number | null;
}

export interface PathResponse {
  origin: string;
  destination: string;
  path: PathStep[];
  total_distance: number;
  node_count: number;
  navigation_instructions?: string;
}

export interface NavigationResponse {
  success: boolean;
  message: string;
  schools_detected: string[];
  paths: PathResponse[];
  total_route_distance: number;
  detailed_instructions?: string;
}

export interface School {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
}

export interface SchoolsResponse {
  schools: School[];
  count: number;
}

export interface Node {
  id: string;
  latitude: number;
  longitude: number;
  is_school: boolean;
  school_name: string | null;
}

export interface Edge {
  source: string;
  target: string;
  weight: number;
  source_coords: [number, number];
  target_coords: [number, number];
}

export interface GraphInfo {
  total_nodes: number;
  total_edges: number;
  schools_count: number;
  schools: School[];
  nodes?: Node[];
}
