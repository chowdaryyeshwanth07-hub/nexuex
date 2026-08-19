/**
 * Interactive Leaflet.js Map Controller
 */

let mapInstance = null;
let layerGroups = {
    traffic: null,
    buses: null,
    parking: null,
    pollution: null,
    incidents: null,
    route: null
};

// Custom SVG icon generator for map pins
function createCustomIcon(iconChar, bgColor, size = 34) {
    return L.divIcon({
        className: 'custom-leaflet-pin',
        html: `<div class="custom-map-icon" style="background: ${bgColor}; width: ${size}px; height: ${size}px; border: 2px solid #fff; color: #fff;">${iconChar}</div>`,
        iconSize: [size, size],
        iconAnchor: [size / 2, size / 2],
        popupAnchor: [0, -size / 2]
    });
}

function initMap(elementId = 'map') {
    const el = document.getElementById(elementId);
    if (!el) return null;

    // Center on Chennai Metropolitan Region (between Tambaram and Central)
    const initialLat = 12.9650;
    const initialLng = 80.1850;

    mapInstance = L.map(elementId, {
        center: [initialLat, initialLng],
        zoom: 11,
        zoomControl: true
    });

    // Dark-themed OpenStreetMap tiles (CartoDB Dark Matter)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        maxZoom: 19
    }).addTo(mapInstance);

    // Initialize feature layer groups
    layerGroups.traffic = L.layerGroup().addTo(mapInstance);
    layerGroups.buses = L.layerGroup().addTo(mapInstance);
    layerGroups.parking = L.layerGroup().addTo(mapInstance);
    layerGroups.pollution = L.layerGroup().addTo(mapInstance);
    layerGroups.incidents = L.layerGroup().addTo(mapInstance);
    layerGroups.route = L.layerGroup().addTo(mapInstance);

    return mapInstance;
}

function toggleMapLayer(layerName) {
    if (!mapInstance || !layerGroups[layerName]) return false;
    
    if (mapInstance.hasLayer(layerGroups[layerName])) {
        mapInstance.removeLayer(layerGroups[layerName]);
        return false;
    } else {
        mapInstance.addLayer(layerGroups[layerName]);
        return true;
    }
}

// Render Bus markers
function renderBusMarkers(buses) {
    if (!layerGroups.buses) return;
    layerGroups.buses.clearLayers();

    buses.forEach(b => {
        const icon = createCustomIcon('🚌', '#3b82f6', 32);
        const marker = L.marker([b.current_lat, b.current_lng], { icon: icon });

        const popupContent = `
            <div style="font-family: inherit; min-width: 170px;">
                <div style="font-weight: 700; font-size: 1rem; color: #60a5fa; margin-bottom: 4px;">🚌 Bus ${b.bus}</div>
                <div style="font-size: 0.82rem; color: #cbd5e1; margin-bottom: 2px;"><strong>Route:</strong> ${b.route_name}</div>
                <div style="font-size: 0.82rem; color: #cbd5e1; margin-bottom: 2px;"><strong>Dest:</strong> ${b.destination}</div>
                <div style="font-size: 0.82rem; color: #cbd5e1; margin-bottom: 4px;"><strong>ETA:</strong> ${b.eta} mins</div>
                <div style="font-size: 0.75rem; padding: 2px 6px; border-radius: 4px; display: inline-block; background: ${b.occupancy > 75 ? '#ef4444' : '#10b981'}; color: #fff;">
                    Occupancy: ${b.occupancy}% (${b.status})
                </div>
            </div>
        `;
        marker.bindPopup(popupContent);
        layerGroups.buses.addLayer(marker);
    });
}

// Render Parking markers
function renderParkingMarkers(parkingLots) {
    if (!layerGroups.parking) return;
    layerGroups.parking.clearLayers();

    parkingLots.forEach(p => {
        const icon = createCustomIcon('🅿️', '#06b6d4', 30);
        const marker = L.marker([p.latitude, p.longitude], { icon: icon });

        const popupContent = `
            <div style="font-family: inherit; min-width: 180px;">
                <div style="font-weight: 700; font-size: 0.95rem; color: #22d3ee; margin-bottom: 4px;">🅿️ ${p.name}</div>
                <div style="font-size: 0.82rem; color: #cbd5e1;"><strong>Available:</strong> <span style="color: #34d399; font-weight:700;">${p.available}</span> / ${p.total} spots</div>
                <div style="font-size: 0.82rem; color: #cbd5e1;"><strong>Tariff:</strong> ₹${p.price}/hour</div>
                <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 4px;">${p.has_ev_charging ? '⚡ EV Charging Available' : 'No EV points'}</div>
            </div>
        `;
        marker.bindPopup(popupContent);
        layerGroups.parking.addLayer(marker);
    });
}

