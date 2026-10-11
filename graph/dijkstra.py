"""
Manual Implementation of Dijkstra's Single-Source Shortest Path Algorithm.

Academic & Viva Concepts:
-------------------------
Dijkstra's algorithm solves the single-source shortest path problem on a
weighted graph with non-negative edge weights.

Algorithmic Strategy: Greedy Algorithm
- Maintains a priority queue (min-heap) of vertices ordered by their tentative distance from the source.
- At each step, it extracts the vertex `u` with the smallest known tentative distance.
- It explores all outgoing edges (u, v) and performs 'edge relaxation':
    If dist[u] + weight(u, v) < dist[v]:
        dist[v] = dist[u] + weight(u, v)
        previous[v] = u
        push (dist[v], v) into the min-heap

Time Complexity Analysis:
-------------------------
Using a Min-Heap (Binary Heap via Python's standard `heapq` module):
1. Initialization: O(|V|) to initialize distance and predecessor tables.
2. Extract-Min: Called at most |V| times, each taking O(log |V|) -> O(|V| log |V|).
3. Decrease-Key / Push: In the worst case, every edge is relaxed once and pushed to the heap -> O(|E| log |V|).
Total Time Complexity: O((|V| + |E|) log |V|)
For sparse graphs where |E| is on the order of |V|, this is significantly faster than the O(|V|^2)
array-based implementation.

Space Complexity Analysis:
--------------------------
1. Min-Heap: Stores up to O(|E|) entries during traversal.
2. Distance dictionary: O(|V|)
3. Predecessor (previous_nodes) dictionary: O(|V|)
4. Visited set: O(|V|)
Total Space Complexity: O(|V| + |E|)
"""

import heapq
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from graph.graph import WeightedGraph


