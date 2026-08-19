from flask import Blueprint, jsonify, request
from backend.models import db, Bus

transport_bp = Blueprint('transport', __name__, url_prefix='/api')

METRO_STATIONS = [
    {"name": "Chennai International Airport", "line": "Blue Line", "latitude": 12.9941, "longitude": 80.1709, "frequency_mins": 5},
    {"name": "Meenambakkam", "line": "Blue Line", "latitude": 12.9875, "longitude": 80.1762, "frequency_mins": 5},
    {"name": "Nanganallur Road", "line": "Blue Line", "latitude": 12.9972, "longitude": 80.1884, "frequency_mins": 5},
    {"name": "Alandur Interchange", "line": "Blue/Green Line", "latitude": 13.0035, "longitude": 80.1988, "frequency_mins": 4},
    {"name": "Guindy Metro", "line": "Blue Line", "latitude": 13.0067, "longitude": 80.2025, "frequency_mins": 5},
    {"name": "Saidapet", "line": "Blue Line", "latitude": 13.0232, "longitude": 80.2201, "frequency_mins": 5},
    {"name": "Nandanam", "line": "Blue Line", "latitude": 13.0305, "longitude": 80.2337, "frequency_mins": 5},
    {"name": "Teynampet", "line": "Blue Line", "latitude": 13.0402, "longitude": 80.2452, "frequency_mins": 5},
    {"name": "AG-DMS", "line": "Blue Line", "latitude": 13.0482, "longitude": 80.2520, "frequency_mins": 5},
    {"name": "Thousand Lights", "line": "Blue Line", "latitude": 13.0585, "longitude": 80.2595, "frequency_mins": 5},
    {"name": "LIC", "line": "Blue Line", "latitude": 13.0674, "longitude": 80.2678, "frequency_mins": 5},
    {"name": "Chennai Central Metro", "line": "Blue/Green Line", "latitude": 13.0827, "longitude": 80.2707, "frequency_mins": 4}
]

@transport_bp.route('/buses', methods=['GET'])
def get_buses():
    """
    Returns list of active public buses, occupancies, ETAs, and locations.
    """
    buses = Bus.query.all()
    result = [b.to_dict() for b in buses]

    avg_occupancy = round(sum(b.occupancy_percent for b in buses) / max(1, len(buses)), 1)
    crowded_count = sum(1 for b in buses if b.occupancy_percent > 75)

    return jsonify({
        'status': 'success',
        'active_fleet_count': len(result),
        'average_occupancy': avg_occupancy,
        'crowded_buses': crowded_count,
        'buses': result
    })

@transport_bp.route('/buses/<int:bus_id>', methods=['GET'])
def get_bus_detail(bus_id):
    bus = db.session.get(Bus, bus_id)
    if not bus:
        return jsonify({'status': 'error', 'message': 'Bus not found'}), 404
    return jsonify({
        'status': 'success',
        'bus': bus.to_dict()
    })

@transport_bp.route('/metro', methods=['GET'])
def get_metro_lines():
    """
    Returns metro transit lines and key station coordinates.
    """
    return jsonify({
        'status': 'success',
        'network': 'Chennai Metro Rail Limited (CMRL)',
        'stations_count': len(METRO_STATIONS),
        'stations': METRO_STATIONS
    })
