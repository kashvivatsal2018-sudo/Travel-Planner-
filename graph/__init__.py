"""Graph data structures and algorithms package."""
from graph.graph import WeightedGraph
from graph.dijkstra import dijkstra, DijkstraResult

__all__ = ["WeightedGraph", "dijkstra", "DijkstraResult"]
