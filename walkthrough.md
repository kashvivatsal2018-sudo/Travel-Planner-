# Travel Planner Walkthrough: Full-Stack Implementation & Verification

The **Travel Planner using Graph** has been built from scratch as one fully integrated project. The application connects a questionnaire-driven content recommendation engine, a manual weighted graph, Dijkstra's shortest path algorithm, an interactive Leaflet/OpenStreetMap visualizer, a dynamic budget estimator, and an automated day-wise itinerary generator powered by an SQLite database.

---

## 1. Accomplishments & Implemented Modules

### 1.1 Data Structures & Algorithms Core (`graph/`)
- **Weighted Graph (`graph/graph.py`)**: Implemented using an **Adjacency List** representation (`defaultdict(list)`). Manages vertices and bidirectional road edges in $O(1)$ edge addition and $O(\text{deg}(v))$ neighbor traversal.
- **Dijkstra's Algorithm (`graph/dijkstra.py`)**: Implemented manually with a min-heap priority queue (`heapq`) in $O((|V| + |E|) \log |V|)$ time and $O(|V| + |E|)$ space complexity.
  - Generates shortest path, total distance, segment distances, and a step-by-step **Relaxation Trace** for project viva examination.

### 1.2 Recommendation Engine (`recommendation/recommender.py`)
- Multi-criteria content-based scoring ($0 - 100\%$):
  - Interests & Categories Match ($30\%$)
  - Budget Tier Match ($25\%$)
  - Trip Duration Match ($15\%$)
  - Distance & Proximity Match ($10\%$)
  - Companion Type Match ($10\%$)
  - Travel History Bonus / Exploration of adjacent gateway hubs ($10\%$)
- Explains **"Why recommended for you"** for every destination.

### 1.3 Interactive Services (`services/`)
- **`route_service.py`**: Queries the database `RouteEdge` table, constructs the in-memory graph, executes Dijkstra, and enriches nodes with coordinates for Leaflet polyline rendering.
- **`budget_service.py`**: Real-time itemized cost calculation (Transportation, Accommodation, Food, Activities, Buffer) with interactive sliders.
- **`itinerary_service.py`**: Dynamically schedules destination attractions into morning, afternoon, and evening slots and pairs them with authentic local restaurants.

### 1.4 Database & Seed Dataset (`database/` & `data/`)
- SQLite database configured via Flask-SQLAlchemy with 7 models:
  - `User`, `Destination`, `TravelHistory`, `RouteEdge`, `TouristPlace`, `Restaurant`, `Review`
- Loaded with 15 Indian destinations, 58 highway edges (29 bidirectional routes), 45+ attractions, 40+ restaurants, and 45+ sample reviews from `data/seed_data.json`.

### 1.5 Frontend UI & Map Integration (`templates/` & `static/`)
- Responsive CSS theme with cards, rating pills, and viva diagnostic view.
- Leaflet + OpenStreetMap integration displaying route polyline, origin marker (green), destination marker (red), and intermediate waypoints (blue) with no paid API keys.
- Standalone and embedded views for Destinations, Recommendations, Route Visualizer, Itinerary, and User Profile.

---

## 2. Test Verification

All 29 unit, service, and integration tests passed cleanly:

```bash
./venv/bin/pytest -v tests/
```

### Output:
```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- .../venv/bin/python3
rootdir: /Users/shambhavisingh/Desktop/Fit2Lit---Fitness-that-fits-you
collected 29 items                                                             

tests/test_budget.py::test_budget_calculation_structure PASSED           [  3%]
tests/test_budget.py::test_budget_transport_modes PASSED                 [  6%]
tests/test_budget.py::test_budget_hotel_tiers PASSED                     [ 10%]
tests/test_dijkstra.py::test_dijkstra_academic_example PASSED            [ 13%]
tests/test_dijkstra.py::test_dijkstra_alternative_path_optimization PASSED [ 17%]
tests/test_dijkstra.py::test_dijkstra_same_source_and_destination PASSED [ 20%]
tests/test_dijkstra.py::test_dijkstra_unknown_vertex PASSED              [ 24%]
tests/test_dijkstra.py::test_dijkstra_disconnected_graph PASSED          [ 27%]
tests/test_dijkstra.py::test_dijkstra_relaxation_steps_recorded PASSED   [ 31%]
tests/test_e2e_flow.py::test_full_primary_user_journey PASSED            [ 34%]
tests/test_graph.py::test_graph_initialization PASSED                    [ 37%]
tests/test_graph.py::test_add_vertex_and_case_insensitivity PASSED       [ 41%]
tests/test_graph.py::test_add_edge_bidirectional PASSED                  [ 44%]
tests/test_graph.py::test_add_edge_directed PASSED                       [ 48%]
tests/test_graph.py::test_update_existing_edge_weight PASSED             [ 51%]
tests/test_itinerary.py::test_itinerary_generation_days PASSED           [ 55%]
tests/test_itinerary.py::test_itinerary_invalid_destination PASSED       [ 58%]
tests/test_recommendation.py::test_recommendation_interest_alignment PASSED [ 62%]
tests/test_recommendation.py::test_recommendation_visited_deprioritization PASSED [ 65%]
tests/test_recommendation.py::test_recommendation_adjacent_hub_bonus PASSED [ 68%]
tests/test_routes.py::test_home_page PASSED                              [ 72%]
tests/test_routes.py::test_destinations_catalog PASSED                   [ 75%]
tests/test_routes.py::test_destination_detail PASSED                     [ 79%]
tests/test_routes.py::test_destination_not_found PASSED                  [ 82%]
tests/test_routes.py::test_questionnaire_and_recommendation_flow PASSED  [ 86%]
tests/test_routes.py::test_route_planner_view PASSED                     [ 89%]
tests/test_routes.py::test_api_route_calculation PASSED                  [ 93%]
tests/test_routes.py::test_api_budget_calculation PASSED                 [ 96%]
tests/test_routes.py::test_api_generate_itinerary PASSED                 [100%]

============================== 29 passed in 0.35s ==============================
```

---

## 3. End-to-End Primary Flow Verification

The primary user workflow was verified through automated end-to-end tests:
1. **Home Page (`/`)**: Displays hero, stats, featured destinations, and live Dijkstra demo.
2. **Guest Entry (`/guest`)**: Grants instant guest session without forced registration.
3. **Questionnaire (`/plan`)**: Captures visited destinations, interests, budget, duration, companions, and origin.
4. **Recommendation (`/recommendations`)**: Displays ranked destinations with match percentages and "Why recommended" bullets.
5. **Destination Details (`/destination/2`)**: Displays Mussoorie attractions, dining, reviews, interactive budget calculator, and itinerary.
6. **Dijkstra Route Calculation (`/route?source=Dehradun&destination=Dhanaulti`)**:
   - Calculates shortest path: `Dehradun → Mussoorie → Dhanaulti` (95.0 km).
   - Renders Leaflet OpenStreetMap polyline and markers.
   - Shows Dijkstra execution relaxation steps table.
7. **Budget Calculation (`/api/calculate-budget`)**: Real-time breakdown updates per sliders.
8. **Itinerary Generation (`/api/generate-itinerary`)**: Generates day-by-day plan with attractions and restaurant meals.
