"""
Shipment Delay Prediction Model.
Predicts the probability of shipment delays based on transit distance, mode, weather, and congestion.
"""

import numpy as np
from typing import Dict, Any
from sklearn.ensemble import GradientBoostingClassifier
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from python.utils.logger import get_logger

logger = get_logger("ShipmentDelayPredictor")

class ShipmentDelayPredictor:
    def __init__(self):
        self.model = GradientBoostingClassifier(n_estimators=40, random_state=42)
        self._train_baseline()

    def _train_baseline(self):
        # Features: [distance_km, mode_code (0:Air, 1:Road, 2:Sea), weather_risk (0-1), port_congestion (0-1)]
        X = np.random.uniform(100, 10000, size=(150, 4))
        y = (X[:, 2] + X[:, 3] > 1.0).astype(int)
        self.model.fit(X, y)

    def predict_delay_risk(self, shipment_id: str, transport_mode: str = "Sea", distance_km: float = 3500.0, weather_severity: float = 0.4, port_congestion: float = 0.6) -> Dict[str, Any]:
        mode_map = {"Air": 0, "Road": 1, "Sea": 2, "Rail": 3}
        mode_code = mode_map.get(transport_mode, 2)
        
        features = np.array([[distance_km, mode_code, weather_severity, port_congestion]])
        prob = round(float(self.model.predict_proba(features)[0][1]), 2)
        prob_pct = round(prob * 100.0, 1)
        
        risk_level = "LOW"
        if prob_pct > 80.0:
            risk_level = "CRITICAL"
        elif prob_pct > 60.0:
            risk_level = "HIGH"
        elif prob_pct > 30.0:
            risk_level = "MEDIUM"

        return {
            "shipment_id": shipment_id,
            "delay_probability_pct": prob_pct,
            "risk_level": risk_level,
            "key_factors": {
                "transport_mode": transport_mode,
                "weather_severity": weather_severity,
                "port_congestion": port_congestion
            }
        }

if __name__ == "__main__":
    predictor = ShipmentDelayPredictor()
    res = predictor.predict_delay_risk("SHIP_10025", transport_mode="Sea", weather_severity=0.8, port_congestion=0.7)
    print(f"Shipment Delay Prediction: {res}")
