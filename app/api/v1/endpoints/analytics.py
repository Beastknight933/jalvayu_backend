from fastapi import APIRouter
from typing import Dict, Any, List

router = APIRouter()

@router.get("")
async def get_analytics_data() -> Dict[str, Any]:
    """
    Returns synthetic, mathematically generated analytics data for the dashboard.
    """
    import math

    # Trend Data (Rainfall)
    trend_data = [
        {"name": "Jan", "value": 15.0 + math.sin(0) * 10},
        {"name": "Feb", "value": 20.0 + math.sin(1) * 10},
        {"name": "Mar", "value": 35.0 + math.sin(2) * 15},
        {"name": "Apr", "value": 55.0 + math.sin(3) * 20},
        {"name": "May", "value": 110.0 + math.sin(4) * 30},
        {"name": "Jun", "value": 280.0 + math.sin(5) * 50},
        {"name": "Jul", "value": 350.0 + math.sin(6) * 60},
        {"name": "Aug", "value": 310.0 + math.sin(7) * 50},
        {"name": "Sep", "value": 190.0 + math.sin(8) * 30},
        {"name": "Oct", "value": 80.0 + math.sin(9) * 20},
        {"name": "Nov", "value": 30.0 + math.sin(10) * 10},
        {"name": "Dec", "value": 15.0 + math.sin(11) * 5},
    ]

    # Anomaly Data (Temperature)
    anomaly_data = [
        {"name": "North", "value": -0.5},
        {"name": "South", "value": 1.2},
        {"name": "East", "value": 0.3},
        {"name": "West", "value": -0.8},
        {"name": "Central", "value": 1.5},
    ]

    # Heatmap Data (Seasonal Extremes Intensity 0-1)
    heatmap_data = [
        {"x": "2020", "y": "Summer", "value": 0.82},
        {"x": "2021", "y": "Summer", "value": 0.88},
        {"x": "2022", "y": "Summer", "value": 0.95},
        {"x": "2020", "y": "Monsoon", "value": 0.45},
        {"x": "2021", "y": "Monsoon", "value": 0.62},
        {"x": "2022", "y": "Monsoon", "value": 0.74},
        {"x": "2020", "y": "Winter", "value": 0.25},
        {"x": "2021", "y": "Winter", "value": 0.18},
        {"x": "2022", "y": "Winter", "value": 0.30},
    ]

    return {
        "data": {
            "trend": trend_data,
            "anomaly": anomaly_data,
            "heatmap": heatmap_data
        }
    }