// Render Pollution (AQI) station circles
function renderPollutionMarkers(stations) {
    if (!layerGroups.pollution) return;
    layerGroups.pollution.clearLayers();

    stations.forEach(s => {
        const circle = L.circle([s.latitude, s.longitude], {
            color: s.color || '#f59e0b',
            fillColor: s.color || '#f59e0b',
            fillOpacity: 0.35,
            radius: 1200
        });

        const popupContent = `
            <div style="font-family: inherit; min-width: 170px;">
                <div style="font-weight: 700; font-size: 0.95rem; color: #fff; margin-bottom: 4px;">🌫️ ${s.location}</div>
                <div style="font-size: 0.85rem; font-weight: 700; color: ${s.color || '#f59e0b'};">AQI: ${s.aqi} (${s.status})</div>
                <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 4px;">PM2.5: ${s.pm25} µg/m³</div>
                <div style="font-size: 0.8rem; color: #cbd5e1;">PM10: ${s.pm10} µg/m³</div>
            </div>
        `;
        circle.bindPopup(popupContent);
        layerGroups.pollution.addLayer(circle);
    });
}

// Render Incidents
function renderIncidentMarkers(incidents) {
    if (!layerGroups.incidents) return;
    layerGroups.incidents.clearLayers();

    incidents.forEach(inc => {
        if (inc.status === 'Resolved') return; // only active/in-progress on map

        const icon = createCustomIcon('⚠️', '#f43f5e', 32);
        const marker = L.marker([inc.latitude, inc.longitude], { icon: icon });

        const popupContent = `
            <div style="font-family: inherit; min-width: 180px;">
                <div style="font-weight: 700; font-size: 0.95rem; color: #fb7171; margin-bottom: 4px;">🚨 ${inc.type}</div>
                <div style="font-size: 0.82rem; color: #cbd5e1;"><strong>Location:</strong> ${inc.road_name || inc.location}</div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin: 4px 0;">${inc.description}</div>
                <div style="font-size: 0.75rem; color: #f87171; font-weight: 600;">Status: ${inc.status}</div>
            </div>
        `;
        marker.bindPopup(popupContent);
        layerGroups.incidents.addLayer(marker);
    });
}

// Render Traffic Corridor Lines
function renderTrafficPolylines(roads) {
    if (!layerGroups.traffic) return;
    layerGroups.traffic.clearLayers();

    roads.forEach(r => {
        let color = '#10b981';
        if (r.congestion >= 80) color = '#ef4444';
        else if (r.congestion >= 60) color = '#f97316';
        else if (r.congestion >= 30) color = '#f59e0b';

        const polyline = L.polyline([
            [r.start_lat, r.start_lng],
            [r.end_lat, r.end_lng]
        ], {
            color: color,
            weight: 6,
            opacity: 0.8
        });

        polyline.bindPopup(`
            <div style="font-family: inherit; min-width: 170px;">
                <div style="font-weight: 700; font-size: 0.95rem; color: ${color};">🚦 ${r.road}</div>
                <div style="font-size: 0.82rem; color: #cbd5e1; margin-top: 4px;"><strong>Congestion:</strong> ${r.congestion}% (${r.status})</div>
                <div style="font-size: 0.82rem; color: #cbd5e1;"><strong>Avg Speed:</strong> ${r.avg_speed_kmh} km/h</div>
                <div style="font-size: 0.82rem; color: #94a3b8;"><strong>Length:</strong> ${r.length_km} km</div>
            </div>
        `);
        layerGroups.traffic.addLayer(polyline);
    });
}

// Draw Selected Recommended Route
function drawRecommendedRoute(originCoords, destCoords, polylinePoints, modeName) {
    if (!layerGroups.route) return;
    layerGroups.route.clearLayers();

    // Origin Marker (Green Pin)
    const originIcon = createCustomIcon('📍', '#10b981', 36);
    const originMarker = L.marker([originCoords.lat, originCoords.lng], { icon: originIcon })
        .bindPopup(`<strong>Origin:</strong> Start of Journey`);
    layerGroups.route.addLayer(originMarker);

    // Destination Marker (Red Flag)
    const destIcon = createCustomIcon('🏁', '#ef4444', 36);
    const destMarker = L.marker([destCoords.lat, destCoords.lng], { icon: destIcon })
        .bindPopup(`<strong>Destination:</strong> End of Journey`);
    layerGroups.route.addLayer(destMarker);

    // Polyline Route Path
    if (polylinePoints && polylinePoints.length > 0) {
        const routeLine = L.polyline(polylinePoints, {
            color: '#3b82f6',
            weight: 7,
            opacity: 0.9,
            dashArray: modeName && modeName.includes('Metro') ? '8, 8' : null
        });
        layerGroups.route.addLayer(routeLine);

        // Fit map bounds to encompass the route
        mapInstance.fitBounds(routeLine.getBounds(), { padding: [40, 40] });
    }
}
