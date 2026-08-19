import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class TrafficRoad(db.Model):
    __tablename__ = 'traffic_roads'
    
    id = db.Column(db.Integer, primary_key=True)
    road = db.Column(db.String(120), nullable=False)
    congestion = db.Column(db.Integer, nullable=False) # 0 - 100
    avg_speed_kmh = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False) # Low, Moderate, High, Severe
    start_lat = db.Column(db.Float, nullable=False)
    start_lng = db.Column(db.Float, nullable=False)
    end_lat = db.Column(db.Float, nullable=False)
    end_lng = db.Column(db.Float, nullable=False)
    length_km = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'road': self.road,
            'congestion': self.congestion,
            'avg_speed_kmh': self.avg_speed_kmh,
            'status': self.status,
            'start_lat': self.start_lat,
            'start_lng': self.start_lng,
            'end_lat': self.end_lat,
            'end_lng': self.end_lng,
            'length_km': self.length_km,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Bus(db.Model):
    __tablename__ = 'buses'
    
    id = db.Column(db.Integer, primary_key=True)
    bus_number = db.Column(db.String(50), nullable=False)
    route_name = db.Column(db.String(120), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    eta_mins = db.Column(db.Integer, nullable=False)
    occupancy_percent = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    current_lat = db.Column(db.Float, nullable=False)
    current_lng = db.Column(db.Float, nullable=False)
    fare_inr = db.Column(db.Float, default=25.0)
    updated_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'bus': self.bus_number,
            'route_name': self.route_name,
            'destination': self.destination,
            'eta': self.eta_mins,
            'occupancy': self.occupancy_percent,
            'status': self.status,
            'current_lat': self.current_lat,
            'current_lng': self.current_lng,
            'fare': self.fare_inr,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ParkingLocation(db.Model):
    __tablename__ = 'parking_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    has_ev_charging = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        occupancy_rate = round(((self.total_spots - self.available_spots) / max(1, self.total_spots)) * 100, 1)
        return {
            'id': self.id,
            'name': self.name,
            'area': self.area,
            'total': self.total_spots,
            'available': self.available_spots,
            'occupied': self.total_spots - self.available_spots,
            'occupancy_rate': occupancy_rate,
            'price': self.price_per_hour,
            'has_ev_charging': self.has_ev_charging,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PollutionStation(db.Model):
    __tablename__ = 'pollution_stations'
    
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(120), nullable=False)
    aqi = db.Column(db.Integer, nullable=False)
    pm25 = db.Column(db.Float, nullable=False)
    pm10 = db.Column(db.Float, nullable=False)
    primary_pollutant = db.Column(db.String(50), default='PM2.5')
    status = db.Column(db.String(80), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'location': self.location,
            'aqi': self.aqi,
            'pm25': self.pm25,
            'pm10': self.pm10,
            'primary_pollutant': self.primary_pollutant,
            'status': self.status,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Incident(db.Model):
    __tablename__ = 'incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80), nullable=False)
    road_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(50), default='Medium')
    status = db.Column(db.String(50), default='Active')
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    reported_time = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'incident': self.type,
            'road_name': self.road_name,
            'location': self.road_name,
            'description': self.description,
            'severity': self.severity,
            'status': self.status,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'reported_time': self.reported_time.strftime('%Y-%m-%d %H:%M:%S') if self.reported_time else None
        }

class LocationNode(db.Model):
    __tablename__ = 'location_nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    category = db.Column(db.String(80), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'description': self.description
        }

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='commuter')
    total_trips = db.Column(db.Integer, default=0)
    total_co2_saved_kg = db.Column(db.Float, default=0.0)
    total_money_saved_inr = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'total_trips': self.total_trips,
            'total_co2_saved_kg': round(self.total_co2_saved_kg, 2),
            'total_money_saved_inr': round(self.total_money_saved_inr, 2)
        }

class TripLog(db.Model):
    __tablename__ = 'trip_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(120), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    mode_chosen = db.Column(db.String(80), nullable=False)
    travel_time_mins = db.Column(db.Integer, nullable=False)
    cost_inr = db.Column(db.Float, nullable=False)
    co2_kg = db.Column(db.Float, nullable=False)
    co2_saved_kg = db.Column(db.Float, nullable=False)
    money_saved_inr = db.Column(db.Float, nullable=False)
    preference = db.Column(db.String(50), default='Balanced')
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'origin': self.origin,
            'destination': self.destination,
            'mode_chosen': self.mode_chosen,
            'travel_time_mins': self.travel_time_mins,
            'cost_inr': self.cost_inr,
            'co2_kg': self.co2_kg,
            'co2_saved_kg': self.co2_saved_kg,
            'money_saved_inr': self.money_saved_inr,
            'preference': self.preference,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
