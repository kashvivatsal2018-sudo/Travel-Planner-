"""Unit tests for the WeightedGraph data structure using adjacency list."""
import pytest
from graph.graph import WeightedGraph


def test_graph_initialization():
    g = WeightedGraph()
    assert g.vertex_count() == 0
    assert g.edge_count() == 0
    assert g.get_vertices() == []


def test_add_vertex_and_case_insensitivity():
    g = WeightedGraph()
    g.add_vertex("Delhi")
    g.add_vertex("delhi ")  # Same city with different case and whitespace

    assert g.vertex_count() == 1
    assert g.has_vertex("DELHI")
    assert g.has_vertex("delhi")
    assert g.get_canonical_name("delhi") == "Delhi"


def test_add_edge_bidirectional():
    g = WeightedGraph()
    g.add_edge("Dehradun", "Mussoorie", 35.0, bidirectional=True)

    assert g.vertex_count() == 2
    assert g.edge_count() == 2  # u->v and v->u
    assert g.get_edge_weight("Dehradun", "Mussoorie") == 35.0
    assert g.get_edge_weight("Mussoorie", "Dehradun") == 35.0

    neighbors_deh = g.get_neighbors("Dehradun")
    assert ("Mussoorie", 35.0) in neighbors_deh


def test_add_edge_directed():
    g = WeightedGraph()
    g.add_edge("CityA", "CityB", 10.0, bidirectional=False)

    assert g.get_edge_weight("CityA", "CityB") == 10.0
    assert g.get_edge_weight("CityB", "CityA") is None


def test_update_existing_edge_weight():
    g = WeightedGraph()
    g.add_edge("CityA", "CityB", 50.0)
    g.add_edge("CityA", "CityB", 42.0)  # Update weight

    assert g.get_edge_weight("CityA", "CityB") == 42.0
    assert g.edge_count() == 2  # Bidirectional pair
