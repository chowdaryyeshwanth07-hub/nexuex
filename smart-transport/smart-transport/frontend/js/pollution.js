/**
 * Pollution (Air Quality) Module Controller
 */

async function fetchPollutionData() {
    try {
        const res = await fetch('/api/pollution');
        const data = await res.json();
        if (data.status === 'success') {
            updatePollutionUI(data);
            if (typeof renderPollutionMarkers === 'function') {
                renderPollutionMarkers(data.stations);
            }
            return data;
        }
    } catch (err) {
        console.error('Error loading air quality data:', err);
    }
    return null;
}

function updatePollutionUI(data) {
    const aqiStatEl = document.getElementById('stat-aqi');
    if (aqiStatEl) {
        aqiStatEl.textContent = `${data.average_aqi}`;
    }

    const aqiBadgeEl = document.getElementById('stat-aqi-badge');
    if (aqiBadgeEl) {
        aqiBadgeEl.textContent = `${data.average_status}`;
        if (data.average_aqi <= 50) aqiBadgeEl.className = 'stat-badge badge-good';
        else if (data.average_aqi <= 100) aqiBadgeEl.className = 'stat-badge badge-moderate';
        else if (data.average_aqi <= 150) aqiBadgeEl.className = 'stat-badge badge-high';
        else aqiBadgeEl.className = 'stat-badge badge-severe';
    }

    const listContainer = document.getElementById('pollution-stations-list');
    if (listContainer && data.stations) {
        listContainer.innerHTML = data.stations.slice(0, 5).map(s => {
            let badgeClass = 'badge-good';
            if (s.aqi > 200) badgeClass = 'badge-severe';
            else if (s.aqi > 150) badgeClass = 'badge-high';
            else if (s.aqi > 100) badgeClass = 'badge-moderate';

            return `
                <div style="display:flex; justify-content:space-between; align-items:center; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color); font-size: 0.84rem;">
                    <div>
                        <div style="font-weight:600; color:#fff;">${s.location.split('(')[0].trim()}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted);">PM2.5: ${s.pm25} µg/m³ • PM10: ${s.pm10}</div>
                    </div>
                    <div>
                        <span class="stat-badge ${badgeClass}">AQI ${s.aqi}</span>
                    </div>
                </div>
            `;
        }).join('');
    }
}
