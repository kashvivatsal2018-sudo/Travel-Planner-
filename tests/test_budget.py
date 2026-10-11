"""Unit tests for the dynamic BudgetService."""
import pytest
from services.budget_service import BudgetService


def test_budget_calculation_structure():
    """Verify all breakdown components exist and sum correctly."""
    result = BudgetService.calculate_budget(
        distance_km=200.0,
        days=3,
        travelers=2,
        transport_mode="train",
        hotel_tier="standard",
        food_tier="moderate"
    )

    assert "total_estimated_budget" in result
    assert "cost_per_person" in result
    assert "breakdown" in result

    breakdown = result["breakdown"]
    assert "transportation" in breakdown
    assert "accommodation" in breakdown
    assert "food" in breakdown
    assert "activities" in breakdown
    assert "miscellaneous" in breakdown

    computed_sum = sum(breakdown.values())
    assert result["total_estimated_budget"] == round(computed_sum, 0)
    assert result["cost_per_person"] == round(result["total_estimated_budget"] / 2, 0)


def test_budget_transport_modes():
    """Test that car cost is vehicle-based while train is person-based."""
    train_budget = BudgetService.calculate_budget(distance_km=300, days=2, travelers=4, transport_mode="train")
    car_budget = BudgetService.calculate_budget(distance_km=300, days=2, travelers=4, transport_mode="car")

    # Round trip = 600km.
    # Train: 600 * 1.8 * 4 = 4320
    # Car: 600 * 9.0 * 1 car = 5400
    assert train_budget["breakdown"]["transportation"] == 4320.0
    assert car_budget["breakdown"]["transportation"] == 5400.0


def test_budget_hotel_tiers():
    """Higher comfort level hotel tiers must increase accommodation costs."""
    budget_tier = BudgetService.calculate_budget(days=3, travelers=2, hotel_tier="budget")
    standard_tier = BudgetService.calculate_budget(days=3, travelers=2, hotel_tier="standard")
    luxury_tier = BudgetService.calculate_budget(days=3, travelers=2, hotel_tier="luxury")

    assert budget_tier["breakdown"]["accommodation"] < standard_tier["breakdown"]["accommodation"]
    assert standard_tier["breakdown"]["accommodation"] < luxury_tier["breakdown"]["accommodation"]
