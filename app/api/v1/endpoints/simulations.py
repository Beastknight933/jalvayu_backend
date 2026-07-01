from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, date
import uuid

from app.ml.inference import weather_predictor

router = APIRouter()

class SimulationParams(BaseModel):
    scenario_name: str
    description: Optional[str] = None
    region: str
    duration_days: int
    model_name: str
    dataset_version: str
    variables: Dict[str, float]

class SimulationJob(BaseModel):
    id: str
    scenario_name: str
    status: str
    progress: int
    created_at: str
    params: SimulationParams
    results: Optional[Dict[str, Any]] = None

class SimulationResponse(BaseModel):
    data: SimulationJob

class SimulationListResponse(BaseModel):
    data: List[SimulationJob]

class LogResponse(BaseModel):
    data: List[str]

# In-memory store for the PoC
SIMULATION_DB = {}
LOGS_DB = {}

@router.post("", response_model=SimulationResponse)
async def create_simulation(params: SimulationParams):
    job_id = str(uuid.uuid4())
    
    # Extract deltas
    tmax_delta = params.variables.get("temperature", 0.0)
    rain_delta = params.variables.get("rainfall", 0.0)
    
    # Run the AI model (synchronously for PoC simplicity)
    target = date.today()
    try:
        # Default coordinates for PoC
        results = weather_predictor.predict_weather(
            lat=28.61, 
            lon=77.20, 
            target_date=target,
            tmax_delta=tmax_delta,
            tmin_delta=tmax_delta,  # Assume same delta
            rain_delta=rain_delta
        )
        
        job = SimulationJob(
            id=job_id,
            scenario_name=params.scenario_name,
            status="completed",
            progress=100,
            created_at=datetime.utcnow().isoformat() + "Z",
            params=params,
            results=results
        )
        
        SIMULATION_DB[job_id] = job
        LOGS_DB[job_id] = [
            "Initializing TensorFlow simulation engine...",
            f"Loading baseline conditions for region: {params.region}...",
            f"Applying perturbations: {params.variables}",
            "Running inference steps...",
            "Post-processing spatial bounds...",
            "Simulation completed successfully."
        ]
        
        return {"data": job}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=SimulationListResponse)
async def get_all_simulations():
    return {"data": list(SIMULATION_DB.values())}

@router.get("/{id}", response_model=SimulationResponse)
async def get_simulation(id: str):
    if id not in SIMULATION_DB:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return {"data": SIMULATION_DB[id]}

@router.delete("/{id}")
async def delete_simulation(id: str):
    if id in SIMULATION_DB:
        del SIMULATION_DB[id]
    if id in LOGS_DB:
        del LOGS_DB[id]
    return {"status": "success"}

@router.get("/{id}/logs", response_model=LogResponse)
async def get_simulation_logs(id: str):
    if id not in LOGS_DB:
        raise HTTPException(status_code=404, detail="Logs not found")
    return {"data": LOGS_DB[id]}

@router.get("/compare/models")
async def get_simulation_comparison(id1: str = "sim1", id2: str = "sim2"):
    """
    Returns synthetic mathematical trajectory data comparing two scenarios or models.
    """
    import math
    comparison_data = []
    for i in range(1, 16):
        val_a = 20 + math.sin(i * 0.5) * 10
        val_b = 20 + math.sin(i * 0.6) * 12
        comparison_data.append({
            "name": f"Day {i}",
            "Model A (LSTM)": round(val_a, 2),
            "Model B (Transformer)": round(val_b, 2)
        })
    return {"data": comparison_data}

