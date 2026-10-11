/**
 * Dynamic Budget Calculator JavaScript:
 * Handles live parameter adjustments and calls the backend BudgetService API.
 */

document.addEventListener("DOMContentLoaded", () => {
    const budgetForm = document.getElementById("budgetCalculatorForm");
    if (!budgetForm) return;

    const travelersInput = document.getElementById("budgetTravelersInput");
    const daysInput = document.getElementById("budgetDaysInput");
    const transportSelect = document.getElementById("budgetTransportSelect");
    const hotelTierRadios = document.querySelectorAll("input[name='hotel_tier']");
    const foodTierRadios = document.querySelectorAll("input[name='food_tier']");
    const destIdInput = document.getElementById("budgetDestinationId");
    const distanceInput = document.getElementById("budgetDistanceInput");

    // Output elements
    const totalDisplay = document.getElementById("budgetTotalDisplay");
    const perPersonDisplay = document.getElementById("budgetPerPersonDisplay");
    const costTransport = document.getElementById("costTransportDisplay");
    const costHotel = document.getElementById("costHotelDisplay");
    const costFood = document.getElementById("costFoodDisplay");
    const costActivities = document.getElementById("costActivitiesDisplay");
    const costMisc = document.getElementById("costMiscDisplay");

    const barTransport = document.getElementById("barTransport");
    const barHotel = document.getElementById("barHotel");
    const barFood = document.getElementById("barFood");
    const barActivities = document.getElementById("barActivities");
    const barMisc = document.getElementById("barMisc");

    const fetchBudgetEstimate = async () => {
        const travelers = parseInt(travelersInput?.value || 2);
        const days = parseInt(daysInput?.value || 3);
        const transport = transportSelect?.value || "train";
        const hotelTier = document.querySelector("input[name='hotel_tier']:checked")?.value || "standard";
        const foodTier = document.querySelector("input[name='food_tier']:checked")?.value || "moderate";
        const destinationId = destIdInput ? parseInt(destIdInput.value) : null;
        const distanceKm = distanceInput ? parseFloat(distanceInput.value) : 250.0;

        try {
            const response = await fetch("/api/calculate-budget", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    travelers: travelers,
                    days: days,
                    transport_mode: transport,
                    hotel_tier: hotelTier,
                    food_tier: foodTier,
                    destination_id: destinationId,
                    distance_km: distanceKm
                })
            });

            if (!response.ok) throw new Error("Calculation failed");
            const data = await response.json();
            const b = data.budget;

            if (totalDisplay) totalDisplay.textContent = `₹${b.total_estimated_budget.toLocaleString("en-IN")}`;
            if (perPersonDisplay) perPersonDisplay.textContent = `₹${b.cost_per_person.toLocaleString("en-IN")} / traveler`;

            if (costTransport) costTransport.textContent = `₹${b.breakdown.transportation.toLocaleString("en-IN")}`;
            if (costHotel) costHotel.textContent = `₹${b.breakdown.accommodation.toLocaleString("en-IN")}`;
            if (costFood) costFood.textContent = `₹${b.breakdown.food.toLocaleString("en-IN")}`;
            if (costActivities) costActivities.textContent = `₹${b.breakdown.activities.toLocaleString("en-IN")}`;
            if (costMisc) costMisc.textContent = `₹${b.breakdown.miscellaneous.toLocaleString("en-IN")}`;

            if (barTransport) barTransport.style.width = `${b.percentages.transportation}%`;
            if (barHotel) barHotel.style.width = `${b.percentages.accommodation}%`;
            if (barFood) barFood.style.width = `${b.percentages.food}%`;
            if (barActivities) barActivities.style.width = `${b.percentages.activities}%`;
            if (barMisc) barMisc.style.width = `${b.percentages.miscellaneous}%`;

        } catch (err) {
            console.error("Budget estimation error:", err);
        }
    };

    // Attach listeners
    [travelersInput, daysInput, transportSelect, distanceInput].forEach(elem => {
        if (elem) {
            elem.addEventListener("input", fetchBudgetEstimate);
            elem.addEventListener("change", fetchBudgetEstimate);
        }
    });

    hotelTierRadios.forEach(radio => radio.addEventListener("change", fetchBudgetEstimate));
    foodTierRadios.forEach(radio => radio.addEventListener("change", fetchBudgetEstimate));
});
