import os
import csv
from backend.models import db, TrafficRoad, Bus, ParkingLocation, PollutionStation, Incident, LocationNode, User, TripLog

def get_db_path(base_dir=None):
    if base_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_dir = os.path.join(base_dir, 'database')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'transport.db')

def init_db(app, base_dir=None):
    db_path = get_db_path(base_dir)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path.replace(os.sep, '/')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_data_if_needed(base_dir)

def seed_data_if_needed(base_dir=None):
    if base_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_dir = os.path.join(base_dir, 'data')

    # Seed Locations
    if LocationNode.query.count() == 0:
        loc_csv = os.path.join(data_dir, 'locations.csv')
        if os.path.exists(loc_csv):
            with open(loc_csv, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    node = LocationNode(
                        id=int(row['id']),
                        name=str(row['name']),
                        category=str(row['category']),
                        latitude=float(row['latitude']),
                        longitude=float(row['longitude']),
                        description=str(row.get('description', ''))
                    )
                    db.session.add(node)
            db.session.commit()

    # Seed Traffic Roads
    if TrafficRoad.query.count() == 0:
        traffic_csv = os.path.join(data_dir, 'traffic.csv')
        if os.path.exists(traffic_csv):
            with open(traffic_csv, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    road = TrafficRoad(
                        id=int(row['id']),
                        road=str(row['road']),
                        congestion=int(row['congestion']),
                        avg_speed_kmh=float(row['avg_speed_kmh']),
                        status=str(row['status']),
                        start_lat=float(row['start_lat']),
                        start_lng=float(row['start_lng']),
                        end_lat=float(row['end_lat']),
                        end_lng=float(row['end_lng']),
                        length_km=float(row['length_km'])
                    )
                    db.session.add(road)
            db.session.commit()

    # Seed Buses
    if Bus.query.count() == 0:
        bus_csv = os.path.join(data_dir, 'buses.csv')
        if os.path.exists(bus_csv):
            with open(bus_csv, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    bus = Bus(
                        id=int(row['id']),
                        bus_number=str(row['bus_number']),
                        route_name=str(row['route_name']),
                        destination=str(row['destination']),
                        eta_mins=int(row['eta_mins']),
                        occupancy_percent=int(row['occupancy_percent']),
                        status=str(row['status']),
                        current_lat=float(row['current_lat']),
                        current_lng=float(row['current_lng']),
                        fare_inr=float(row.get('fare_inr', 25.0))
                    )
                    db.session.add(bus)
            db.session.commit()

    # Seed Parking
    if ParkingLocation.query.count() == 0:
        parking_csv = os.path.join(data_dir, 'parking.csv')
        if os.path.exists(parking_csv):
            with open(parking_csv, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    ev = str(row['has_ev_charging']).strip().lower() in ['true', '1', 'yes']
                    parking = ParkingLocation(
                        id=int(row['id']),
                        name=str(row['name']),
                        area=str(row['area']),
                        total_spots=int(row['total_spots']),
                        available_spots=int(row['available_spots']),
                        price_per_hour=float(row['price_per_hour']),
                        has_ev_charging=ev,
                        latitude=float(row['latitude']),
                        longitude=float(row['longitude'])
                    )
                    db.session.add(parking)
            db.session.commit()

    # Seed Pollution Stations
    if PollutionStation.query.count() == 0:
        pollution_csv = os.path.join(data_dir, 'pollution.csv')
        if os.path.exists(pollution_csv):
            with open(pollution_csv, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    station = PollutionStation(
                        id=int(row['id']),
                        location=str(row['location']),
                        aqi=int(row['aqi']),
                        pm25=float(row['pm25']),
                        pm10=float(row['pm10']),
                        primary_pollutant=str(row.get('primary_pollutant', 'PM2.5')),
                        status=str(row['status']),
                        latitude=float(row['latitude']),
                        longitude=float(row['longitude'])
                    )
                    db.session.add(station)
            db.session.commit()

    # Seed Incidents
    if Incident.query.count() == 0:
        incidents_csv = os.path.join(data_dir, 'incidents.csv')
        if os.path.exists(incidents_csv):
            with open(incidents_csv, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    inc = Incident(
                        id=int(row['id']),
                        type=str(row['type']),
                        road_name=str(row['road_name']),
                        description=str(row['description']),
                        severity=str(row['severity']),
                        status=str(row['status']),
                        latitude=float(row['latitude']),
                        longitude=float(row['longitude'])
                    )
                    db.session.add(inc)
            db.session.commit()

    # Seed Sample Admin & Commuter Users
    if User.query.count() == 0:
        admin_user = User(
            username='admin',
            email='admin@smarttransport.org',
            password_hash='admin123',
            role='admin',
            total_trips=48,
            total_co2_saved_kg=142.8,
            total_money_saved_inr=3850.0
        )
        commuter_user = User(
            username='commuter',
            email='commuter@vit.ac.in',
            password_hash='commuter123',
            role='commuter',
            total_trips=14,
            total_co2_saved_kg=38.4,
            total_money_saved_inr=1120.0
        )
        db.session.add(admin_user)
        db.session.add(commuter_user)
        db.session.commit()

    # Seed Sample Trip Logs for Charts
    if TripLog.query.count() == 0:
        sample_logs = [
            TripLog(origin='VIT Chennai', destination='Chennai Airport', mode_chosen='Bus + Metro', travel_time_mins=43, cost_inr=40.0, co2_kg=0.9, co2_saved_kg=4.5, money_saved_inr=140.0, preference='Balanced'),
            TripLog(origin='Tambaram Hub', destination='Guindy Metro', mode_chosen='Metro', travel_time_mins=22, cost_inr=20.0, co2_kg=0.3, co2_saved_kg=2.8, money_saved_inr=70.0, preference='Fastest'),
            TripLog(origin='OMR Sholinganallur', destination='Chennai Central', mode_chosen='Bus', travel_time_mins=55, cost_inr=35.0, co2_kg=1.2, co2_saved_kg=3.9, money_saved_inr=120.0, preference='Cheapest'),
            TripLog(origin='ECR Thiruvanmiyur', destination='Chennai Airport', mode_chosen='Bus + Metro', travel_time_mins=38, cost_inr=45.0, co2_kg=0.8, co2_saved_kg=3.6, money_saved_inr=110.0, preference='Greenest'),
            TripLog(origin='VIT Chennai', destination='Guindy Metro', mode_chosen='Bus + Metro', travel_time_mins=39, cost_inr=35.0, co2_kg=0.8, co2_saved_kg=4.1, money_saved_inr=130.0, preference='Balanced')
        ]
        db.session.add_all(sample_logs)
        db.session.commit()
