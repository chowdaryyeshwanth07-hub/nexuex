from flask import Blueprint, jsonify, request
from backend.models import db, ParkingLocation
import math

parking_bp = Blueprint('parking', __name__, url_prefix='/api/parking')

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

@parking_bp.route('', methods=['GET'])
def get_parking():
    """
    Returns list of smart parking locations with occupancy rates and pricing.
    """
    parking_lots = ParkingLocation.query.all()
    result = [p.to_dict() for p in parking_lots]

    total_capacity = sum(p.total_spots for p in parking_lots)
    total_available = sum(p.available_spots for p in parking_lots)
    available_rate = round((total_available / max(1, total_capacity)) * 100, 1)

    return jsonify({
        'status': 'success',
        'total_parking_hubs': len(result),
        'total_capacity': total_capacity,
        'total_available_spots': total_available,
        'overall_availability_rate': available_rate,
        'parking': result
    })

@parking_bp.route('/<int:parking_id>', methods=['GET'])
def get_parking_detail(parking_id):
    lot = db.session.get(ParkingLocation, parking_id)
    if not lot:
        return jsonify({'status': 'error', 'message': 'Parking location not found'}), 404
    return jsonify({
        'status': 'success',
        'parking': lot.to_dict()
    })

@parking_bp.route('/nearest', methods=['GET'])
def get_nearest_parking():
    """
    Finds the nearest parking hub to a given coordinate with available spots.
    """
    try:
        lat = float(request.args.get('lat', 12.9941))
        lng = float(request.args.get('lng', 80.1709))
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid coordinates provided'}), 400

    lots = ParkingLocation.query.all()
    if not lots:
        return jsonify({'status': 'error', 'message': 'No parking facilities found'}), 404

    lots_with_dist = []
    for lot in lots:
        dist = haversine_distance(lat, lng, lot.latitude, lot.longitude)
        data = lot.to_dict()
        data['distance_km'] = dist
        lots_with_dist.append(data)

    # Sort by distance
    lots_with_dist.sort(key=lambda x: (x['available'] == 0, x['distance_km']))

    return jsonify({
        'status': 'success',
        'target_lat': lat,
        'target_lng': lng,
        'recommended_parking': lots_with_dist[0] if lots_with_dist else None,
        'nearby_options': lots_with_dist[:5]
    })
