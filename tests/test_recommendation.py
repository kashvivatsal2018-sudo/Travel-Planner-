"""Unit tests for the content-based recommendation engine."""
import pytest
from recommendation.recommender import RecommendationEngine
from graph.graph import WeightedGraph


class MockDestination:
    """Mock destination object mimicking SQLAlchemy model."""
    def __init__(self, id, name, category, secondary_cats, rating, cost_min, cost_max, days, companions=None):
        self.id = id
        self.name = name
        self.category = category
        self.secondary_categories = secondary_cats
        self.rating = rating
        self.avg_cost_min = cost_min
        self.avg_cost_max = cost_max
        self.recommended_days = days
        self.image_url = ""
        self.tagline = f"Test {name}"
        self.best_time = "October - March"
        self.suitable_companions = companions or ["Friends", "Couple", "Solo", "Family"]

    def get_all_categories(self):
        return [self.category] + self.secondary_categories

    def get_suitable_companions(self):
        return self.suitable_companions


@pytest.fixture
def sample_destinations():
    return [
        MockDestination(1, "Mussoorie", "Mountains", ["Nature", "Adventure"], 4.6, 5000, 9000, 3, ["Couple", "Friends"]),
        MockDestination(2, "Haridwar", "Religious", ["Cultural"], 4.5, 2500, 5000, 2, ["Family", "Solo"]),
        MockDestination(3, "Agra", "Historical", ["Cultural"], 4.6, 3000, 6500, 2, ["Family", "Couple"]),
        MockDestination(4, "Chopta", "Adventure", ["Mountains", "Nature"], 4.8, 4500, 8000, 3, ["Friends", "Solo"])
    ]


def test_recommendation_interest_alignment(sample_destinations):
    """User interested in Mountains & Adventure should rank Mussoorie and Chopta at the top."""
    recommender = RecommendationEngine()
    results = recommender.recommend(
        destinations=sample_destinations,
        preferred_categories=["Mountains", "Adventure"],
        budget_key="5000_10000",
        duration_key="2_3_days",
        travel_companion="Friends",
        visited_destinations=[],
        top_k=4
    )

    assert len(results) == 4
    top_dest_names = [r.name for r in results[:2]]
    assert "Mussoorie" in top_dest_names or "Chopta" in top_dest_names
    # Check explanations generated
    assert len(results[0].reasons) > 0


def test_recommendation_visited_deprioritization(sample_destinations):
    """If user has already visited Mussoorie, it should not be the top pick."""
    recommender = RecommendationEngine()
    results = recommender.recommend(
        destinations=sample_destinations,
        preferred_categories=["Mountains", "Adventure"],
        budget_key="5000_10000",
        duration_key="2_3_days",
        travel_companion="Friends",
        visited_destinations=["Mussoorie"],
        top_k=4
    )

    # Mussoorie is marked as previously visited and ranked lower than Chopta
    top_result = results[0]
    assert top_result.name != "Mussoorie"
    mussoorie_res = next(r for r in results if r.name == "Mussoorie")
    assert mussoorie_res.is_previously_visited is True


def test_recommendation_adjacent_hub_bonus():
    """Destination connected to a previously visited city receives an exploration bonus."""
    g = WeightedGraph()
    g.add_edge("Dehradun", "Mussoorie", 35.0)

    destinations = [
        MockDestination(1, "Mussoorie", "Mountains", ["Nature"], 4.6, 5000, 9000, 3),
        MockDestination(2, "Agra", "Historical", ["Cultural"], 4.6, 3000, 6500, 2)
    ]

    recommender = RecommendationEngine(graph=g)
    results = recommender.recommend(
        destinations=destinations,
        preferred_categories=["Mountains"],
        budget_key="5000_10000",
        duration_key="2_3_days",
        travel_companion="Friends",
        visited_destinations=["Dehradun"],
        top_k=2
    )

    mussoorie = results[0]
    assert mussoorie.name == "Mussoorie"
    # Should contain adjacent discovery reason
    assert any("adjacent" in r.lower() or "dehradun" in r.lower() for r in mussoorie.reasons)
