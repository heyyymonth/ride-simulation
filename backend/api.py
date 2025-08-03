from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from models import Driver, Rider, RideRequest, Location, DriverStatus, RideStatus
from storage import storage
from dispatch import process_ride_request, handle_driver_rejection, accept_ride, reject_ride
from simulation import advance_simulation_tick, get_simulation_state

router = APIRouter()

# Pydantic models for request/response
class LocationModel(BaseModel):
    x: int
    y: int

class CreateDriverRequest(BaseModel):
    name: str
    location: LocationModel

class CreateRiderRequest(BaseModel):
    name: str
    pickup_location: LocationModel
    dropoff_location: LocationModel

class RideRequestModel(BaseModel):
    rider_id: str

class DriverActionRequest(BaseModel):
    driver_id: str

# Driver Management Endpoints
@router.post("/drivers", response_model=dict)
async def create_driver(request: CreateDriverRequest):
    """Create a new driver with name and location"""
    location = Location(x=request.location.x, y=request.location.y)
    
    # Validate grid bounds (100x100)
    if not (0 <= location.x < 100 and 0 <= location.y < 100):
        raise HTTPException(status_code=400, detail="Location must be within 100x100 grid")
    
    driver = Driver.create_new(request.name, location)
    storage.add_driver(driver)
    
    return {
        "id": driver.id,
        "name": driver.name,
        "location": {"x": driver.location.x, "y": driver.location.y},
        "status": driver.status.value,
        "completed_rides": driver.completed_rides,
        "message": "Driver created successfully"
    }

@router.delete("/drivers/{driver_id}")
async def delete_driver(driver_id: str):
    """Remove a driver from the system"""
    if storage.remove_driver(driver_id):
        return {"message": "Driver removed successfully"}
    else:
        raise HTTPException(status_code=404, detail="Driver not found")

@router.get("/drivers")
async def list_drivers():
    """Get all drivers"""
    drivers = storage.get_all_drivers()
    return {
        "drivers": [
            {
                "id": d.id,
                "name": d.name,
                "location": {"x": d.location.x, "y": d.location.y},
                "status": d.status.value,
                "current_ride_id": d.current_ride_id,
                "completed_rides": d.completed_rides,
                "idle_time_minutes": d.get_idle_time_minutes(),
                "recent_rides_count": d.get_recent_rides_count()
            } for d in drivers
        ]
    }

# Rider Management Endpoints
@router.post("/riders", response_model=dict)
async def create_rider(request: CreateRiderRequest):
    """Create a new rider with name, pickup and dropoff locations"""
    pickup = Location(x=request.pickup_location.x, y=request.pickup_location.y)
    dropoff = Location(x=request.dropoff_location.x, y=request.dropoff_location.y)
    
    # Validate grid bounds
    if not (0 <= pickup.x < 100 and 0 <= pickup.y < 100):
        raise HTTPException(status_code=400, detail="Pickup location must be within 100x100 grid")
    if not (0 <= dropoff.x < 100 and 0 <= dropoff.y < 100):
        raise HTTPException(status_code=400, detail="Dropoff location must be within 100x100 grid")
    
    rider = Rider.create_new(request.name, pickup, dropoff)
    storage.add_rider(rider)
    
    return {
        "id": rider.id,
        "name": rider.name,
        "pickup_location": {"x": rider.pickup_location.x, "y": rider.pickup_location.y},
        "dropoff_location": {"x": rider.dropoff_location.x, "y": rider.dropoff_location.y},
        "message": "Rider created successfully"
    }

@router.delete("/riders/{rider_id}")
async def delete_rider(rider_id: str):
    """Remove a rider from the system"""
    if storage.remove_rider(rider_id):
        return {"message": "Rider removed successfully"}
    else:
        raise HTTPException(status_code=404, detail="Rider not found")

@router.get("/riders")
async def list_riders():
    """Get all riders"""
    riders = storage.get_all_riders()
    return {
        "riders": [
            {
                "id": r.id,
                "pickup_location": {"x": r.pickup_location.x, "y": r.pickup_location.y},
                "dropoff_location": {"x": r.dropoff_location.x, "y": r.dropoff_location.y}
            } for r in riders
        ]
    }

# Ride Request Endpoints
@router.post("/rides/request", response_model=dict)
async def request_ride(request: RideRequestModel):
    """Create a ride request for a rider"""
    ride_request = process_ride_request(request.rider_id)
    
    if not ride_request:
        raise HTTPException(status_code=404, detail="Rider not found")
    
    return {
        "id": ride_request.id,
        "rider_id": ride_request.rider_id,
        "status": ride_request.status.value,
        "assigned_driver_id": ride_request.assigned_driver_id,
        "offered_to_driver_id": ride_request.offered_to_driver_id,
        "pickup_location": {"x": ride_request.pickup_location.x, "y": ride_request.pickup_location.y},
        "dropoff_location": {"x": ride_request.dropoff_location.x, "y": ride_request.dropoff_location.y},
        "message": "Ride request processed"
    }

