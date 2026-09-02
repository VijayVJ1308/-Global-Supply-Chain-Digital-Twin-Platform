"""
Enterprise Supply Chain Risk Engine.
Computes a normalized composite risk score (0-100) across 6 dimensions:
- Supplier Risk
- Transportation Risk
- Weather Risk
- Inventory Risk
- Geopolitical Risk
- Demand Risk
"""

from typing import Dict, Any, List

class SupplyChainRiskEngine:
    def __init__(self):
        # Weights for the 6 risk dimensions (Sum = 1.0)
        self.weights = {
            "supplier": 0.20,
            "transportation": 0.20,
            "weather": 0.15,
            "inventory": 0.20,
            "geopolitical": 0.15,
            "demand": 0.10
        }

    def compute_composite_risk(
        self,
        supplier_risk: float = 25.0,
        transportation_risk: float = 40.0,
        weather_risk: float = 30.0,
        inventory_risk: float = 20.0,
        geopolitical_risk: float = 15.0,
        demand_risk: float = 20.0
    ) -> Dict[str, Any]:
        
        composite_score = round(
            supplier_risk * self.weights["supplier"] +
            transportation_risk * self.weights["transportation"] +
            weather_risk * self.weights["weather"] +
            inventory_risk * self.weights["inventory"] +
            geopolitical_risk * self.weights["geopolitical"] +
            demand_risk * self.weights["demand"], 1
        )
        
        # Categorize risk level: 0-30 LOW, 31-60 MEDIUM, 61-80 HIGH, 81-100 CRITICAL
        if composite_score > 80.0:
            level = "CRITICAL"
        elif composite_score > 60.0:
            level = "HIGH"
        elif composite_score > 30.0:
            level = "MEDIUM"
        else:
            level = "LOW"
            
        return {
            "composite_risk_score": composite_score,
            "risk_level": level,
            "dimension_breakdown": {
                "supplier_risk": supplier_risk,
                "transportation_risk": transportation_risk,
                "weather_risk": weather_risk,
                "inventory_risk": inventory_risk,
                "geopolitical_risk": geopolitical_risk,
                "demand_risk": demand_risk
            }
        }

if __name__ == "__main__":
    engine = SupplyChainRiskEngine()
    score = engine.compute_composite_risk(supplier_risk=65.0, transportation_risk=75.0, weather_risk=80.0)
    print(f"Risk Score Result: {score}")
