/**
 * Main Commuter Application Entry Point & Orchestrator
 */

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚦 Smart Transportation Ecosystem Dashboard Initializing...');

    // 1. Initialize Leaflet Map
    if (typeof initMap === 'function') {
        initMap('map');
    }

    // 2. Fetch Live Ecosystem Data
    await Promise.all([
        typeof fetchTrafficData === 'function' ? fetchTrafficData() : null,
        typeof fetchTransportData === 'function' ? fetchTransportData() : null,
        typeof fetchParkingData === 'function' ? fetchParkingData() : null,
        typeof fetchPollutionData === 'function' ? fetchPollutionData() : null,
        fetchIncidents()
    ]);

    // 3. Initialize Journey Planner & Route Recommendation Engine
    if (typeof initRouteModule === 'function') {
        initRouteModule();
    }

    // 4. Setup Map Layer Toggle Buttons
    setupLayerToggles();

    // 5. Setup Incident Reporting Modal
    setupIncidentModal();

    // 6. Optional: Periodic Background Sync every 30 seconds
    setInterval(() => {
        if (typeof fetchTrafficData === 'function') fetchTrafficData();
        if (typeof fetchTransportData === 'function') fetchTransportData();
        if (typeof fetchParkingData === 'function') fetchParkingData();
    }, 30000);
});

async function fetchIncidents() {
    try {
        const res = await fetch('/api/incidents');
        const data = await res.json();
        if (data.status === 'success' && typeof renderIncidentMarkers === 'function') {
            renderIncidentMarkers(data.incidents);
        }
    } catch (e) {
        console.error('Error loading incidents:', e);
    }
}

function setupLayerToggles() {
    const toggleButtons = document.querySelectorAll('.layer-toggle-btn');
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const layerName = btn.getAttribute('data-layer');
            if (layerName && typeof toggleMapLayer === 'function') {
                const isActive = toggleMapLayer(layerName);
                btn.classList.toggle('active', isActive);
            }
        });
    });
}

function setupIncidentModal() {
    const modal = document.getElementById('incident-modal');
    const openBtn = document.getElementById('btn-open-incident-modal');
    const closeBtn = document.getElementById('btn-close-incident-modal');
    const form = document.getElementById('incident-report-form');

    if (openBtn && modal) {
        openBtn.addEventListener('click', () => {
            modal.classList.add('active');
        });
    }

    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => {
            modal.classList.remove('active');
        });
    }

    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.remove('active');
        });
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const type = document.getElementById('inc-type').value;
            const location = document.getElementById('inc-location').value;
            const description = document.getElementById('inc-desc').value;
            const severity = document.getElementById('inc-severity').value;

            try {
                const res = await fetch('/api/incidents', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        type: type,
                        location: location,
                        description: description,
                        severity: severity,
                        latitude: 12.9250 + (Math.random() * 0.08),
                        longitude: 80.1700 + (Math.random() * 0.08)
                    })
                });

                const data = await res.json();
                if (data.status === 'success') {
                    alert('✅ Incident reported successfully! It is now broadcast to transit monitoring.');
                    modal.classList.remove('active');
                    form.reset();
                    fetchIncidents();
                }
            } catch (err) {
                alert('Failed to submit incident report');
            }
        });
    }
}
