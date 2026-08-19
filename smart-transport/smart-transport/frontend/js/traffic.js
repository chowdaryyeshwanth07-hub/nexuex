/**
 * Traffic Module Controller
 */

async function fetchTrafficData() {
    try {
        const res = await fetch('/api/traffic');
        const data = await res.json();
        if (data.status === 'success') {
            updateTrafficUI(data);
            if (typeof renderTrafficPolylines === 'function') {
                renderTrafficPolylines(data.roads);
            }
            return data;
        }
    } catch (err) {
        console.error('Error loading traffic data:', err);
    }
    return null;
}

function updateTrafficUI(data) {
    // Update live banner stat
    const trafficStatEl = document.getElementById('stat-traffic');
    if (trafficStatEl) {
        trafficStatEl.textContent = `${data.average_congestion}%`;
    }

    const trafficBadgeEl = document.getElementById('stat-traffic-badge');
    if (trafficBadgeEl) {
        if (data.average_congestion >= 80) {
            trafficBadgeEl.textContent = 'Severe Traffic';
            trafficBadgeEl.className = 'stat-badge badge-severe';
        } else if (data.average_congestion >= 60) {
            trafficBadgeEl.textContent = 'High Congestion';
            trafficBadgeEl.className = 'stat-badge badge-high';
        } else if (data.average_congestion >= 30) {
            trafficBadgeEl.textContent = 'Moderate Traffic';
            trafficBadgeEl.className = 'stat-badge badge-moderate';
        } else {
            trafficBadgeEl.textContent = 'Smooth Flow';
            trafficBadgeEl.className = 'stat-badge badge-low';
        }
    }

    // Populate Traffic Monitor list in sidebar if container exists
    const listContainer = document.getElementById('traffic-roads-list');
    if (listContainer && data.roads) {
        listContainer.innerHTML = data.roads.map(r => {
            let badgeClass = 'badge-low';
            if (r.congestion >= 80) badgeClass = 'badge-severe';
            else if (r.congestion >= 60) badgeClass = 'badge-high';
            else if (r.congestion >= 30) badgeClass = 'badge-moderate';

            return `
                <div style="display:flex; justify-content:space-between; align-items:center; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color); font-size: 0.84rem;">
                    <div>
                        <div style="font-weight:600; color:#fff;">${r.road.split('(')[0].trim()}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted);">${r.avg_speed_kmh} km/h</div>
                    </div>
                    <div style="text-align:right;">
                        <span class="stat-badge ${badgeClass}">${r.congestion}% ${r.status}</span>
                    </div>
                </div>
            `;
        }).join('');
    }
}
