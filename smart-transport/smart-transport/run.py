#!/usr/bin/env python
"""
Smart Transportation Ecosystem Launcher
Trains the AI traffic prediction model if needed, initializes the database,
and starts the integrated web server.
"""

import os
import sys

# Ensure UTF-8 output encoding for Windows terminal compatibility
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def main():
    print("=" * 65)
    print("SMART TRANSPORTATION ECOSYSTEM")
    print("Intelligent Multi-Modal Urban Mobility Platform")
    print("=" * 65)

    # 1. Check & Train ML Traffic Model if missing
    model_path = os.path.join(BASE_DIR, 'ml', 'traffic_model.pkl')
    if not os.path.exists(model_path):
        print("\n[1/2] Training AI Traffic Prediction Model...")
        try:
            from ml.train import train_model
            train_model()
        except Exception as e:
            print(f"Warning: Could not train ML model ({e}). Using statistical heuristic fallback.")
    else:
        print("\n[1/2] AI Traffic Prediction Model is ready.")

    # 2. Start Flask Application
    print("\n[2/2] Starting Flask Web & API Server...")
    from backend.app import create_app

    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "-" * 65)
    print(f"Commuter Navigation Hub:  http://127.0.0.1:{port}/")
    print(f"Operations Admin Portal:  http://127.0.0.1:{port}/admin.html")
    print(f"REST API Health Endpoint: http://127.0.0.1:{port}/api")
    print("-" * 65)
    print("Press Ctrl+C to stop the server.\n")

    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
