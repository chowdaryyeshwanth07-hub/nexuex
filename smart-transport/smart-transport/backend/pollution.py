from flask import Blueprint, jsonify, request
from backend.models import db, PollutionStation

pollution_bp = Blueprint('pollution', __name__, url_prefix='/api/pollution')

def classify_aqi(aqi):
    if aqi <= 50:
        return "Good", "#10b981"
    elif aqi <= 100:
        return "Moderate", "#f59e0b"
    elif aqi <= 150:
        return "Unhealthy for sensitive groups", "#f97316"
    elif aqi <= 200:
        return "Unhealthy", "#ef4444"
    elif aqi <= 300:
        return "Very unhealthy", "#8b5cf6"
    else:
        return "Hazardous", "#7f1d1d"

@pollution_bp.route('', methods=['GET'])
def get_pollution():
    """
    Returns list of all AQI pollution monitoring stations and city metrics.
    """
    stations = PollutionStation.query.all()
    result = [s.to_dict() for s in stations]

    for item in result:
        status, color = classify_aqi(item['aqi'])
        item['status'] = status
        item['color'] = color

    avg_aqi = round(sum(s.aqi for s in stations) / max(1, len(stations)), 1)
    avg_status, avg_color = classify_aqi(int(avg_aqi))

    return jsonify({
        'status': 'success',
        'station_count': len(result),
        'average_aqi': avg_aqi,
        'average_status': avg_status,
        'average_color': avg_color,
        'stations': result
    })

@pollution_bp.route('/<int:station_id>', methods=['GET'])
def get_station_detail(station_id):
    station = db.session.get(PollutionStation, station_id)
    if not station:
        return jsonify({'status': 'error', 'message': 'Pollution station not found'}), 404
    data = station.to_dict()
    status, color = classify_aqi(data['aqi'])
    data['status'] = status
    data['color'] = color
    return jsonify({
        'status': 'success',
        'station': data
    })

@pollution_bp.route('/by-name', methods=['GET'])
def get_pollution_by_name():
    name = request.args.get('name', '').strip().lower()
    if not name:
        return jsonify({'status': 'error', 'message': 'Missing name parameter'}), 400

    station = PollutionStation.query.filter(PollutionStation.location.ilike(f"%{name}%")).first()
    if not station:
        return jsonify({'status': 'error', 'message': f'No station found for {name}'}), 404

    data = station.to_dict()
    status, color = classify_aqi(data['aqi'])
    data['status'] = status
    data['color'] = color
    return jsonify({
        'status': 'success',
        'station': data
    })
