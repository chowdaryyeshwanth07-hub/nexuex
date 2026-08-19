import os
import sys

# Ensure UTF-8 output encoding for Windows terminal compatibility
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Ensure project root is in python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import init_db
from backend.traffic import traffic_bp
from backend.transport import transport_bp
from backend.parking import parking_bp
from backend.pollution import pollution_bp
from backend.recommendation import recommendation_bp
from backend.incidents import incidents_bp
from backend.auth import auth_bp
from backend.admin import admin_bp
from ml.predict import predict_bp

def create_app():
    frontend_dir = os.path.join(BASE_DIR, 'frontend')
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    CORS(app)

    # Initialize Database & seed initial CSV datasets
    init_db(app, base_dir=BASE_DIR)

    # Register Blueprints
    app.register_blueprint(traffic_bp)
    app.register_blueprint(transport_bp)
    app.register_blueprint(parking_bp)
    app.register_blueprint(pollution_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(predict_bp)

    # Serve Main Frontend Commuter Dashboard
    @app.route('/')
    def serve_index():
        return send_from_directory(frontend_dir, 'index.html')

    # Serve Admin Dashboard
    @app.route('/admin')
    @app.route('/admin.html')
    def serve_admin():
        return send_from_directory(frontend_dir, 'admin.html')

    # API Root Health Check
    @app.route('/api')
    def api_index():
        return jsonify({
            'name': 'Smart Transportation Ecosystem API',
            'version': '1.0.0',
            'status': 'online',
            'endpoints': [
                '/api/traffic',
                '/api/buses',
                '/api/parking',
                '/api/pollution',
                '/api/recommendation',
                '/api/routes',
                '/api/incidents',
                '/api/admin/statistics',
                '/api/admin/charts-data',
                '/api/predict-traffic'
            ]
        })

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n=======================================================")
    print(f"Smart Transportation Ecosystem is starting...")
    print(f"Commuter Dashboard: http://127.0.0.1:{port}/")
    print(f"Admin Dashboard:    http://127.0.0.1:{port}/admin.html")
    print(f"API Root:           http://127.0.0.1:{port}/api")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=True)
