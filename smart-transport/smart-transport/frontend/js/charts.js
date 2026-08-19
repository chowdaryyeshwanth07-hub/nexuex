/**
 * Admin Dashboard Charts & Analytics Controller
 */

let chartInstances = {};

async function initAdminDashboard() {
    await fetchAdminStats();
    await fetchAndRenderCharts();
    setupSimulator();
    setupIncidentTable();
}

async function fetchAdminStats() {
    try {
        const res = await fetch('/api/admin/statistics');
        const data = await res.json();
        if (data.status === 'success') {
            const ov = data.overview;
            document.getElementById('adm-active-buses').textContent = ov.active_buses;
            document.getElementById('adm-incidents').textContent = ov.active_incidents;
            document.getElementById('adm-parking-avail').textContent = `${ov.parking_availability_percent}%`;
            document.getElementById('adm-avg-aqi').textContent = ov.average_aqi;
            document.getElementById('adm-co2-saved').textContent = `${ov.total_co2_saved_kg} kg`;
            document.getElementById('adm-active-users').textContent = ov.active_users;
        }
    } catch (e) {
        console.error('Error fetching admin statistics:', e);
    }
}

async function fetchAndRenderCharts() {
    try {
        const res = await fetch('/api/admin/charts-data');
        const data = await res.json();
        if (data.status === 'success') {
            renderTrafficChart(data.traffic_chart);
            renderAqiChart(data.aqi_chart);
            renderTrendChart(data.hourly_trend_chart);
            renderIncidentChart(data.incident_chart);
            renderModalShareChart(data.modal_share_chart);
        }
    } catch (e) {
        console.error('Error loading chart data:', e);
    }
}

function renderTrafficChart(chartData) {
    const ctx = document.getElementById('chart-traffic');
    if (!ctx) return;

    if (chartInstances.traffic) chartInstances.traffic.destroy();

    chartInstances.traffic = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Congestion Level (%)',
                data: chartData.data,
                backgroundColor: chartData.colors,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { size: 10 } }
                }
            }
        }
    });
}

function renderAqiChart(chartData) {
    const ctx = document.getElementById('chart-aqi');
    if (!ctx) return;

    if (chartInstances.aqi) chartInstances.aqi.destroy();

    chartInstances.aqi = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Air Quality Index (AQI)',
                data: chartData.data,
                backgroundColor: '#f59e0b',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 220,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { size: 10 } }
                }
            }
        }
    });
}

function renderTrendChart(chartData) {
    const ctx = document.getElementById('chart-trend');
    if (!ctx) return;

    if (chartInstances.trend) chartInstances.trend.destroy();

    chartInstances.trend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Actual Congestion (%)',
                    data: chartData.actual,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'AI Model Forecast (RandomForest)',
                    data: chartData.predicted,
                    borderColor: '#10b981',
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#f8fafc' } }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

function renderIncidentChart(chartData) {
    const ctx = document.getElementById('chart-incidents');
    if (!ctx) return;

    if (chartInstances.incidents) chartInstances.incidents.destroy();

    chartInstances.incidents = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: ['#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#3b82f6']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#f8fafc', boxWidth: 12 } }
            }
        }
    });
}

function renderModalShareChart(chartData) {
    const ctx = document.getElementById('chart-modal');
    if (!ctx) return;

    if (chartInstances.modal) chartInstances.modal.destroy();

    chartInstances.modal = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: ['#10b981', '#3b82f6', '#06b6d4', '#ef4444', '#f59e0b']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#f8fafc', boxWidth: 12 } }
            }
        }
    });
}

