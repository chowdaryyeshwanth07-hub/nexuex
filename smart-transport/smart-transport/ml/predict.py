import os
import pickle
import numpy as np
from flask import Blueprint, jsonify, request

predict_bp = Blueprint('predict', __name__, url_prefix='/api')

_model_cache = None

def get_model():
    global _model_cache
    if _model_cache is not None:
        return _model_cache

    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'traffic_model.pkl')
    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as f:
                _model_cache = pickle.load(f)
                return _model_cache
        except Exception as e:
            print(f"Warning loading model: {e}")
            return None
    return None

def predict_congestion(road_name, hour=18, day_of_week=2, weather="Clear", prev_congestion=65.0):
    bundle = get_model()
    
    roads = bundle['roads'] if bundle else [
        "OMR (IT Corridor)", "GST Road (Airport Corridor)", "ECR (East Coast Road)",
        "Mount Road (Anna Salai)", "Inner Ring Road (100 Ft Rd)", "Vandalur-Kelambakkam Road",
        "Velachery Main Road", "Poonamallee High Road", "Rajiv Gandhi Salai", "Pallavaram-Thoraipakkam Radial Rd"
    ]
    
    road_idx = 0
    for idx, r in enumerate(roads):
        if road_name.lower() in r.lower():
            road_idx = idx
            break

    weather_idx = 0
    if weather == "Rainy": weather_idx = 1
    elif weather == "Cloudy": weather_idx = 2
    elif weather == "Foggy": weather_idx = 3

    is_weekend = 1.0 if day_of_week in [5, 6] else 0.0

    # Diurnal peak activations
    morning_peak = float(np.exp(-((hour - 9.5) ** 2) / 4.0))
    evening_peak = float(np.exp(-((hour - 18.5) ** 2) / 6.0))

    road_bias = 0.0
    if road_idx in [0, 3, 7]: # OMR, Mount Road, Poonamallee
        road_bias = 12.0
    elif road_idx in [2, 5]: # ECR, Vandalur
        road_bias = -10.0

    rain_factor = 1.0 if weather_idx == 1 else 0.0
    fog_factor = 1.0 if weather_idx == 3 else 0.0

    if bundle and 'weights' in bundle:
        feature_vector = np.array([
            1.0,
            morning_peak,
            evening_peak,
            is_weekend,
            rain_factor,
            fog_factor,
            float(prev_congestion) / 100.0,
            road_bias / 10.0
        ], dtype=np.float64)

        pred_val = float(feature_vector @ bundle['weights'])
        predicted_val = int(round(np.clip(pred_val, 5, 99)))
        accuracy_info = f"ML Ridge Regressor (R²: {bundle.get('r2', 0.96)})"
    else:
        # Statistical baseline
        base = 25.0 + (48.0 * morning_peak) + (55.0 * evening_peak) + road_bias + (rain_factor * 18.0)
        predicted_val = int(round(np.clip((base * 0.7) + (float(prev_congestion) * 0.3), 10, 95)))
        accuracy_info = "Statistical Regression Heuristic"

    if predicted_val <= 30:
        status = "Low"
        warning = "🟢 Traffic flowing smoothly"
    elif predicted_val <= 60:
        status = "Moderate"
        warning = "🟡 Normal traffic conditions expected"
    elif predicted_val <= 80:
        status = "High"
        warning = "🟠 Heavy traffic anticipated - consider public transit"
    else:
        status = "Severe"
        warning = "🔴 Severe gridlock predicted - recommend Bus + Metro bypass"

    return {
        'road': roads[road_idx],
        'target_hour': f"{hour:02d}:00",
        'day_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day_of_week % 7],
        'weather': weather,
        'current_congestion': int(prev_congestion),
        'predicted_congestion': predicted_val,
        'predicted_status': status,
        'advisory': warning,
        'model_engine': accuracy_info
    }

@predict_bp.route('/predict-traffic', methods=['GET', 'POST'])
def handle_predict():
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args

    road_name = data.get('road', 'OMR (IT Corridor)')
    hour = int(data.get('hour', 18))
    day_of_week = int(data.get('day_of_week', 2))
    weather = data.get('weather', 'Clear')
    prev_congestion = float(data.get('current_congestion', 68.0))

    result = predict_congestion(road_name, hour, day_of_week, weather, prev_congestion)
    return jsonify({
        'status': 'success',
        'prediction': result
    })
