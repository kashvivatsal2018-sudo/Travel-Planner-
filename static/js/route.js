/**
 * Route Visualization JavaScript:
 * Integrates Leaflet + OpenStreetMap with manual Python Dijkstra shortest path calculations.
 */

let travelMap = null;
let routePolyline = null;
let routeMarkers = [];

document.addEventListener("DOMContentLoaded", () => {
    const mapElement = document.getElementById("map");
    if (!mapElement) return;

    // Initialize Leaflet Map centered roughly on Northern India
    travelMap = L.map("map").setView([29.5, 77.5], 7);

    // Free OpenStreetMap Tile Layer (Zero API key required!)
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Travel Planner Graph Engine'
    }).addTo(travelMap);

    // Check if initial waypoints are provided in the HTML data attribute
    const waypointsData = mapElement.getAttribute("data-waypoints");
    if (waypointsData) {
        try {
            const waypoints = JSON.parse(waypointsData);
            renderRouteOnMap(waypoints);
        } catch (e) {
            console.error("Error parsing waypoints data:", e);
        }
    }

    // Interactive Route Swap Button
    const swapBtn = document.getElementById("swapCitiesBtn");
    if (swapBtn) {
        swapBtn.addEventListener("click", () => {
            const srcSelect = document.getElementById("sourceCitySelect");
            const dstSelect = document.getElementById("destCitySelect");
            if (srcSelect && dstSelect) {
                const temp = srcSelect.value;
                srcSelect.value = dstSelect.value;
                dstSelect.value = temp;
            }
        });
    }

    // Toggle Viva Diagnostics Trace
    const toggleTraceBtn = document.getElementById("toggleVivaTraceBtn");
    const traceSection = document.getElementById("vivaTraceSection");
    if (toggleTraceBtn && traceSection) {
        toggleTraceBtn.addEventListener("click", () => {
            const isHidden = traceSection.style.display === "none";
            traceSection.style.display = isHidden ? "block" : "none";
            toggleTraceBtn.innerHTML = isHidden
                ? '<i class="fa-solid fa-chevron-up"></i> Hide Dijkstra Execution Trace'
                : '<i class="fa-solid fa-terminal"></i> Show Dijkstra Execution Trace (Viva Examiner View)';
        });
    }
});

/**
 * Render waypoints, markers, and polyline on the Leaflet map.
 */
function renderRouteOnMap(waypoints) {
    if (!travelMap || !waypoints || waypoints.length === 0) return;

    // Clear existing markers and polyline
    routeMarkers.forEach(m => travelMap.removeLayer(m));
    routeMarkers = [];
    if (routePolyline) {
        travelMap.removeLayer(routePolyline);
        routePolyline = null;
    }

    const latLngs = [];

    waypoints.forEach((wp, index) => {
        const lat = wp.latitude;
        const lng = wp.longitude;
        latLngs.push([lat, lng]);

        const isSource = index === 0;
        const isTarget = index === waypoints.length - 1;

        // Custom marker colors
        let markerColor = "#3b82f6"; // Blue for transit
        let markerLabel = `${index + 1}`;
        if (isSource) {
            markerColor = "#10b981"; // Green for source
            markerLabel = "A";
        } else if (isTarget) {
            markerColor = "#ef4444"; // Red for destination
            markerLabel = "B";
        }

        const customIcon = L.divIcon({
            className: "custom-leaflet-marker",
            html: `
                <div style="
                    background: ${markerColor};
                    color: white;
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    border: 3px solid white;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 800;
                    font-size: 13px;
                ">${markerLabel}</div>
            `,
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        });

        const marker = L.marker([lat, lng], { icon: customIcon }).addTo(travelMap);
        
        const popupContent = `
            <div style="font-family: inherit; min-width: 160px; padding: 4px;">
                <h4 style="margin: 0 0 4px; font-weight: 800; color: #0f172a;">${wp.name}</h4>
                <p style="margin: 0 0 6px; font-size: 12px; color: #64748b;">${wp.category || "Waypoint"}</p>
                <div style="font-size: 12px; font-weight: 700; color: ${isSource ? '#10b981' : isTarget ? '#ef4444' : '#2563eb'};">
                    ${isSource ? '🟢 Trip Origin' : isTarget ? '🎯 Target Destination' : `Waypoint #${index + 1}`}
                </div>
            </div>
        `;
        marker.bindPopup(popupContent);
        routeMarkers.push(marker);
    });

    // Draw connecting route polyline
    if (latLngs.length > 1) {
        routePolyline = L.polyline(latLngs, {
            color: "#2563eb",
            weight: 5,
            opacity: 0.85,
            dashArray: "8, 8",
            lineJoin: "round"
        }).addTo(travelMap);

        // Fit map bounds to neatly display entire road route
        travelMap.fitBounds(routePolyline.getBounds(), {
            padding: [60, 60],
            maxZoom: 12
        });
    } else if (latLngs.length === 1) {
        travelMap.setView(latLngs[0], 11);
    }
}
