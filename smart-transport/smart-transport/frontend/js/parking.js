/**
 * Smart Parking Module Controller
 */

async function fetchParkingData() {
    try {
        const res = await fetch('/api/parking');
        const data = await res.json();
        if (data.status === 'success') {
            updateParkingUI(data);
            if (typeof renderParkingMarkers === 'function') {
                renderParkingMarkers(data.parking);
            }
            return data;
        }
    } catch (err) {
        console.error('Error loading parking data:', err);
    }
    return null;
}

function updateParkingUI(data) {
    const parkingStatEl = document.getElementById('stat-parking');
    if (parkingStatEl) {
        parkingStatEl.textContent = `${data.total_available_spots}`;
    }

    const parkingBadgeEl = document.getElementById('stat-parking-badge');
    if (parkingBadgeEl) {
        parkingBadgeEl.textContent = `${data.overall_availability_rate}% Available`;
        parkingBadgeEl.className = data.overall_availability_rate < 25 ? 'stat-badge badge-severe' : 'stat-badge badge-good';
    }

    const listContainer = document.getElementById('parking-lots-list');
    if (listContainer && data.parking) {
        listContainer.innerHTML = data.parking.slice(0, 5).map(p => {
            const isFull = p.available <= 15;
            return `
                <div style="display:flex; justify-content:space-between; align-items:center; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color); font-size: 0.84rem;">
                    <div>
                        <div style="font-weight:600; color:#fff;">${p.name}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted);">${p.area} • ₹${p.price}/hr ${p.has_ev_charging ? '• ⚡ EV' : ''}</div>
                    </div>
                    <div>
                        <span class="stat-badge ${isFull ? 'badge-high' : 'badge-good'}">${p.available} Free</span>
                    </div>
                </div>
            `;
        }).join('');
    }
}
