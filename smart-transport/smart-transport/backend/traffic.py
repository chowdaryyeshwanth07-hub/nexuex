from flask import Blueprint, jsonify, request
from backend.models import db, TrafficRoad

traffic_bp = Blueprint('traffic', __name__, url_prefix='/api/traffic')

def classify_congestion(percentage):
    if percentage <= 30:
        return "Low"
    elif percentage <= 60:
        return "Moderate"
    elif percentage <= 80:
        return "High"
    else:
        return "Severe"

@traffic_bp.route('', methods=['GET'])
def get_all_traffic():
    """
    Returns list of all monitored roads and congestion status.
    """
    roads = TrafficRoad.query.all()
    result = [r.to_dict() for r in roads]
    
    # Calculate city average
    if roads:
        avg_congestion = round(sum(r.congestion for r in roads) / len(roads), 1)
        severe_count = sum(1 for r in roads if r.status == 'Severe')
        high_count = sum(1 for r in roads if r.status == 'High')
    else:
        avg_congestion = 0
        severe_count = 0
        high_count = 0

    return jsonify({
        'status': 'success',
        'count': len(result),
        'average_congestion': avg_congestion,
        'severe_roads_count': severe_count,
        'high_congestion_count': high_count,
        'roads': result
    })

@traffic_bp.route('/<int:road_id>', methods=['GET'])
def get_road_detail(road_id):
    road = db.session.get(TrafficRoad, road_id)
    if not road:
        return jsonify({'status': 'error', 'message': 'Road not found'}), 404
    return jsonify({
        'status': 'success',
        'road': road.to_dict()
    })

@traffic_bp.route('/update', methods=['POST'])
def update_road_traffic():
    """
    Admin simulation endpoint to dynamically update road congestion.
    """
    data = request.get_json() or {}
    road_id = data.get('id')
    congestion = data.get('congestion')

    if road_id is None or congestion is None:
        return jsonify({'status': 'error', 'message': 'Missing road id or congestion level'}), 400

    road = db.session.get(TrafficRoad, road_id)
    if not road:
        return jsonify({'status': 'error', 'message': 'Road not found'}), 404

    congestion = max(0, min(100, int(congestion)))
    road.congestion = congestion
    road.status = classify_congestion(congestion)
    # Estimate speed reduction based on congestion
    road.avg_speed_kmh = round(max(10.0, 60.0 * (1.0 - (congestion / 120.0))), 1)
    
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': f"Updated {road.road} congestion to {road.congestion}% ({road.status})",
        'road': road.to_dict()
    })