@dataclass
class DijkstraResult:
    """Encapsulates the complete result of running Dijkstra's algorithm."""
    source: str
    destination: str
    success: bool
    total_distance: float
    path: List[str] = field(default_factory=list)
    segments: List[Dict[str, Any]] = field(default_factory=list)
    visited_nodes: List[str] = field(default_factory=list)
    relaxation_steps: List[Dict[str, Any]] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dictionary for JSON API responses."""
        return {
            "source": self.source,
            "destination": self.destination,
            "success": self.success,
            "total_distance": round(self.total_distance, 2),
            "path": self.path,
            "hop_count": max(0, len(self.path) - 1),
            "segments": self.segments,
            "visited_count": len(self.visited_nodes),
            "visited_nodes": self.visited_nodes,
            "relaxation_steps_count": len(self.relaxation_steps),
            "relaxation_steps": self.relaxation_steps,
            "message": self.message
        }


def dijkstra(graph: WeightedGraph, start_vertex: str, end_vertex: str) -> DijkstraResult:
    """
    Computes the shortest path from start_vertex to end_vertex on graph.

    Args:
        graph: An instance of WeightedGraph with adjacency list representation.
        start_vertex: Source city name.
        end_vertex: Target destination city name.

    Returns:
        DijkstraResult containing the optimal path, segment distances,
        total road distance, and complete step-by-step relaxation trace for viva.
    """
    # 1. Input Validation and Canonical Case Resolution
    canonical_start = graph.get_canonical_name(start_vertex)
    canonical_end = graph.get_canonical_name(end_vertex)

    if not canonical_start:
        return DijkstraResult(
            source=start_vertex,
            destination=end_vertex,
            success=False,
            total_distance=float("inf"),
            message=f"Starting location '{start_vertex}' not found in the road network."
        )

    if not canonical_end:
        return DijkstraResult(
            source=start_vertex,
            destination=end_vertex,
            success=False,
            total_distance=float("inf"),
            message=f"Destination location '{end_vertex}' not found in the road network."
        )

    # Edge Case: Source is identical to Destination
    if canonical_start.lower() == canonical_end.lower():
        return DijkstraResult(
            source=canonical_start,
            destination=canonical_end,
            success=True,
            total_distance=0.0,
            path=[canonical_start],
            segments=[],
            visited_nodes=[canonical_start],
            relaxation_steps=[],
            message="Source and destination are identical. Total travel distance is 0 km."
        )

    # 2. Initialization of Data Structures
    all_vertices = graph.get_vertices()
    distances: Dict[str, float] = {v: float("inf") for v in all_vertices}
    previous_nodes: Dict[str, Optional[str]] = {v: None for v in all_vertices}
    visited: set = set()

    distances[canonical_start] = 0.0

    # Min-Heap Priority Queue storing tuples: (distance_so_far, vertex_name)
    # The smallest distance always floats to the top (heapq min-heap property).
    priority_queue: List[Tuple[float, str]] = []
    heapq.heappush(priority_queue, (0.0, canonical_start))

    visited_order: List[str] = []
    relaxation_steps: List[Dict[str, Any]] = []
    step_counter = 0

    # 3. Main Dijkstra Loop
    while priority_queue:
        # Greedy choice: Extract vertex with minimum tentative distance
        current_distance, current_vertex = heapq.heappop(priority_queue)

        # If already finalized with a shorter path, skip (handles duplicate heap entries)
        if current_vertex in visited:
            continue

        visited.add(current_vertex)
        visited_order.append(current_vertex)

        # Early termination: if we reached the target destination, we have found the optimal path
        if current_vertex.lower() == canonical_end.lower():
            break

        # If smallest distance remaining is infinity, the remaining nodes are unreachable
        if current_distance == float("inf"):
            break

        # 4. Explore all adjacent neighbors (Edge Relaxation)
        for neighbor, weight in graph.get_neighbors(current_vertex):
            if neighbor in visited:
                continue

            tentative_distance = current_distance + weight
            old_distance = distances[neighbor]
            step_counter += 1

            step_record = {
                "step": step_counter,
                "current_node": current_vertex,
                "neighbor": neighbor,
                "edge_weight": weight,
                "old_distance": "∞" if old_distance == float("inf") else round(old_distance, 1),
                "tentative_distance": round(tentative_distance, 1),
                "relaxed": tentative_distance < old_distance
            }
            relaxation_steps.append(step_record)

            # Relaxation Condition
            if tentative_distance < old_distance:
                distances[neighbor] = tentative_distance
                previous_nodes[neighbor] = current_vertex
                heapq.heappush(priority_queue, (tentative_distance, neighbor))

    # 5. Path Reconstruction
    # If the destination distance remains infinity, no valid path exists between them
    if distances[canonical_end] == float("inf"):
        return DijkstraResult(
            source=canonical_start,
            destination=canonical_end,
            success=False,
            total_distance=float("inf"),
            visited_nodes=visited_order,
            relaxation_steps=relaxation_steps,
            message=f"No connected road route found between {canonical_start} and {canonical_end}."
        )

    # Backtrack from destination to source using previous_nodes map
    reconstructed_path: List[str] = []
    curr: Optional[str] = canonical_end
    while curr is not None:
        reconstructed_path.append(curr)
        curr = previous_nodes[curr]
    reconstructed_path.reverse()

    # 6. Build Detailed Segment Information
    segments: List[Dict[str, Any]] = []
    for i in range(len(reconstructed_path) - 1):
        u = reconstructed_path[i]
        v = reconstructed_path[i + 1]
        weight = graph.get_edge_weight(u, v) or 0.0
        segments.append({
            "from": u,
            "to": v,
            "distance": weight
        })

    return DijkstraResult(
        source=canonical_start,
        destination=canonical_end,
        success=True,
        total_distance=distances[canonical_end],
        path=reconstructed_path,
        segments=segments,
        visited_nodes=visited_order,
        relaxation_steps=relaxation_steps,
        message=f"Optimal shortest route found ({round(distances[canonical_end], 1)} km across {len(segments)} segments)."
    )
