"""Unit tests for the dynamic ItineraryService."""
import pytest
from app import create_app
from services.itinerary_service import ItineraryService
from database.models import Destination


@pytest.fixture
def app_context():
    app = create_app()
    with app.app_context():
        yield app


def test_itinerary_generation_days(app_context):
    """Verify that a 3-day itinerary generates exactly 3 day plans."""
    dest = Destination.query.filter_by(name="Mussoorie").first()
    assert dest is not None

    itinerary = ItineraryService.generate_itinerary(dest.id, duration_days=3)
    assert itinerary["success"] is True
    assert itinerary["destination_name"] == "Mussoorie"
    assert len(itinerary["days"]) == 3

    # Check Day 1 slots
    day1 = itinerary["days"][0]
    assert day1["day_number"] == 1
    assert len(day1["slots"]) >= 4

    # Slot periods must include Morning, Afternoon, Evening/Night
    periods = [s["period"] for s in day1["slots"]]
    assert "Morning" in periods
    assert "Afternoon" in periods


def test_itinerary_invalid_destination(app_context):
    """Unknown destination id must gracefully return error dict."""
    itinerary = ItineraryService.generate_itinerary(99999, duration_days=3)
    assert itinerary["success"] is False
    assert "not found" in itinerary["error"].lower()
