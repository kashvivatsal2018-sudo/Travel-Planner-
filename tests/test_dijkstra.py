"""Unit tests for Dijkstra's shortest path algorithm implementation."""
import pytest
from graph.graph import WeightedGraph
from graph.dijkstra import dijkstra, DijkstraResult


@pytest.fixture
def academic_sample_graph():
    """Graph matching the academic problem statement example."""
    g = WeightedGraph()
    # Dehradun -> Mussoorie (35) -> Dhanaulti (60)
    g.add_edge("Dehradun", "Mussoorie", 35.0)
    g.add_edge("Mussoorie", "Dhanaulti", 60.0)
    g.add_edge("Dehradun", "Rishikesh", 45.0)
    g.add_edge("Rishikesh", "Haridwar", 25.0)
    g.add_edge("Delhi", "Dehradun", 250.0)
    g.add_edge("Delhi", "Haridwar", 215.0)
    return g


def test_dijkstra_academic_example(academic_sample_graph):
    """Verify Dehradun -> Dhanaulti yields 95.0 km through Mussoorie."""
    result = dijkstra(academic_sample_graph, "Dehradun", "Dhanaulti")
    assert result.success is True
    assert result.total_distance == 95.0
    assert result.path == ["Dehradun", "Mussoorie", "Dhanaulti"]
    assert len(result.segments) == 2
    assert result.segments[0] == {"from": "Dehradun", "to": "Mussoorie", "distance": 35.0}
    assert result.segments[1] == {"from": "Mussoorie", "to": "Dhanaulti", "distance": 60.0}


def test_dijkstra_alternative_path_optimization():
    """
    Test diamond graph where path with more hops has lower total distance:
    A -> B: 100 km (1 hop)
    A -> C: 30 km, C -> B: 40 km (2 hops, total 70 km)
    Dijkstra must pick A -> C -> B (70 km).
    """
    g = WeightedGraph()
    g.add_edge("A", "B", 100.0)
    g.add_edge("A", "C", 30.0)
    g.add_edge("C", "B", 40.0)

    result = dijkstra(g, "A", "B")
    assert result.success is True
    assert result.total_distance == 70.0
    assert result.path == ["A", "C", "B"]


def test_dijkstra_same_source_and_destination(academic_sample_graph):
    """Source == Destination must return 0 distance and 1-element path."""
    result = dijkstra(academic_sample_graph, "Dehradun", "Dehradun")
    assert result.success is True
    assert result.total_distance == 0.0
    assert result.path == ["Dehradun"]
    assert result.segments == []


def test_dijkstra_unknown_vertex(academic_sample_graph):
    """Non-existent vertex must return failure result gracefully."""
    res1 = dijkstra(academic_sample_graph, "Atlantis", "Dehradun")
    assert res1.success is False
    assert "not found" in res1.message

    res2 = dijkstra(academic_sample_graph, "Dehradun", "Mordor")
    assert res2.success is False
    assert "not found" in res2.message


def test_dijkstra_disconnected_graph():
    """Two isolated components must report no route available."""
    g = WeightedGraph()
    g.add_edge("IslandA", "IslandB", 20.0)
    g.add_edge("MainlandX", "MainlandY", 50.0)

    result = dijkstra(g, "IslandA", "MainlandX")
    assert result.success is False
    assert result.total_distance == float("inf")
    assert "No connected road route" in result.message


def test_dijkstra_relaxation_steps_recorded(academic_sample_graph):
    """Verify relaxation diagnostic steps for viva demonstration."""
    result = dijkstra(academic_sample_graph, "Dehradun", "Dhanaulti")
    assert len(result.relaxation_steps) > 0
    first_step = result.relaxation_steps[0]
    assert "current_node" in first_step
    assert "neighbor" in first_step
    assert "old_distance" in first_step
    assert "tentative_distance" in first_step
    assert "relaxed" in first_step