@router.post("/rides/{request_id}/accept")
async def accept_ride_endpoint(request_id: str, action: DriverActionRequest):
    """Driver accepts a ride offer"""
    result = accept_ride(action.driver_id, request_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": result["message"], "status": "accepted"}

@router.post("/rides/{request_id}/reject")
async def reject_ride_endpoint(request_id: str, action: DriverActionRequest):
    """Driver rejects a ride offer (triggers fallback to next driver)"""
    result = reject_ride(action.driver_id, request_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": result["message"], "status": "rejected"}

@router.get("/drivers/{driver_id}/pending-rides")
async def get_driver_pending_rides(driver_id: str):
    """Get rides pending acceptance for a specific driver"""
    driver = storage.get_driver(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    pending_rides = storage.get_driver_pending_rides(driver_id)
    
    return {
        "driver_id": driver_id,
        "driver_name": driver.name,
        "pending_rides": [
            {
                "ride_id": ride.id,
                "rider_id": ride.rider_id,
                "pickup_location": {"x": ride.pickup_location.x, "y": ride.pickup_location.y},
                "dropoff_location": {"x": ride.dropoff_location.x, "y": ride.dropoff_location.y},
                "estimated_distance": driver.location.distance_to(ride.pickup_location)
            } for ride in pending_rides
        ]
    }

# Ride management endpoints

@router.get("/rides")
async def list_rides():
    """Get all ride requests"""
    requests = storage.get_all_ride_requests()
    return {
        "ride_requests": [
            {
                "id": r.id,
                "rider_id": r.rider_id,
                "status": r.status.value,
                "assigned_driver_id": r.assigned_driver_id,
                "offered_to_driver_id": r.offered_to_driver_id,
                "pickup_location": {"x": r.pickup_location.x, "y": r.pickup_location.y},
                "dropoff_location": {"x": r.dropoff_location.x, "y": r.dropoff_location.y},
                "rejected_by": r.rejected_by,
                "pickup_completed": r.pickup_completed
            } for r in requests
        ]
    }

# Simulation Endpoints
@router.post("/tick")
async def advance_tick():
    """Advance simulation by one tick"""
    result = advance_simulation_tick()
    return {
        "current_tick": result["current_tick"],
        "moved_drivers": result["moved_drivers"],
        "message": f"Advanced to tick {result['current_tick']}"
    }

@router.get("/state")
async def get_system_state():
    """Get current system state for frontend visualization"""
    state = get_simulation_state()
    
    # Convert to JSON-serializable format
    return {
        "drivers": [
            {
                "id": d.id,
                "name": d.name,
                "location": {"x": d.location.x, "y": d.location.y},
                "status": d.status.value,
                "current_ride_id": d.current_ride_id,
                "completed_rides": d.completed_rides,
                "idle_time_minutes": d.get_idle_time_minutes(),
                "recent_rides_count": d.get_recent_rides_count()
            } for d in state["drivers"]
        ],
        "riders": [
            {
                "id": r.id,
                "name": r.name,
                "pickup_location": {"x": r.pickup_location.x, "y": r.pickup_location.y},
                "dropoff_location": {"x": r.dropoff_location.x, "y": r.dropoff_location.y}
            } for r in state["riders"]
        ],
        "ride_requests": [
            {
                "id": req.id,
                "rider_id": req.rider_id,
                "status": req.status.value,
                "assigned_driver_id": req.assigned_driver_id,
                "offered_to_driver_id": req.offered_to_driver_id,
                "pickup_location": {"x": req.pickup_location.x, "y": req.pickup_location.y},
                "dropoff_location": {"x": req.dropoff_location.x, "y": req.dropoff_location.y},
                "rejected_by": req.rejected_by,
                "pickup_completed": req.pickup_completed
            } for req in state["ride_requests"]
        ],
        "current_tick": state["current_tick"]
    }

@router.get("/active-rides")
async def get_active_rides():
    """Get currently active rides with detailed driver and rider information"""
    state = get_simulation_state()
    
    active_rides = []
    for request in state["ride_requests"]:
        if request.status == RideStatus.ASSIGNED:
            # Find the assigned driver and rider
            driver = storage.get_driver(request.assigned_driver_id)
            rider = storage.get_rider(request.rider_id)
            
            if driver and rider:
                active_rides.append({
                    "ride_id": request.id,
                    "status": request.status.value,
                    "pickup_completed": request.pickup_completed,
                    "pickup_location": {"x": request.pickup_location.x, "y": request.pickup_location.y},
                    "dropoff_location": {"x": request.dropoff_location.x, "y": request.dropoff_location.y},
                    "driver": {
                        "id": driver.id,
                        "name": driver.name,
                        "location": {"x": driver.location.x, "y": driver.location.y},
                        "completed_rides": driver.completed_rides
                    },
                    "rider": {
                        "id": rider.id,
                        "name": rider.name,
                        "pickup_location": {"x": rider.pickup_location.x, "y": rider.pickup_location.y},
                        "dropoff_location": {"x": rider.dropoff_location.x, "y": rider.dropoff_location.y}
                    }
                })
    
    return {"active_rides": active_rides}

@router.get("/grid")
async def get_grid_data():
    """Get grid visualization data (alias for /state)"""
    return await get_system_state()