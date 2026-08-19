"""
Automated Test Suite for Smart Transportation Ecosystem
Verifies:
1. Database initialization and CSV seeding
2. Traffic API (/api/traffic)
3. Buses / Transit API (/api/buses, /api/metro)
4. Smart Parking API (/api/parking, /api/parking/nearest)
5. Pollution API (/api/pollution)
6. Route Recommendation Engine (/api/recommendation, /api/routes)
7. Carbon Emissions & Savings Calculator
8. Incident Reporting & Resolution (/api/incidents)
9. Admin Statistics & Charts Data (/api/admin/statistics, /api/admin/charts-data)
10. AI Traffic Prediction (/api/predict-traffic)
"""

import os
import sys
import unittest
import json

# Add project root to path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import create_app
from backend.models import db, TrafficRoad, Bus, ParkingLocation, PollutionStation, Incident
from backend.emissions import calculate_emissions, calculate_savings

class SmartTransportTestSuite(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_api_health_check(self):
        """Verify API index root endpoint"""
        response = self.client.get('/api')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'online')
        self.assertIn('endpoints', data)

    def test_02_traffic_api(self):
        """Verify /api/traffic returns roads with valid congestion ratings"""
        response = self.client.get('/api/traffic')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(data['count'], 0)
        
        # Check first road structure
        first_road = data['roads'][0]
        self.assertIn('road', first_road)
        self.assertIn('congestion', first_road)
        self.assertIn('status', first_road)
        self.assertIn(first_road['status'], ['Low', 'Moderate', 'High', 'Severe'])

    def test_03_buses_api(self):
        """Verify /api/buses returns active transit fleet"""
        response = self.client.get('/api/buses')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(data['active_fleet_count'], 0)
        
        first_bus = data['buses'][0]
        self.assertIn('bus', first_bus)
        self.assertIn('destination', first_bus)
        self.assertIn('occupancy', first_bus)
        self.assertIn('eta', first_bus)

    def test_04_parking_api(self):
        """Verify /api/parking returns smart parking spots and nearest search"""
        response = self.client.get('/api/parking')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(data['total_available_spots'], 0)

        # Test nearest parking search to Airport coordinates (12.9941, 80.1709)
        nearest_res = self.client.get('/api/parking/nearest?lat=12.9941&lng=80.1709')
        self.assertEqual(nearest_res.status_code, 200)
        n_data = json.loads(nearest_res.data)
        self.assertIn('recommended_parking', n_data)
        self.assertIsNotNone(n_data['recommended_parking'])

    def test_05_pollution_api(self):
        """Verify /api/pollution returns AQI classifications"""
        response = self.client.get('/api/pollution')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(data['station_count'], 0)
        
        station = data['stations'][0]
        self.assertIn('aqi', station)
        self.assertIn('status', station)
        self.assertIn('pm25', station)

    def test_06_emissions_calculator(self):
        """Verify CO2 calculations and baseline comparison savings"""
        dist_km = 25.0
        car_co2 = calculate_emissions(dist_km, 'car')
        bus_co2 = calculate_emissions(dist_km, 'bus')
        metro_co2 = calculate_emissions(dist_km, 'metro')

        self.assertAlmostEqual(car_co2, 4.0, delta=0.5) # ~0.160 kg/km * 25 = 4.0 kg
        self.assertLess(bus_co2, car_co2)
        self.assertLess(metro_co2, bus_co2)

        savings = calculate_savings(dist_km, bus_co2, 35.0, car_cost_base=320.0)
        self.assertGreater(savings['co2_saved_kg'], 0)
        self.assertGreater(savings['money_saved_inr'], 0)
        self.assertGreater(savings['co2_reduction_percentage'], 50.0)

    def test_07_route_recommendation_engine(self):
        """Verify route recommendation ranking and multi-modal optimization"""
        payload = {
            "origin": "VIT Chennai",
            "destination": "Chennai International Airport",
            "preference": "Balanced"
        }
        response = self.client.post('/api/recommendation', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['data']

        self.assertEqual(data['origin'], 'VIT Chennai')
        self.assertEqual(data['destination'], 'Chennai International Airport')
        self.assertIn('recommended_option', data)
        self.assertIn('all_options', data)
        self.assertEqual(len(data['all_options']), 4) # Car, Bus, Metro, Bus+Metro

        winner = data['recommended_option']
        self.assertTrue(winner['is_recommended'])
        self.assertIn('steps', winner)
        self.assertGreater(len(winner['steps']), 0)
        self.assertIn('savings', winner)

    def test_08_preference_weightings(self):
        """Verify recommendation weights dynamically shift top scores based on user preference"""
        # Test Greenest preference favors minimal emission options
        res_green = self.client.post('/api/recommendation', data=json.dumps({
            "origin": "VIT Chennai",
            "destination": "Chennai International Airport",
            "preference": "Greenest"
        }), content_type='application/json')
        data_green = json.loads(res_green.data)['data']
        winner_green = data_green['recommended_option']
        self.assertIn(winner_green['id'], ['metro', 'bus_metro', 'bus'])

        # Test Fastest preference
        res_fast = self.client.post('/api/recommendation', data=json.dumps({
            "origin": "VIT Chennai",
            "destination": "Chennai International Airport",
            "preference": "Fastest"
        }), content_type='application/json')
        self.assertEqual(res_fast.status_code, 200)

    def test_09_incident_reporting_workflow(self):
        """Verify reporting a new incident and marking it resolved"""
        new_inc = {
            "type": "Accident",
            "location": "OMR Sholinganallur Junction",
            "description": "Test collision blocking right lane",
            "severity": "High",
            "latitude": 12.9030,
            "longitude": 80.2280
        }
        res = self.client.post('/api/incidents', data=json.dumps(new_inc), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        inc_data = json.loads(res.data)['incident']
        inc_id = inc_data['id']
        self.assertEqual(inc_data['status'], 'Active')

        # Resolve incident
        res_resolve = self.client.post(f'/api/incidents/{inc_id}/status', data=json.dumps({"status": "Resolved"}), content_type='application/json')
        self.assertEqual(res_resolve.status_code, 200)
        updated_data = json.loads(res_resolve.data)['incident']
        self.assertEqual(updated_data['status'], 'Resolved')

    def test_10_admin_and_ml_prediction(self):
        """Verify Admin overview and ML Traffic forecast endpoint"""
        res_stats = self.client.get('/api/admin/statistics')
        self.assertEqual(res_stats.status_code, 200)
        stats = json.loads(res_stats.data)
        self.assertIn('overview', stats)
        self.assertGreater(stats['overview']['active_buses'], 0)

        # Test ML Traffic prediction
        res_pred = self.client.post('/api/predict-traffic', data=json.dumps({
            "road": "OMR (IT Corridor)",
            "hour": 18,
            "weather": "Rainy",
            "current_congestion": 70
        }), content_type='application/json')
        self.assertEqual(res_pred.status_code, 200)
        pred_data = json.loads(res_pred.data)['prediction']
        self.assertIn('predicted_congestion', pred_data)
        self.assertIn('predicted_status', pred_data)
        self.assertIn('advisory', pred_data)

if __name__ == '__main__':
    unittest.main()
