"""
Dynamic Budget Calculation Service.
Computes itemized trip expenses based on distance, duration, travelers, and spending tiers.
"""

import math
from typing import Dict, Any, Optional
from database import db
from database.models import Destination


class BudgetService:
    """Service for computing dynamic, itemized travel budgets."""

    # Transportation rates in INR per KM per person
    TRANSPORT_RATES = {
        "bus": 2.2,       # State/Volvo buses
        "train": 1.8,     # AC Chair Car / 3-Tier Sleeper
        "car": 9.0,       # Cab / self-drive shared among group
        "flight": 4.5,    # Short air route / premium
        "any": 2.5
    }

    # Accommodation room rates in INR per night
    HOTEL_RATES = {
        "budget": 900.0,      # Backpacker hostel / budget guest house
        "standard": 2200.0,   # 3-star hotel / boutique resort
        "luxury": 5500.0      # 4/5-star luxury heritage stay
    }

    # Daily food allowance in INR per person per day
    FOOD_RATES = {
        "budget": 350.0,      # Street food, dhabas, local thalis
        "moderate": 750.0,    # Good cafes, casual dining restaurants
        "premium": 1600.0     # Fine dining, multi-course meals, specialty drinks
    }

    @classmethod
    def calculate_budget(
        cls,
        distance_km: float = 250.0,
        days: int = 3,
        travelers: int = 2,
        transport_mode: str = "train",
        hotel_tier: str = "standard",
        food_tier: str = "moderate",
        destination_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate an itemized travel budget based on traveler parameters.
        """
        days = max(1, int(days))
        travelers = max(1, int(travelers))
        distance_km = max(10.0, float(distance_km))

        mode = (transport_mode or "train").lower()
        h_tier = (hotel_tier or "standard").lower()
        f_tier = (food_tier or "moderate").lower()

        # 1. Transportation Cost (Round trip = 2 * distance_km)
        round_trip_dist = distance_km * 2.0
        if mode == "car":
            # For car, fuel and toll is shared for the entire vehicle
            vehicle_count = math.ceil(travelers / 4.0)
            transport_cost = round_trip_dist * cls.TRANSPORT_RATES["car"] * vehicle_count
        else:
            per_person_rate = cls.TRANSPORT_RATES.get(mode, 2.5)
            transport_cost = round_trip_dist * per_person_rate * travelers

        # 2. Accommodation Cost
        # Assume 2 travelers per hotel room
        rooms_needed = math.ceil(travelers / 2.0)
        nights = max(1, days - 1)
        nightly_room_rate = cls.HOTEL_RATES.get(h_tier, 2200.0)
        accommodation_cost = nights * rooms_needed * nightly_room_rate

        # 3. Food & Dining Cost
        daily_food_rate = cls.FOOD_RATES.get(f_tier, 750.0)
        food_cost = days * travelers * daily_food_rate

        # 4. Activities & Sightseeing
        activities_cost = 0.0
        if destination_id:
            dest = db.session.get(Destination, destination_id)
            if dest and dest.tourist_places:
                # Sum actual entry costs for the destination
                total_entry_per_person = sum(p.entry_cost for p in dest.tourist_places)
                activities_cost = total_entry_per_person * travelers
        
        # Fallback activity cost if no entry fees or zero
        if activities_cost == 0:
            activities_cost = 400.0 * days * travelers

        # 5. Miscellaneous / Buffer (10% of subtotal)
        subtotal = transport_cost + accommodation_cost + food_cost + activities_cost
        misc_cost = round(subtotal * 0.08, 0)  # 8% emergency & shopping buffer

        total_cost = subtotal + misc_cost
        per_person = round(total_cost / travelers, 0)

        return {
            "travelers": travelers,
            "days": days,
            "nights": nights,
            "rooms": rooms_needed,
            "distance_km": round(distance_km, 1),
            "transport_mode": mode.capitalize(),
            "hotel_tier": h_tier.capitalize(),
            "food_tier": f_tier.capitalize(),
            "breakdown": {
                "transportation": round(transport_cost, 0),
                "accommodation": round(accommodation_cost, 0),
                "food": round(food_cost, 0),
                "activities": round(activities_cost, 0),
                "miscellaneous": round(misc_cost, 0)
            },
            "total_estimated_budget": round(total_cost, 0),
            "cost_per_person": per_person,
            "percentages": {
                "transportation": round((transport_cost / total_cost) * 100, 1),
                "accommodation": round((accommodation_cost / total_cost) * 100, 1),
                "food": round((food_cost / total_cost) * 100, 1),
                "activities": round((activities_cost / total_cost) * 100, 1),
                "miscellaneous": round((misc_cost / total_cost) * 100, 1)
            }
        }
