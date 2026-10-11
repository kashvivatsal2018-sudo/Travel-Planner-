"""
Dynamic Day-Wise Itinerary Generator.
Generates customized day-by-day schedules dynamically from the destination's tourist places and restaurants.
"""

from typing import Dict, Any, List, Optional
from database import db
from database.models import Destination, TouristPlace, Restaurant


class ItineraryService:
    """Service to dynamically synthesize structured day-by-day travel itineraries."""

    @classmethod
    def generate_itinerary(
        cls,
        destination_id: int,
        duration_days: int = 3,
        budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Dynamically construct a multi-day itinerary for destination_id.
        """
        dest = db.session.get(Destination, destination_id)
        if not dest:
            return {"success": False, "error": f"Destination ID {destination_id} not found."}

        duration_days = max(1, min(7, int(duration_days)))

        places: List[TouristPlace] = dest.tourist_places
        restaurants: List[Restaurant] = dest.restaurants

        # Segregate attractions by best time of day
        morning_spots = [p for p in places if p.best_time_of_day.lower() == "morning"]
        afternoon_spots = [p for p in places if p.best_time_of_day.lower() == "afternoon"]
        evening_spots = [p for p in places if p.best_time_of_day.lower() == "evening"]

        # Pool remaining unassigned spots
        all_places_pool = list(places)

        days_schedule = []
        place_idx = 0
        rest_idx = 0

        for day_num in range(1, duration_days + 1):
            day_plan = {
                "day_number": day_num,
                "title": f"Day {day_num}: " + (
                    "Arrival & Local Immersion" if day_num == 1 else
                    ("Farewell & Departure" if day_num == duration_days and duration_days > 1 else "Exploring Highlights & Culture")
                ),
                "slots": [],
                "day_entry_total": 0.0
            }

            # ---------------------------------------------------------
            # Morning Slot
            # ---------------------------------------------------------
            if day_num == 1:
                day_plan["slots"].append({
                    "time": "09:00 AM - 11:30 AM",
                    "period": "Morning",
                    "type": "logistics",
                    "title": f"Arrival & Check-in at {dest.name}",
                    "description": f"Arrive in {dest.name}, check into hotel, refresh, and unpack.",
                    "cost": 0.0,
                    "icon": "hotel"
                })
            else:
                # Morning attraction
                m_place = morning_spots.pop(0) if morning_spots else (all_places_pool[place_idx % len(all_places_pool)] if all_places_pool else None)
                if m_place:
                    if m_place in all_places_pool:
                        place_idx += 1
                    day_plan["day_entry_total"] += m_place.entry_cost
                    day_plan["slots"].append({
                        "time": "09:30 AM - 12:30 PM",
                        "period": "Morning",
                        "type": "attraction",
                        "title": m_place.name,
                        "description": m_place.description,
                        "category": m_place.category,
                        "rating": m_place.rating,
                        "duration_hours": m_place.visit_duration,
                        "cost": m_place.entry_cost,
                        "icon": "map-pin"
                    })
                else:
                    day_plan["slots"].append({
                        "time": "09:30 AM - 12:00 PM",
                        "period": "Morning",
                        "type": "activity",
                        "title": "Morning Nature Walk & Photography",
                        "description": f"Take a tranquil morning walk enjoying scenic mountain breezes and capturing photos around {dest.name}.",
                        "cost": 0.0,
                        "icon": "camera"
                    })

            # ---------------------------------------------------------
            # Lunch Slot
            # ---------------------------------------------------------
            lunch_rest = restaurants[rest_idx % len(restaurants)] if restaurants else None
            rest_idx += 1
            if lunch_rest:
                day_plan["slots"].append({
                    "time": "01:00 PM - 02:15 PM",
                    "period": "Afternoon",
                    "type": "dining",
                    "title": f"Lunch at {lunch_rest.name}",
                    "description": f"Enjoy authentic {lunch_rest.cuisine} at {lunch_rest.location}. Must try: {lunch_rest.popular_dishes or 'Chef Special'}.",
                    "rating": lunch_rest.rating,
                    "cost": lunch_rest.avg_cost_per_person,
                    "icon": "utensils"
                })
            else:
                day_plan["slots"].append({
                    "time": "01:00 PM - 02:00 PM",
                    "period": "Afternoon",
                    "type": "dining",
                    "title": "Local Street Food & Lunch",
                    "description": "Savor authentic regional delicacies at a popular local bazaar dhaba.",
                    "cost": 250.0,
                    "icon": "utensils"
                })

            # ---------------------------------------------------------
            # Afternoon Slot
            # ---------------------------------------------------------
            a_place = afternoon_spots.pop(0) if afternoon_spots else (all_places_pool[place_idx % len(all_places_pool)] if all_places_pool else None)
            if a_place:
                if a_place in all_places_pool:
                    place_idx += 1
                day_plan["day_entry_total"] += a_place.entry_cost
                day_plan["slots"].append({
                    "time": "02:45 PM - 05:00 PM",
                    "period": "Afternoon",
                    "type": "attraction",
                    "title": a_place.name,
                    "description": a_place.description,
                    "category": a_place.category,
                    "rating": a_place.rating,
                    "duration_hours": a_place.visit_duration,
                    "cost": a_place.entry_cost,
                    "icon": "compass"
                })
            else:
                day_plan["slots"].append({
                    "time": "02:30 PM - 04:30 PM",
                    "period": "Afternoon",
                    "type": "leisure",
                    "title": "Heritage Walk & Artisan Market Exploration",
                    "description": f"Explore local handicraft markets, souvenir stalls, and cultural streets in {dest.name}.",
                    "cost": 0.0,
                    "icon": "shopping-bag"
                })

            # ---------------------------------------------------------
            # Evening Slot
            # ---------------------------------------------------------
            e_place = evening_spots.pop(0) if evening_spots else None
            if e_place:
                day_plan["day_entry_total"] += e_place.entry_cost
                day_plan["slots"].append({
                    "time": "05:30 PM - 07:30 PM",
                    "period": "Evening",
                    "type": "attraction",
                    "title": e_place.name,
                    "description": e_place.description,
                    "category": e_place.category,
                    "rating": e_place.rating,
                    "duration_hours": e_place.visit_duration,
                    "cost": e_place.entry_cost,
                    "icon": "sunset"
                })
            else:
                day_plan["slots"].append({
                    "time": "05:30 PM - 07:30 PM",
                    "period": "Evening",
                    "type": "leisure",
                    "title": "Sunset View & Evening Promenade",
                    "description": f"Relax with tea or coffee overlooking sunset vistas across the {dest.name} valley.",
                    "cost": 100.0,
                    "icon": "coffee"
                })

            # ---------------------------------------------------------
            # Dinner Slot
            # ---------------------------------------------------------
            dinner_rest = restaurants[rest_idx % len(restaurants)] if restaurants else None
            rest_idx += 1
            if dinner_rest:
                day_plan["slots"].append({
                    "time": "08:00 PM - 09:45 PM",
                    "period": "Night",
                    "type": "dining",
                    "title": f"Dinner at {dinner_rest.name}",
                    "description": f"Savor delicious {dinner_rest.cuisine} in cozy ambiance. Popular dishes: {dinner_rest.popular_dishes or 'House Specialty'}.",
                    "rating": dinner_rest.rating,
                    "cost": dinner_rest.avg_cost_per_person,
                    "icon": "moon"
                })
            else:
                day_plan["slots"].append({
                    "time": "08:00 PM - 09:30 PM",
                    "period": "Night",
                    "type": "dining",
                    "title": "Relaxing Dinner",
                    "description": "Casual dinner at your hotel or neighboring bistro.",
                    "cost": 350.0,
                    "icon": "moon"
                })

            days_schedule.append(day_plan)

        return {
            "success": True,
            "destination_id": dest.id,
            "destination_name": dest.name,
            "category": dest.category,
            "tagline": dest.tagline,
            "recommended_days": dest.recommended_days,
            "planned_days": duration_days,
            "days": days_schedule,
            "total_estimated_attraction_cost": sum(d["day_entry_total"] for d in days_schedule)
        }
