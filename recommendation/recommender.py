"""
Transparent Content-Based Recommendation Engine for Travel Destinations.

Academic & Viva Concepts:
-------------------------
Why Content-Based Recommendation?
- Cold-Start Problem: Works effectively without requiring millions of historical user ratings.
- Transparency / Explainability: The model can explicitly justify WHY a destination is recommended
  based on transparent attribute matches (Interests, Budget, Duration, Companions, Distance, and Travel History).
- Multi-Criteria Decision Analysis (MCDA): Uses normalized weighted scoring across heterogeneous attributes.

Scoring Formula:
----------------
Total Score (0 - 100) =
      W_interest * Score_interest (30%)
    + W_budget   * Score_budget   (25%)
    + W_duration * Score_duration (15%)
    + W_distance * Score_distance (10%)
    + W_companion* Score_companion(10%)
    + W_history  * Score_history  (10%)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from graph.graph import WeightedGraph


@dataclass
class RecommendationResult:
    """Individual destination recommendation with transparent scoring breakdown."""
    destination_id: int
    name: str
    category: str
    all_categories: List[str]
    rating: float
    avg_cost_min: int
    avg_cost_max: int
    recommended_days: int
    image_url: str
    tagline: str
    best_time: str
    final_score: float  # 0 to 100%
    score_breakdown: Dict[str, float]
    reasons: List[str]
    is_previously_visited: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "destination_id": self.destination_id,
            "name": self.name,
            "category": self.category,
            "all_categories": self.all_categories,
            "rating": self.rating,
            "avg_cost_min": self.avg_cost_min,
            "avg_cost_max": self.avg_cost_max,
            "recommended_days": self.recommended_days,
            "image_url": self.image_url,
            "tagline": self.tagline,
            "best_time": self.best_time,
            "final_score": round(self.final_score, 1),
            "score_breakdown": self.score_breakdown,
            "reasons": self.reasons,
            "is_previously_visited": self.is_previously_visited
        }


class RecommendationEngine:
    """Multi-factor content-based destination recommendation engine."""

    # Budget range boundaries in INR
    BUDGET_RANGES = {
        "under_3000": (0, 3000),
        "3000_5000": (3000, 5000),
        "5000_10000": (5000, 10000),
        "10000_20000": (10000, 20000),
        "above_20000": (20000, 100000)
    }

    # Trip duration values in days
    DURATION_VALUES = {
        "1_day": 1.0,
        "2_3_days": 2.5,
        "4_5_days": 4.5,
        "6_7_days": 6.5,
        "above_7_days": 8.0
    }

    def __init__(self, graph: Optional[WeightedGraph] = None):
        self.graph = graph

    def recommend(
        self,
        destinations: List[Any],
        preferred_categories: List[str],
        budget_key: str,
        duration_key: str,
        travel_companion: str,
        visited_destinations: List[str],
        preferred_distance: str = "any",
        current_city: Optional[str] = None,
        top_k: int = 6
    ) -> List[RecommendationResult]:
        """
        Rank all available destinations for a user profile and return top_k recommendations.
        """
        results: List[RecommendationResult] = []

        norm_visited = {v.strip().lower() for v in visited_destinations if v}
        norm_prefs = [c.strip().lower() for c in preferred_categories if c]
        budget_bounds = self.BUDGET_RANGES.get(budget_key, (3000, 10000))
        target_days = self.DURATION_VALUES.get(duration_key, 2.5)

        for dest in destinations:
            d_name = dest.name
            d_name_norm = d_name.lower()
            is_visited = d_name_norm in norm_visited

            score_breakdown = {}
            reasons = []

            # -------------------------------------------------------------
            # Factor 1: Interest / Category Match (Weight: 30)
            # -------------------------------------------------------------
            all_cats = [c.lower() for c in dest.get_all_categories()]
            matched_interests = [c for c in norm_prefs if any(c in d_cat or d_cat in c for d_cat in all_cats)]

            if matched_interests:
                # Primary category match gets 20 pts, each extra gets 5 pts up to 30
                primary_match = any(p in dest.category.lower() or dest.category.lower() in p for p in norm_prefs)
                interest_score = 20.0 if primary_match else 15.0
                extra_matches = len(matched_interests) - 1
                interest_score = min(30.0, interest_score + max(0, extra_matches) * 5.0)
                reasons.append(f"Matches your passion for {', '.join([c.capitalize() for c in matched_interests[:2]])}")
            else:
                interest_score = 6.0  # baseline interest score

            score_breakdown["interests"] = round(interest_score, 1)

            # -------------------------------------------------------------
            # Factor 2: Budget Compatibility (Weight: 25)
            # -------------------------------------------------------------
            u_min, u_max = budget_bounds
            d_min, d_max = dest.avg_cost_min, dest.avg_cost_max

            # Check overlap between [u_min, u_max] and [d_min, d_max]
            overlap_min = max(u_min, d_min)
            overlap_max = min(u_max, d_max)

            if overlap_max >= overlap_min:
                budget_score = 25.0
                reasons.append(f"Fits comfortably in your ₹{u_min:,} - ₹{u_max:,} budget range")
            else:
                # Calculate normalized distance to user's budget range
                if d_min > u_max:
                    diff = d_min - u_max
                else:
                    diff = u_min - d_max
                # Graded decay
                if diff <= 2500:
                    budget_score = 16.0
                    reasons.append("Slightly outside preferred budget tier, but great value")
                elif diff <= 5000:
                    budget_score = 10.0
                else:
                    budget_score = 4.0

            score_breakdown["budget"] = round(budget_score, 1)

            # -------------------------------------------------------------
            # Factor 3: Trip Duration Compatibility (Weight: 15)
            # -------------------------------------------------------------
            day_diff = abs(dest.recommended_days - target_days)
            if day_diff <= 0.8:
                duration_score = 15.0
                reasons.append(f"Ideal for a {dest.recommended_days}-day itinerary")
            elif day_diff <= 1.8:
                duration_score = 11.0
            else:
                duration_score = 6.0

            score_breakdown["duration"] = round(duration_score, 1)

            # -------------------------------------------------------------
            # Factor 4: Companion Type Compatibility (Weight: 10)
            # -------------------------------------------------------------
            suitable_companions = [c.lower() for c in dest.get_suitable_companions()]
            companion_norm = (travel_companion or "Friends").lower()

            if any(companion_norm in c for c in suitable_companions):
                companion_score = 10.0
                reasons.append(f"Highly recommended for travel with {travel_companion.capitalize()}")
            else:
                companion_score = 4.0

            score_breakdown["companion"] = round(companion_score, 1)

            # -------------------------------------------------------------
            # Factor 5: Distance & Hub Proximity (Weight: 10)
            # -------------------------------------------------------------
            distance_score = 8.0
            if self.graph and (current_city or visited_destinations):
                base_ref = current_city or (visited_destinations[0] if visited_destinations else None)
                if base_ref and self.graph.has_vertex(base_ref) and self.graph.has_vertex(d_name):
                    # Check direct neighbor or edge distance
                    direct_dist = self.graph.get_edge_weight(base_ref, d_name)
                    if direct_dist is not None:
                        if preferred_distance == "within_100" and direct_dist <= 100:
                            distance_score = 10.0
                            reasons.append(f"Close to {base_ref} ({int(direct_dist)} km direct drive)")
                        elif preferred_distance == "within_300" and direct_dist <= 300:
                            distance_score = 10.0
                            reasons.append(f"Convenient road connection from {base_ref} ({int(direct_dist)} km)")
                        else:
                            distance_score = 9.0
                    else:
                        distance_score = 7.0
            elif preferred_distance == "any":
                distance_score = 9.0

            score_breakdown["distance"] = round(distance_score, 1)

            # -------------------------------------------------------------
            # Factor 6: Travel History Relevance & Hub Exploration (Weight: 10)
            # -------------------------------------------------------------
            history_score = 7.0
            if is_visited:
                # If already visited, deprioritize so user discovers new places
                history_score = 2.0
            else:
                # Check if destination is adjacent to ANY previously visited city in the graph
                if self.graph and visited_destinations:
                    adjacent_to_visited = False
                    adj_city = ""
                    for v_city in visited_destinations:
                        if self.graph.has_vertex(v_city) and self.graph.has_vertex(d_name):
                            w = self.graph.get_edge_weight(v_city, d_name)
                            if w is not None:
                                adjacent_to_visited = True
                                adj_city = v_city
                                break
                    if adjacent_to_visited:
                        history_score = 10.0
                        reasons.insert(1, f"Exciting new destination adjacent to your visited city {adj_city}")
                    else:
                        history_score = 7.0

            score_breakdown["history"] = round(history_score, 1)

            # -------------------------------------------------------------
            # Quality & Rating Modifier (Subtle bonus up to 5 pts)
            # -------------------------------------------------------------
            rating_bonus = max(0.0, (dest.rating - 4.0) * 5.0)
            score_breakdown["rating_quality"] = round(rating_bonus, 1)

            # Final aggregated score (normalized out of 100)
            raw_total = sum(score_breakdown.values())
            # Cap at 99.0 max for realism
            final_score = min(98.5, max(25.0, raw_total))

            if dest.rating >= 4.6 and not any("rating" in r.lower() for r in reasons):
                reasons.append(f"Top-rated destination with ⭐ {dest.rating}/5 user rating")

            results.append(
                RecommendationResult(
                    destination_id=dest.id,
                    name=dest.name,
                    category=dest.category,
                    all_categories=dest.get_all_categories(),
                    rating=dest.rating,
                    avg_cost_min=dest.avg_cost_min,
                    avg_cost_max=dest.avg_cost_max,
                    recommended_days=dest.recommended_days,
                    image_url=dest.image_url or "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800",
                    tagline=dest.tagline or "",
                    best_time=dest.best_time,
                    final_score=final_score,
                    score_breakdown=score_breakdown,
                    reasons=reasons[:5],
                    is_previously_visited=is_visited
                )
            )

        # Sort descending by final score
        results.sort(key=lambda r: r.final_score, reverse=True)
        return results[:top_k]
