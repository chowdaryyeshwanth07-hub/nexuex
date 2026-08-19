import math
from flask import Blueprint, jsonify, request
from backend.models import db, LocationNode, TrafficRoad, Bus, PollutionStation, TripLog
from backend.emissions import calculate_emissions, calculate_savings

recommendation_bp = Blueprint('recommendation', __name__, url_prefix='/api')

WEIGHTS = {
    'Fastest': {'time': 0.70, 'cost': 0.10, 'traffic': 0.15, 'emission': 0.05},
    'Cheapest': {'time': 0.15, 'cost': 0.70, 'traffic': 0.10, 'emission': 0.05},
    'Greenest': {'time': 0.15, 'cost': 0.10, 'traffic': 0.15, 'emission': 0.60},
    'Balanced': {'time': 0.40, 'cost': 0.25, 'traffic': 0.20, 'emission': 0.15}
}

# Coordinate registry for fallback & distance computing
KNOWN_LOCATIONS = {
    "VIT Chennai": (12.8406, 80.1534),
    "Chennai International Airport": (12.9941, 80.1709),
    "Tambaram Hub": (12.9249, 80.1000),
    "Guindy Metro & Station": (13.0067, 80.2025),
    "OMR Sholinganallur": (12.9010, 80.2279),
    "ECR Thiruvanmiyur": (12.9830, 80.2594),
    "Mount Road (Anna Salai)": (13.0305, 80.2337),
    "Chennai Central": (13.0827, 80.2707),
    "Velachery Hub": (12.9756, 80.2207),
    "Koyambedu CMBT": (13.0694, 80.1948)
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_location_coords(loc_name):
    # Check DB first
    node = LocationNode.query.filter(LocationNode.name.ilike(f"%{loc_name}%")).first()
    if node:
        return node.latitude, node.longitude, node.name
    
    # Fallback dictionary
    for k, v in KNOWN_LOCATIONS.items():
        if loc_name.lower() in k.lower() or k.lower() in loc_name.lower():
            return v[0], v[1], k
            
    # Default fallback to VIT Chennai -> Airport
    return 12.8406, 80.1534, loc_name

def get_relevant_corridor_congestion():
    roads = TrafficRoad.query.all()
    if not roads:
        return 65.0
    return round(sum(r.congestion for r in roads) / len(roads), 1)

def generate_route_options(origin_name, dest_name, origin_coords, dest_coords, preference='Balanced'):
    straight_dist = haversine(origin_coords[0], origin_coords[1], dest_coords[0], dest_coords[1])
    # Road network distance is typically ~1.3 - 1.45x straight line
    road_distance = round(max(5.0, straight_dist * 1.38), 1)
    
    avg_congestion = get_relevant_corridor_congestion()

    # --- Mode 1: Private Car ---
    # Car speed drops severely with congestion
    effective_car_speed = max(18.0, 55.0 * (1.0 - (avg_congestion / 130.0)))
    car_time_mins = int(round((road_distance / effective_car_speed) * 60.0 + 8)) # +8 min parking/traffic buffer
    car_cost = int(round(road_distance * 11.5 + 40.0)) # Fuel + parking
    car_emissions = round(calculate_emissions(road_distance, 'car'), 1)
    car_traffic_exposure = int(avg_congestion)

    # --- Mode 2: Public Bus ---
    effective_bus_speed = max(16.0, 42.0 * (1.0 - (avg_congestion / 150.0)))
    bus_time_mins = int(round((road_distance / effective_bus_speed) * 60.0 + 12)) # +12 min stops & waiting
    bus_cost = int(round(min(45.0, max(20.0, road_distance * 1.6))))
    bus_emissions = round(calculate_emissions(road_distance, 'bus'), 1)
    bus_traffic_exposure = int(avg_congestion * 0.9)

    # --- Mode 3: Metro (Direct/Feeder) ---
    # Metro has dedicated right of way (unaffected by road congestion)
    metro_distance = road_distance * 0.95
    metro_speed = 38.0 # km/h including station stops
    metro_transit_time = (metro_distance / metro_speed) * 60.0
    metro_time_mins = int(round(metro_transit_time + 16)) # +16 mins for station access, security, egress walk
    metro_cost = int(round(min(50.0, max(20.0, road_distance * 1.8))))
    metro_emissions = round(calculate_emissions(road_distance, 'metro'), 1)
    metro_traffic_exposure = 10 # virtually zero road traffic

    # --- Mode 4: Multimodal (Walk + Bus + Metro + Walk) ---
    # E.g. Fast feeder bus to nearby Metro line + Metro express bypass + walk to terminal
    feeder_dist = road_distance * 0.35
    metro_leg_dist = road_distance * 0.65
    feeder_time = (feeder_dist / 28.0) * 60.0 + 6
    metro_leg_time = (metro_leg_dist / 42.0) * 60.0 + 4
    multimodal_time_mins = int(round(feeder_time + metro_leg_time + 5)) # walk/transfer
    multimodal_cost = int(round(20.0 + 20.0)) # ₹20 bus + ₹20 metro = ₹40
    multimodal_emissions = round((feeder_dist * 0.038) + (metro_leg_dist * 0.018), 1)
    multimodal_traffic_exposure = int(avg_congestion * 0.35)

    # Compile options
    options = [
        {
            "id": "car",
            "mode": "Car (Private Vehicle)",
            "icon": "🚗",
            "time_mins": car_time_mins,
            "cost_inr": car_cost,
            "co2_kg": car_emissions,
            "traffic_exposure_percent": car_traffic_exposure,
            "distance_km": road_distance,
            "description": "Direct road transit via main arterial highways. Susceptible to congestion and parking constraints.",
            "steps": [
                {"type": "drive", "instruction": f"Drive from {origin_name} via Arterial Road", "duration_mins": car_time_mins - 8, "distance_km": road_distance},
                {"type": "parking", "instruction": f"Find parking near {dest_name} and walk to entrance", "duration_mins": 8, "distance_km": 0.3}
            ],
            "badges": ["Private", "Direct Door-to-Door"]
        },
        {
            "id": "bus",
            "mode": "Public Bus (MTC)",
            "icon": "🚌",
            "time_mins": bus_time_mins,
            "cost_inr": bus_cost,
            "co2_kg": bus_emissions,
            "traffic_exposure_percent": bus_traffic_exposure,
            "distance_km": road_distance,
            "description": "Affordable city transit bus service connecting major terminal hubs.",
            "steps": [
                {"type": "walk", "instruction": f"Walk 350m to nearest Bus Stop from {origin_name}", "duration_mins": 5, "distance_km": 0.35},
                {"type": "bus", "instruction": f"Board MTC Route 21G / 570 towards {dest_name}", "duration_mins": bus_time_mins - 10, "distance_km": road_distance - 0.7},
                {"type": "walk", "instruction": f"Alight at destination stop and walk to {dest_name}", "duration_mins": 5, "distance_km": 0.35}
            ],
            "badges": ["Low Cost", "Public Transit"]
        },
        {
            "id": "metro",
            "mode": "Metro Rail (CMRL)",
            "icon": "🚇",
            "time_mins": metro_time_mins,
            "cost_inr": metro_cost,
            "co2_kg": metro_emissions,
            "traffic_exposure_percent": metro_traffic_exposure,
            "distance_km": road_distance,
            "description": "High-speed grade-separated electric transit avoiding road congestion bottlenecks completely.",
            "steps": [
                {"type": "walk", "instruction": f"Access nearest Metro station from {origin_name}", "duration_mins": 8, "distance_km": 0.6},
                {"type": "metro", "instruction": f"Take Blue Line Metro directly towards {dest_name}", "duration_mins": metro_time_mins - 14, "distance_km": road_distance - 1.0},
                {"type": "walk", "instruction": f"Exit station gate to {dest_name}", "duration_mins": 6, "distance_km": 0.4}
            ],
            "badges": ["Zero Traffic", "Low Carbon"]
        },
        {
            "id": "bus_metro",
            "mode": "Bus + Metro (Multimodal)",
            "icon": "🚌 + 🚇",
            "time_mins": multimodal_time_mins,
            "cost_inr": multimodal_cost,
            "co2_kg": multimodal_emissions,
            "traffic_exposure_percent": multimodal_traffic_exposure,
            "distance_km": road_distance,
            "description": "Optimal multimodal sync: Fast feeder bus to express metro spine, avoiding severe road bottlenecks.",
            "steps": [
                {"type": "walk", "instruction": f"Walk 200m to Feeder Stop at {origin_name}", "duration_mins": 3, "distance_km": 0.2},
                {"type": "bus", "instruction": "Board Feeder Bus 21G to Tambaram / Guindy Metro Interchange", "duration_mins": int(feeder_time), "distance_km": round(feeder_dist, 1)},
                {"type": "transfer", "instruction": "Quick 3-min covered interchange to CMRL Blue Line Platform", "duration_mins": 3, "distance_km": 0.1},
                {"type": "metro", "instruction": f"Take Blue Line Metro Express to {dest_name} Station", "duration_mins": int(metro_leg_time), "distance_km": round(metro_leg_dist, 1)},
                {"type": "walk", "instruction": f"Direct covered skywalk into {dest_name}", "duration_mins": 3, "distance_km": 0.2}
            ],
            "badges": ["Integrated Multi-modal", "High Efficiency", "Green Choice"]
        }
    ]

    # Normalize metrics to 0-100 scores (higher score is better)
    min_time = min(opt['time_mins'] for opt in options)
    max_time = max(opt['time_mins'] for opt in options)
    
    min_cost = min(opt['cost_inr'] for opt in options)
    max_cost = max(opt['cost_inr'] for opt in options)

    min_co2 = min(opt['co2_kg'] for opt in options)
    max_co2 = max(opt['co2_kg'] for opt in options)

    w = WEIGHTS.get(preference, WEIGHTS['Balanced'])

    for opt in options:
        # Time score: shorter time gives higher score
        time_score = 100.0 - (80.0 * (opt['time_mins'] - min_time) / max(1, max_time - min_time))
        # Cost score: lower cost gives higher score
        cost_score = 100.0 - (80.0 * (opt['cost_inr'] - min_cost) / max(1, max_cost - min_cost))
        # Traffic score: lower exposure gives higher score
        traffic_score = 100.0 - opt['traffic_exposure_percent']
        # Emission score: lower emission gives higher score
        emission_score = 100.0 - (80.0 * (opt['co2_kg'] - min_co2) / max(0.01, max_co2 - min_co2))

        total_score = (
            (w['time'] * time_score) +
            (w['cost'] * cost_score) +
            (w['traffic'] * traffic_score) +
            (w['emission'] * emission_score)
        )
        opt['score'] = int(round(total_score))
        opt['breakdown_scores'] = {
            'time_score': int(round(time_score)),
            'cost_score': int(round(cost_score)),
            'traffic_score': int(round(traffic_score)),
            'emission_score': int(round(emission_score))
        }

        # Calculate savings compared to car baseline
        savings = calculate_savings(road_distance, opt['co2_kg'], opt['cost_inr'], car_cost_base=car_cost)
        opt['savings'] = savings

    # Sort options by overall score descending
    options.sort(key=lambda x: x['score'], reverse=True)
    
    # Flag the top recommended option
    options[0]['is_recommended'] = True
    options[0]['recommendation_badge'] = "🏆 RECOMMENDED ROUTE"

    for opt in options[1:]:
        opt['is_recommended'] = False
        opt['recommendation_badge'] = None

    # Generate synthetic polyline waypoints for Leaflet map display
    # Interpolates between origin and destination coordinates with realistic intermediate curve points
    polyline = generate_route_polyline(origin_coords, dest_coords)

    return {
        'origin': origin_name,
        'origin_coords': {'lat': origin_coords[0], 'lng': origin_coords[1]},
        'destination': dest_name,
        'destination_coords': {'lat': dest_coords[0], 'lng': dest_coords[1]},
        'preference_applied': preference,
        'preference_weights': w,
        'corridor_traffic_congestion_avg': avg_congestion,
        'recommended_option': options[0],
        'all_options': options,
        'route_polyline': polyline,
        'total_distance_km': road_distance
    }

def generate_route_polyline(start, end):
    """
    Generates a realistic smooth sequence of coordinates between start and end.
    """
    lat1, lon1 = start
    lat2, lon2 = end
    points = []
    num_segments = 8
    
    # Add gentle curve offset to simulate road bends
    mid_offset_lat = (lon2 - lon1) * 0.15
    mid_offset_lon = -(lat2 - lat1) * 0.15

    for i in range(num_segments + 1):
        t = i / float(num_segments)
        # Bezier curve interpolation
        curv_factor = 4.0 * t * (1.0 - t)
        lat = (1.0 - t) * lat1 + t * lat2 + curv_factor * mid_offset_lat
        lon = (1.0 - t) * lon1 + t * lon2 + curv_factor * mid_offset_lon
        points.append([round(lat, 5), round(lon, 5)])

    return points

@recommendation_bp.route('/recommendation', methods=['GET', 'POST'])
def get_recommendation():
    """
    Accepts origin, destination, and preference (Fastest, Cheapest, Greenest, Balanced)
    and computes the optimized multi-modal route recommendation.
    """
    if request.method == 'POST':
        data = request.get_json() or {}
        origin = data.get('origin', 'VIT Chennai')
        destination = data.get('destination', 'Chennai International Airport')
        preference = data.get('preference', 'Balanced')
    else:
        origin = request.args.get('origin', 'VIT Chennai')
        destination = request.args.get('destination', 'Chennai International Airport')
        preference = request.args.get('preference', 'Balanced')

    origin_lat, origin_lng, origin_clean = get_location_coords(origin)
    dest_lat, dest_lng, dest_clean = get_location_coords(destination)

    result = generate_route_options(
        origin_clean, dest_clean,
        (origin_lat, origin_lng), (dest_lat, dest_lng),
        preference=preference
    )

    return jsonify({
        'status': 'success',
        'data': result
    })

@recommendation_bp.route('/routes', methods=['POST'])
def calculate_routes():
    """
    Alias / endpoint for route calculation and history logging.
    """
    data = request.get_json() or {}
    origin = data.get('origin', 'VIT Chennai')
    destination = data.get('destination', 'Chennai International Airport')
    preference = data.get('preference', 'Balanced')

    origin_lat, origin_lng, origin_clean = get_location_coords(origin)
    dest_lat, dest_lng, dest_clean = get_location_coords(destination)

    result = generate_route_options(
        origin_clean, dest_clean,
        (origin_lat, origin_lng), (dest_lat, dest_lng),
        preference=preference
    )

    # Optional: Log the trip in database
    try:
        winner = result['recommended_option']
        trip = TripLog(
            origin=origin_clean,
            destination=dest_clean,
            mode_chosen=winner['mode'],
            travel_time_mins=winner['time_mins'],
            cost_inr=float(winner['cost_inr']),
            co2_kg=float(winner['co2_kg']),
            co2_saved_kg=float(winner['savings']['co2_saved_kg']),
            money_saved_inr=float(winner['savings']['money_saved_inr']),
            preference=preference
        )
        db.session.add(trip)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({
        'status': 'success',
        'data': result
    })

@recommendation_bp.route('/locations', methods=['GET'])
def get_available_locations():
    """
    Returns list of predefined hub locations for the journey planner dropdown.
    """
    locations = LocationNode.query.all()
    if not locations:
        res = [{"id": i+1, "name": k, "category": "Hub", "latitude": v[0], "longitude": v[1]} for i, (k, v) in enumerate(KNOWN_LOCATIONS.items())]
    else:
        res = [l.to_dict() for l in locations]

    return jsonify({
        'status': 'success',
        'count': len(res),
        'locations': res
    })
