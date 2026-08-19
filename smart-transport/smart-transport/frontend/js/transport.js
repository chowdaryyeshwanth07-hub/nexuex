/**
 * Transport (Bus & Metro) Module Controller
 */

async function fetchTransportData() {
    try {
        const res = await fetch('/api/buses');
        const data = await res.json();
        if (data.status === 'success') {
            updateTransportUI(data);
            if (typeof renderBusMarkers === 'function') {
                renderBusMarkers(data.buses);
            }
            return data;
        }
    } catch (err) {
        console.error('Error loading transit data:', err);
    }
    return null;
}

function updateTransportUI(data) {
    const busStatEl = document.getElementById('stat-buses');
    if (busStatEl) {
        busStatEl.textContent = `${data.active_fleet_count}`;
    }

    const busBadgeEl = document.getElementById('stat-buses-badge');
    if (busBadgeEl) {
        busBadgeEl.textContent = `Avg Occ: ${data.average_occupancy}%`;
        busBadgeEl.className = data.average_occupancy > 75 ? 'stat-badge badge-high' : 'stat-badge badge-good';
    }

    const listContainer = document.getElementById('bus-fleet-list');
    if (listContainer && data.buses) {
        listContainer.innerHTML = data.buses.slice(0, 5).map(b => {
            const isCrowded = b.occupancy > 75;
            return `
                <div style="display:flex; justify-content:space-between; align-items:center; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color); font-size: 0.84rem;">
                    <div>
                        <div style="font-weight:700; color:#60a5fa;">Bus ${b.bus} &rarr; ${b.destination}</div>
                        <div style="font-size:0.75rem; color:var(--text-secondary);">ETA: ${b.eta} mins</div>
                    </div>
                    <div>
                        <span class="stat-badge ${isCrowded ? 'badge-high' : 'badge-good'}">${b.occupancy}% Occupancy</span>
                    </div>
                </div>
            `;
        }).join('');
    }
}
