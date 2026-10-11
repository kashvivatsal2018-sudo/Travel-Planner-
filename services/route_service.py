"""
Route Service: Integrates database RouteEdge records with WeightedGraph and Dijkstra's algorithm.
Provides geographic coordinates for Leaflet map visualization.
"""

from typing import Dict, Any, List, Optional
from graph.graph import WeightedGraph
from graph.dijkstra import dijkstra, DijkstraResult
from database.models import RouteEdge, Destination


class RouteService:
    """Service to load graph from database, run Dijkstra, and provide map-ready route objects."""

    _cached_graph: Optional[WeightedGraph] = None

    @classmethod
    def get_or_build_graph(cls, force_reload: bool = False) -> WeightedGraph:
        """
        Build WeightedGraph instance from database RouteEdge entries.
        Caches the graph in memory for optimal query performance.
        """
        if cls._cached_graph is not None and not force_reload:
            return cls._cached_graph

        graph = WeightedGraph()

        # Add all destinations as vertices (ensures even isolated nodes exist in graph)
        destinations = Destination.query.all()
        for d in destinations:
            graph.add_vertex(d.name)

        # Add all edges
        routes = RouteEdge.query.all()
        for r in routes:
            graph.add_edge(r.source, r.destination, r.distance, bidirectional=True)

        cls._cached_graph = graph
        return graph

    @classmethod
    def find_shortest_route(cls, source: str, destination: str) -> Dict[str, Any]:
        """
        Executes manual Dijkstra shortest path algorithm and enriches the response
        with node coordinates, city details, and Leaflet polyline waypoints.
        """
        graph = cls.get_or_build_graph()
        result: DijkstraResult = dijkstra(graph, source, destination)

        if not result.success:
            return {
                "success": False,
                "error": result.message,
                "source": source,
                "destination": destination,
                "total_distance": 0,
                "path": [],
                "waypoints": [],
                "segments": [],
                "relaxation_steps": result.relaxation_steps
            }

        # Build coordinate waypoints for Leaflet map polyline & markers
        waypoints = []
        destination_details = []

        for city_name in result.path:
            dest_record = Destination.query.filter(Destination.name.ilike(city_name)).first()
            if dest_record:
                wp = {
                    "name": dest_record.name,
                    "latitude": dest_record.latitude,
                    "longitude": dest_record.longitude,
                    "category": dest_record.category,
                    "rating": dest_record.rating,
                    "image_url": dest_record.image_url,
                    "tagline": dest_record.tagline,
                    "recommended_days": dest_record.recommended_days
                }
                destination_details.append(dest_record.to_dict())
            else:
                # Fallback coordinates if city is purely a transit node
                wp = {
                    "name": city_name,
                    "latitude": 28.6139,
                    "longitude": 77.2090,
                    "category": "Transit",
                    "rating": 4.0,
                    "image_url": "",
                    "tagline": "Transit Waypoint"
                }
            waypoints.append(wp)

        # Get detailed target destination information
        target_dest = Destination.query.filter(Destination.name.ilike(destination)).first()
        target_info = None
        if target_dest:
            target_info = {
                "id": target_dest.id,
                "name": target_dest.name,
                "category": target_dest.category,
                "description": target_dest.description,
                "rating": target_dest.rating,
                "best_time": target_dest.best_time,
                "recommended_days": target_dest.recommended_days,
                "avg_cost_min": target_dest.avg_cost_min,
                "avg_cost_max": target_dest.avg_cost_max,
                "image_url": target_dest.image_url,
                "tourist_places": [p.to_dict() for p in target_dest.tourist_places],
                "restaurants": [r.to_dict() for r in target_dest.restaurants],
                "reviews": [rev.to_dict() for rev in target_dest.reviews]
            }

        return {
            "success": True,
            "source": result.source,
            "destination": result.destination,
            "total_distance": round(result.total_distance, 1),
            "hop_count": len(result.path) - 1,
            "path": result.path,
            "segments": result.segments,
            "waypoints": waypoints,
            "visited_count": len(result.visited_nodes),
            "visited_nodes": result.visited_nodes,
            "relaxation_steps_count": len(result.relaxation_steps),
            "relaxation_steps": result.relaxation_steps,
            "target_destination": target_info,
            "message": result.message
        }
