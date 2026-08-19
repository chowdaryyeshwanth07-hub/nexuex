/**
 * Multi-Modal Route Recommendation & Journey Planner Controller
 */

let currentRouteData = null;
let currentPreference = 'Balanced';

async function initRouteModule() {
    // 1. Populate Origin and Destination dropdowns
    try {
        const res = await fetch('/api/locations');
        const data = await res.json();
        if (data.status === 'success' && data.locations) {
            const originSelect = document.getElementById('select-origin');
            const destSelect = document.getElementById('select-destination');

            if (originSelect && destSelect) {
                const optionsHtml = data.locations.map(loc => 
                    `<option value="${loc.name}">${loc.name} (${loc.category})</option>`
                ).join('');

                originSelect.innerHTML = optionsHtml;
                destSelect.innerHTML = optionsHtml;

                // Set default demo scenario: VIT Chennai -> Chennai Airport
                originSelect.value = "VIT Chennai";
                destSelect.value = "Chennai International Airport";
            }
        }
    } catch (e) {
        console.error('Error fetching locations:', e);
    }

    // 2. Bind preference selector buttons
    const prefButtons = document.querySelectorAll('.pref-tab');
    prefButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            prefButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentPreference = btn.getAttribute('data-pref') || 'Balanced';
            // Auto re-calculate route if form was already executed
            calculateRoute();
        });
    });

    // 3. Bind Journey Form Submit
    const form = document.getElementById('journey-planner-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            calculateRoute();
        });
    }

    // Trigger initial calculation for default demonstration scenario
    setTimeout(() => {
        calculateRoute();
    }, 600);
}

async function calculateRoute() {
    const originSelect = document.getElementById('select-origin');
    const destSelect = document.getElementById('select-destination');

    const origin = originSelect ? originSelect.value : 'VIT Chennai';
    const destination = destSelect ? destSelect.value : 'Chennai International Airport';

    if (origin === destination) {
        alert('Origin and Destination cannot be the same. Please choose distinct locations.');
        return;
    }

    const searchBtn = document.getElementById('btn-calculate-route');
    if (searchBtn) {
        searchBtn.innerHTML = `<span>⏳ Optimizing Routes...</span>`;
        searchBtn.disabled = true;
    }

    try {
        const response = await fetch('/api/recommendation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                origin: origin,
                destination: destination,
                preference: currentPreference
            })
        });

        const json = await response.json();
        if (json.status === 'success' && json.data) {
            currentRouteData = json.data;
            renderRouteResults(json.data);

            // Update Map Polyline and Markers
            if (typeof drawRecommendedRoute === 'function') {
                const winner = json.data.recommended_option;
                drawRecommendedRoute(
                    json.data.origin_coords,
                    json.data.destination_coords,
                    json.data.route_polyline,
                    winner.mode
                );
            }
        }
    } catch (err) {
        console.error('Error calculating route:', err);
    } finally {
        if (searchBtn) {
            searchBtn.innerHTML = `<span>🚀 Calculate Smart Route</span>`;
            searchBtn.disabled = false;
        }
    }
}

function renderRouteResults(data) {
    const winner = data.recommended_option;
    const allOptions = data.all_options;
    const resultsContainer = document.getElementById('route-results-container');
    if (!resultsContainer) return;

    resultsContainer.style.display = 'block';

    // 1. Render Top Winner Card
    const winnerCardHtml = `
        <div class="winner-card">
            <div class="winner-badge">
                <span>🏆 RECOMMENDED OPTION (${data.preference_applied.toUpperCase()})</span>
            </div>
            <div class="winner-grid">
                <div>
                    <div class="winner-title">${winner.icon} ${winner.mode}</div>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 4px;">${winner.description}</p>
                </div>
                <div class="winner-score-ring">
                    <div class="score-num">${winner.score}</div>
                    <div class="score-txt">Index Score</div>
                </div>
            </div>

            <div class="winner-metrics">
                <div class="winner-metric-item">
                    <span class="metric-icon">⏱️</span>
                    <div>
                        <div class="metric-val">${winner.time_mins} mins</div>
                        <div class="metric-lbl">Travel Time</div>
                    </div>
                </div>
                <div class="winner-metric-item">
                    <span class="metric-icon">💰</span>
                    <div>
                        <div class="metric-val">₹${winner.cost_inr}</div>
                        <div class="metric-lbl">Estimated Cost</div>
                    </div>
                </div>
                <div class="winner-metric-item">
                    <span class="metric-icon">🌱</span>
                    <div>
                        <div class="metric-val">${winner.co2_kg} kg CO₂</div>
                        <div class="metric-lbl">Emissions</div>
                    </div>
                </div>
                <div class="winner-metric-item">
                    <span class="metric-icon">🚦</span>
                    <div>
                        <div class="metric-val">${winner.traffic_exposure_percent}%</div>
                        <div class="metric-lbl">Traffic Impact</div>
                    </div>
                </div>
            </div>

            <div class="savings-banner">
                <span>🌿</span>
                <span>
                    <strong>Environmental & Pocket Benefit:</strong> You save <strong>₹${winner.savings.money_saved_inr}</strong> and cut <strong>${winner.savings.co2_saved_kg} kg CO₂</strong> (${winner.savings.co2_reduction_percentage}% reduction vs driving a private car).
                </span>
            </div>

            <!-- Itinerary Steps -->
            <div style="margin-top: 1.25rem;">
                <div style="font-size: 0.88rem; font-weight: 700; color: #fff; margin-bottom: 0.6rem;">🗺️ Journey Breakdown:</div>
                <div class="timeline">
                    ${winner.steps.map(step => `
                        <div class="timeline-step">
                            <div style="font-weight: 600; color: #f8fafc;">${step.instruction}</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted);">${step.duration_mins} mins • ${step.distance_km} km</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;

    // 2. Render Comparison Grid for all remaining options
    const comparisonCardsHtml = allOptions.map(opt => {
        const isWin = opt.is_recommended;
        return `
            <div class="route-card ${isWin ? 'active-selection' : ''}">
                <div class="route-header">
                    <div class="route-title">${opt.icon} ${opt.mode}</div>
                    <div class="route-score" style="color: ${isWin ? '#34d399' : '#94a3b8'};">Score: ${opt.score}</div>
                </div>
                <div class="route-details-grid">
                    <div>
                        <div class="d-val">${opt.time_mins} min</div>
                        <div class="d-lbl">Time</div>
                    </div>
                    <div>
                        <div class="d-val">₹${opt.cost_inr}</div>
                        <div class="d-lbl">Cost</div>
                    </div>
                    <div>
                        <div class="d-val">${opt.co2_kg} kg</div>
                        <div class="d-lbl">CO₂</div>
                    </div>
                </div>
                <div style="font-size: 0.78rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    ${opt.description}
                </div>
                <div style="display: flex; gap: 0.35rem; flex-wrap: wrap;">
                    ${opt.badges.map(b => `<span class="stat-badge badge-good" style="font-size: 0.68rem;">${b}</span>`).join('')}
                </div>
            </div>
        `;
    }).join('');

    resultsContainer.innerHTML = `
        ${winnerCardHtml}
        <div style="margin-top: 1.25rem;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #fff; margin-bottom: 0.75rem;">📊 Compare All Modal Alternatives</div>
            <div class="routes-comparison-grid">
                ${comparisonCardsHtml}
            </div>
        </div>
    `;
}
