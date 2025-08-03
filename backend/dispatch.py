from typing import Optional, List
from models import Driver, Rider, RideRequest, DriverStatus, RideStatus
from storage import storage

def find_best_driver(request: RideRequest) -> Optional[Driver]:
    """
    Find the best available driver for a ride request.
    Algorithm: Closest driver by Manhattan distance (ETA optimization)
    """
    available_drivers = storage.get_available_drivers()
    
    # Filter out drivers who already rejected this request
    eligible_drivers = [
        driver for driver in available_drivers 
        if driver.id not in request.rejected_by
    ]
    
    if not eligible_drivers:
        return None
    
    # Find closest driver by Manhattan distance (Low ETA goal)
    best_driver = min(
        eligible_drivers,
        key=lambda d: d.location.distance_to(request.pickup_location)
    )
    
    return best_driver

def assign_driver_to_request(request: RideRequest, driver: Driver) -> bool:
    """Assign a driver to a ride request"""
    try:
        request.assigned_driver_id = driver.id
        request.status = RideStatus.ASSIGNED
        driver.status = DriverStatus.ON_TRIP
        driver.current_ride_id = request.id
        return True
    except Exception:
        return False

def handle_driver_rejection(request: RideRequest, driver_id: str) -> bool:
    """
    Handle driver rejection and implement fallback mechanism
    Returns True if can retry with another driver, False if max rejections reached
    """
    request.rejected_by.append(driver_id)
    
    # Reset driver status
    driver = storage.get_driver(driver_id)
    if driver:
        driver.status = DriverStatus.AVAILABLE
        driver.current_ride_id = None
    
    # Check if max rejections reached (fallback limit)
    MAX_REJECTIONS = 3
    if len(request.rejected_by) >= MAX_REJECTIONS:
        request.status = RideStatus.FAILED
        return False
    
    # Try to find another driver
    next_driver = find_best_driver(request)
    if next_driver:
        assign_driver_to_request(request, next_driver)
        return True
    else:
        request.status = RideStatus.FAILED
        return False

def process_ride_request(rider_id: str) -> Optional[RideRequest]:
    """
    Process a new ride request from a rider
    """
    rider = storage.get_rider(rider_id)
    if not rider:
        return None
    
    # Create ride request
    request = RideRequest.create_new(
        rider_id=rider_id,
        pickup=rider.pickup_location,
        dropoff=rider.dropoff_location
    )
    
    # Store the request
    storage.add_ride_request(request)
    
    # Try to assign a driver
    best_driver = find_best_driver(request)
    if best_driver:
        assign_driver_to_request(request, best_driver)
    else:
        request.status = RideStatus.FAILED
    
    return request