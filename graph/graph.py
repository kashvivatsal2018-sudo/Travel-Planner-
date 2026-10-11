"""
Graph Data Structure Implementation using Adjacency List.

Academic Context:
-----------------
A Weighted Undirected/Directed Graph G = (V, E) where:
- V is the set of vertices (cities/destinations)
- E is the set of edges (road connections) with non-negative weights (distance in km).

Why Adjacency List?
- Space Complexity: O(|V| + |E|), optimal for sparse graphs like road networks
  where each city is only connected to a few neighboring cities (average degree << |V|).
- Time Complexity to retrieve neighbors: O(deg(u)), proportional to the number of roads out of city u.
- Contrast with Adjacency Matrix: Matrix requires O(|V|^2) space and O(|V|) time to inspect neighbors,
  which wastes memory when |E| << |V|^2.
"""

from collections import defaultdict
from typing import Dict, List, Tuple, Set, Optional


class WeightedGraph:
    """
    Weighted Graph represented using an Adjacency List.
    Internal Structure:
        adjacency_list = {
            "CityA": [("CityB", distance_AB), ("CityC", distance_AC)],
            "CityB": [("CityA", distance_AB)],
            ...
        }
    """

    def __init__(self):
        # Maps each vertex to a list of (neighbor_vertex, edge_weight) tuples
        self.adjacency_list: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        self._vertices: Set[str] = set()

    def add_vertex(self, vertex: str) -> None:
        """
        Add a vertex (city) to the graph.
        Time Complexity: O(1)
        """
        vertex = vertex.strip()
        canonical = self.get_canonical_name(vertex)
        if not canonical:
            self._vertices.add(vertex)
            # Ensure vertex exists as a key even if it has no incident edges
            _ = self.adjacency_list[vertex]

    def add_edge(self, u: str, v: str, weight: float, bidirectional: bool = True) -> None:
        """
        Add a weighted edge between vertex u and vertex v.
        If bidirectional=True, adds edges in both directions (undirected road).
        Time Complexity: O(1)
        """
        u = u.strip()
        v = v.strip()
        weight = float(weight)

        self.add_vertex(u)
        self.add_vertex(v)

        # Avoid duplicate edges: update weight if already exists, else append
        self._upsert_neighbor(u, v, weight)
        if bidirectional:
            self._upsert_neighbor(v, u, weight)

    def _upsert_neighbor(self, u: str, v: str, weight: float) -> None:
        """Helper to insert or update an edge from u to v."""
        for i, (neighbor, _) in enumerate(self.adjacency_list[u]):
            if neighbor.lower() == v.lower():
                self.adjacency_list[u][i] = (neighbor, weight)
                return
        self.adjacency_list[u].append((v, weight))

    def get_neighbors(self, vertex: str) -> List[Tuple[str, float]]:
        """
        Get all adjacent vertices and their edge weights for a given vertex.
        Returns: List of tuples [(neighbor_city, distance_km), ...]
        Time Complexity: O(deg(V))
        """
        # Case-insensitive lookup matching stored vertex
        canonical_vertex = self.get_canonical_name(vertex)
        if canonical_vertex:
            return list(self.adjacency_list[canonical_vertex])
        return []

    def get_canonical_name(self, vertex: str) -> Optional[str]:
        """Find the matching vertex name preserving original case."""
        target = vertex.strip().lower()
        for v in self._vertices:
            if v.lower() == target:
                return v
        return None

    def has_vertex(self, vertex: str) -> bool:
        """Check if vertex exists in the graph."""
        return self.get_canonical_name(vertex) is not None

    def get_vertices(self) -> List[str]:
        """Return list of all vertex names in the graph."""
        return sorted(list(self._vertices))

    def vertex_count(self) -> int:
        """Return total number of vertices |V|."""
        return len(self._vertices)

    def edge_count(self) -> int:
        """
        Return total number of directed edges |E|.
        For an undirected graph, undirected edges = edge_count() / 2.
        """
        return sum(len(neighbors) for neighbors in self.adjacency_list.values())

    def get_edge_weight(self, u: str, v: str) -> Optional[float]:
        """Return distance weight between u and v if edge exists, else None."""
        u_canon = self.get_canonical_name(u)
        v_canon = self.get_canonical_name(v)
        if not u_canon or not v_canon:
            return None
        for neighbor, weight in self.adjacency_list[u_canon]:
            if neighbor.lower() == v_canon.lower():
                return weight
        return None

    def to_dict(self) -> Dict[str, List[Dict[str, float]]]:
        """Convert adjacency list to JSON-serializable dictionary."""
        return {
            v: [{"to": n, "distance": w} for n, w in neighbors]
            for v, neighbors in self.adjacency_list.items()
        }
