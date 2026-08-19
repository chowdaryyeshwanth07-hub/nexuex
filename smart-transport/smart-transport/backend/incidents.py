from flask import Blueprint, jsonify, request
from backend.models import db, Incident, utc_now

incidents_bp = Blueprint('incidents', __name__, url_prefix='/api/incidents')

VALID_TYPES = [
    'Accident',
    'Traffic Signal Failure',
    'Road Damage / Pothole',
    'Vehicle Breakdown',
    'Road Construction',
    'Severe Traffic Congestion',
    'Waterlogging'
]

@incidents_bp.route('', methods=['GET'])
def get_incidents():
    """
    Returns list of all reported traffic incidents.
    """
    status_filter = request.args.get('status')
    query = Incident.query
    if status_filter:
        query = query.filter(Incident.status.ilike(status_filter))
    
    incidents = query.order_by(Incident.reported_time.desc()).all()
    result = [inc.to_dict() for inc in incidents]

    active_count = sum(1 for i in incidents if i.status == 'Active')
    in_progress_count = sum(1 for i in incidents if i.status == 'In Progress')
    resolved_count = sum(1 for i in incidents if i.status == 'Resolved')

    return jsonify({
        'status': 'success',
        'total_count': len(result),
        'active_count': active_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'incidents': result
    })

@incidents_bp.route('', methods=['POST'])
def report_incident():
    """
    Submit a new incident report.
    """
    data = request.get_json() or {}
    incident_type = data.get('type', 'Accident')
    location_name = data.get('location', data.get('road_name', 'OMR Corridor'))
    description = data.get('description', 'User reported traffic obstruction')
    severity = data.get('severity', 'Medium')
    latitude = float(data.get('latitude', 12.9250))
    longitude = float(data.get('longitude', 80.1750))

    new_incident = Incident(
        type=incident_type,
        road_name=location_name,
        description=description,
        severity=severity,
        status='Active',
        latitude=latitude,
        longitude=longitude,
        reported_time=utc_now()
    )

    db.session.add(new_incident)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Incident reported successfully and shared with the traffic control center.',
        'incident': new_incident.to_dict()
    }), 201

@incidents_bp.route('/<int:incident_id>/status', methods=['POST', 'PATCH'])
def update_incident_status(incident_id):
    """
    Update incident status (Active, In Progress, Resolved).
    """
    incident = db.session.get(Incident, incident_id)
    if not incident:
        return jsonify({'status': 'error', 'message': 'Incident not found'}), 404

    data = request.get_json() or {}
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'status': 'error', 'message': 'Status parameter is required'}), 400

    incident.status = new_status
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': f"Incident #{incident_id} marked as {incident.status}",
        'incident': incident.to_dict()
    })
