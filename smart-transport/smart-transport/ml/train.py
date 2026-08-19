"""
AI Traffic Congestion Prediction Model Trainer
Trains a machine learning regression model to predict future congestion levels (0-100%)
based on road, time of day, day of week, weather conditions, and preceding traffic patterns.
"""

import os
import pickle
import numpy as np

ROADS = [
    "OMR (IT Corridor)",
    "GST Road (Airport Corridor)",
    "ECR (East Coast Road)",
    "Mount Road (Anna Salai)",
    "Inner Ring Road (100 Ft Rd)",
    "Vandalur-Kelambakkam Road",
    "Velachery Main Road",
    "Poonamallee High Road",
    "Rajiv Gandhi Salai",
    "Pallavaram-Thoraipakkam Radial Rd"
]

WEATHER_TYPES = ["Clear", "Rainy", "Cloudy", "Foggy"]

def generate_features(samples=5000):
    np.random.seed(42)
    
    # Feature matrix: [bias, hour_peak1, hour_peak2, is_weekend, weather_rain, weather_fog, prev_congestion, road_bias]
    X_rows = []
    y_vals = []

    for _ in range(samples):
        road_idx = np.random.randint(0, len(ROADS))
        hour = np.random.randint(0, 24)
        day_of_week = np.random.randint(0, 7)
        is_weekend = 1.0 if day_of_week in [5, 6] else 0.0
        weather_idx = np.random.choice([0, 1, 2, 3], p=[0.65, 0.15, 0.15, 0.05])
        
        # Diurnal Peak activations (Morning rush 8-11, Evening rush 17-21)
        morning_peak = np.exp(-((hour - 9.5) ** 2) / 4.0)
        evening_peak = np.exp(-((hour - 18.5) ** 2) / 6.0)

        # Base congestion profile
        base = 25.0 + (48.0 * morning_peak) + (55.0 * evening_peak)
        
        if is_weekend:
            base = base * 0.7 + (15.0 * np.exp(-((hour - 20.0) ** 2) / 8.0))

        # Road bias
        road_bias = 0.0
        if road_idx in [0, 3, 7]: # OMR, Mount Road, Poonamallee
            road_bias = 12.0
        elif road_idx in [2, 5]: # ECR, Vandalur
            road_bias = -10.0

        rain_factor = 1.0 if weather_idx == 1 else 0.0
        fog_factor = 1.0 if weather_idx == 3 else 0.0

        prev_cong = np.clip(base + road_bias + np.random.normal(0, 4.0), 5.0, 95.0)

        # Target future congestion 1-hour ahead
        target = np.clip(base + road_bias + (rain_factor * 18.0) + (fog_factor * 8.0) + (prev_cong * 0.15) + np.random.normal(0, 3.5), 5.0, 99.0)

        feature_vector = [
            1.0, # Bias term
            morning_peak,
            evening_peak,
            is_weekend,
            rain_factor,
            fog_factor,
            prev_cong / 100.0,
            road_bias / 10.0
        ]

        X_rows.append(feature_vector)
        y_vals.append(target)

    return np.array(X_rows, dtype=np.float64), np.array(y_vals, dtype=np.float64)

def train_model():
    print("Generating synthetic traffic dataset for training...")
    X, y = generate_features(6000)

    # Train / Test Split
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    print("Training ML Traffic Regressor (Ridge Regression)...")
    # Analytical Ridge Regression: W = (X^T * X + lambda * I)^-1 * X^T * y
    lambda_reg = 0.01
    I = np.eye(X_train.shape[1])
    I[0, 0] = 0 # Do not regularize bias
    
    weights = np.linalg.inv(X_train.T @ X_train + lambda_reg * I) @ X_train.T @ y_train

    # Evaluate on test set
    y_pred = X_test @ weights
    mae = float(np.mean(np.abs(y_test - y_pred)))
    
    ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
    ss_res = np.sum((y_test - y_pred) ** 2)
    r2 = float(1.0 - (ss_res / ss_tot))

    print(f"Model Training Complete! MAE: {mae:.2f}%, R2 Score: {r2:.3f}")

    # Save artifact
    output_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(output_dir, 'traffic_model.pkl')
    
    bundle = {
        'weights': weights,
        'roads': ROADS,
        'weather_types': WEATHER_TYPES,
        'mae': round(mae, 2),
        'r2': round(r2, 3),
        'model_type': 'Ridge Regularized Traffic Regressor'
    }

    with open(model_path, 'wb') as f:
        pickle.dump(bundle, f)

    print(f"Saved traffic model successfully to: {model_path}")
    return model_path

if __name__ == '__main__':
    train_model()