async function setupSimulator() {
    const simForm = document.getElementById('traffic-simulator-form');
    if (!simForm) return;

    // Fetch road options
    try {
        const res = await fetch('/api/traffic');
        const data = await res.json();
        const select = document.getElementById('sim-road-select');
        if (select && data.roads) {
            select.innerHTML = data.roads.map(r => `<option value="${r.id}">${r.road} (Currently ${r.congestion}%)</option>`).join('');
        }
    } catch (e) {}

    const slider = document.getElementById('sim-congestion-slider');
    const valDisplay = document.getElementById('sim-slider-val');
    if (slider && valDisplay) {
        slider.addEventListener('input', (e) => {
            valDisplay.textContent = `${e.target.value}%`;
        });
    }

    simForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const roadId = document.getElementById('sim-road-select').value;
        const congestion = document.getElementById('sim-congestion-slider').value;

        try {
            const res = await fetch('/api/traffic/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: parseInt(roadId), congestion: parseInt(congestion) })
            });
            const data = await res.json();
            if (data.status === 'success') {
                alert(`✅ ${data.message}`);
                fetchAdminStats();
                fetchAndRenderCharts();
            }
        } catch (err) {
            alert('Failed to update traffic');
        }
    });

    // AI Prediction Form
    const aiForm = document.getElementById('ai-predict-form');
    if (aiForm) {
        aiForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const road = document.getElementById('ai-road-select').value;
            const hour = document.getElementById('ai-hour-input').value;
            const weather = document.getElementById('ai-weather-select').value;

            try {
                const res = await fetch('/api/predict-traffic', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ road: road, hour: parseInt(hour), weather: weather })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    const p = data.prediction;
                    document.getElementById('ai-result-box').style.display = 'block';
                    document.getElementById('ai-result-box').innerHTML = `
                        <div style="font-weight: 700; color: #60a5fa; font-size: 1rem;">Forecast for ${p.road} at ${p.target_hour} (${p.weather})</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #f8fafc; margin: 4px 0;">Predicted Congestion: ${p.predicted_congestion}% <span class="stat-badge badge-${p.predicted_status.toLowerCase()}">${p.predicted_status}</span></div>
                        <div style="font-size: 0.85rem; color: #facc15; margin-top: 4px;">${p.advisory}</div>
                        <div style="font-size: 0.72rem; color: #64748b; margin-top: 6px;">Powered by: ${p.model_engine}</div>
                    `;
                }
            } catch (err) {
                alert('Prediction failed');
            }
        });
    }
}

async function setupIncidentTable() {
    const tableBody = document.getElementById('admin-incidents-tbody');
    if (!tableBody) return;

    try {
        const res = await fetch('/api/incidents');
        const data = await res.json();
        if (data.status === 'success') {
            tableBody.innerHTML = data.incidents.map(inc => `
                <tr>
                    <td><strong>#${inc.id}</strong></td>
                    <td><span class="stat-badge badge-severe">${inc.type}</span></td>
                    <td>${inc.road_name || inc.location}</td>
                    <td style="max-width: 250px; font-size: 0.8rem; color: #cbd5e1;">${inc.description}</td>
                    <td>
                        <span class="stat-badge ${inc.status === 'Active' ? 'badge-severe' : (inc.status === 'In Progress' ? 'badge-moderate' : 'badge-good')}">
                            ${inc.status}
                        </span>
                    </td>
                    <td>
                        ${inc.status !== 'Resolved' ? `
                            <button class="btn-secondary" style="padding: 0.2rem 0.6rem; font-size: 0.75rem;" onclick="resolveIncident(${inc.id})">Mark Resolved</button>
                        ` : '<span style="color: #34d399; font-size: 0.8rem;">✓ Closed</span>'}
                    </td>
                </tr>
            `).join('');
        }
    } catch (e) {
        console.error('Error rendering incident table:', e);
    }
}

async function resolveIncident(id) {
    try {
        const res = await fetch(`/api/incidents/${id}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'Resolved' })
        });
        const data = await res.json();
        if (data.status === 'success') {
            setupIncidentTable();
            fetchAdminStats();
            fetchAndRenderCharts();
        }
    } catch (err) {
        alert('Could not update incident status');
    }
}
