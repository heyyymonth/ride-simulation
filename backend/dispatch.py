from typing import Optional, List
from models import Driver, Rider, RideRequest, DriverStatus, RideStatus
from storage import storage

def find_best_driver(request: RideRequest) -> Optional[Driver]:
    """
    Find the best available driver using normalized multi-factor scoring.
    Algorithm: Driver Score = α⋅Norm_ETA + β⋅Norm_Rides + γ⋅Norm_IdleTime
    Lower score = better choice
    """
    available_drivers = storage.get_available_drivers()
    
    # Filter out drivers who already rejected this request
    eligible_drivers = [
        driver for driver in available_drivers 
        if driver.id not in request.rejected_by
    ]
    
    if not eligible_drivers:
        return None
    
    if len(eligible_drivers) == 1:
        return eligible_drivers[0]
    
    # Calculate raw metrics for all drivers
    eta_values = []
    rides_values = []
    idle_values = []
    
    for driver in eligible_drivers:
        eta = driver.location.distance_to(request.pickup_location)  # Manhattan distance as ETA proxy
        recent_rides = driver.get_recent_rides_count(window_hours=1)  # Last hour
        idle_time = driver.get_idle_time_minutes()
        
        eta_values.append(eta)
        rides_values.append(recent_rides)
        idle_values.append(idle_time)
    
    # Normalize metrics (0-1 scale)
    def normalize_metric(values, reverse=False):
        if not values or min(values) == max(values):
            return [0.0] * len(values)
        
        min_val, max_val = min(values), max(values)
        normalized = [(v - min_val) / (max_val - min_val) for v in values]
        
        if reverse:  # For metrics where higher is better (idle time)
            normalized = [1.0 - n for n in normalized]
        
        return normalized
    
    norm_eta = normalize_metric(eta_values)  # Lower ETA is better (0 = best)
    norm_rides = normalize_metric(rides_values)  # Fewer recent rides is better (0 = best)
    norm_idle = normalize_metric(idle_values, reverse=True)  # More idle time is better (0 = best after reversal)
    
    # Scoring weights
    alpha = 0.6   # Distance priority
    beta = 0.25   # Fairness priority
    gamma = 0.15  # Idle time priority
    
    # Calculate composite scores
    driver_scores = []
    for i, driver in enumerate(eligible_drivers):
        score = (alpha * norm_eta[i]) + (beta * norm_rides[i]) + (gamma * norm_idle[i])
        driver_scores.append((score, driver, {
            'eta': eta_values[i],
            'recent_rides': rides_values[i], 
            'idle_minutes': idle_values[i],
            'norm_eta': norm_eta[i],
            'norm_rides': norm_rides[i],
            'norm_idle': norm_idle[i],
            'final_score': score
        }))
    
    # Sort by score (lowest wins) and return best driver
    best_score, best_driver, best_metrics = min(driver_scores, key=lambda x: x[0])
    
    # Log the selection for debugging (could be removed in production)
    print(f"🎯 Driver Selection: {best_driver.name} (Score: {best_score:.3f}) - ETA:{best_metrics['eta']}, Rides:{best_metrics['recent_rides']}, Idle:{best_metrics['idle_minutes']:.1f}min")
    
    return best_driver

def offer_ride_to_driver(request: RideRequest, driver: Driver) -> bool:
    """Offer a ride to a driver for acceptance/rejection"""
    try:
        request.offered_to_driver_id = driver.id
        request.status = RideStatus.PENDING_ACCEPTANCE
        return True
    except Exception:
        return False

def assign_driver_to_request(request: RideRequest, driver: Driver) -> bool:
    """Assign a driver to a ride request (after acceptance)"""
    try:
        request.assigned_driver_id = driver.id
        request.offered_to_driver_id = None  # Clear the offer
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
    
    # Offer ride to best available driver
    best_driver = find_best_driver(request)
    if best_driver:
        offer_ride_to_driver(request, best_driver)
        print(f"🔔 Ride offered to {best_driver.name} - waiting for response")
    else:
        request.status = RideStatus.FAILED
    
    return request

def accept_ride(driver_id: str, ride_request_id: str) -> dict:
    """Driver accepts a ride offer"""
    request = storage.get_ride_request(ride_request_id)
    driver = storage.get_driver(driver_id)
    
    if not request or not driver:
        return {"success": False, "error": "Invalid request or driver"}
    
    if request.status != RideStatus.PENDING_ACCEPTANCE:
        return {"success": False, "error": "Ride is not pending acceptance"}
    
    if request.offered_to_driver_id != driver_id:
        return {"success": False, "error": "Ride was not offered to this driver"}
    
    # Accept the ride
    assign_driver_to_request(request, driver)
    print(f"✅ {driver.name} accepted ride {ride_request_id[:8]}")
    
    return {"success": True, "message": f"Ride accepted by {driver.name}"}

def reject_ride(driver_id: str, ride_request_id: str) -> dict:
    """Driver rejects a ride offer"""
    request = storage.get_ride_request(ride_request_id)
    driver = storage.get_driver(driver_id)
    
    if not request or not driver:
        return {"success": False, "error": "Invalid request or driver"}
    
    if request.status != RideStatus.PENDING_ACCEPTANCE:
        return {"success": False, "error": "Ride is not pending acceptance"}
    
    if request.offered_to_driver_id != driver_id:
        return {"success": False, "error": "Ride was not offered to this driver"}
    
    # Reject the ride and try next driver
    request.offered_to_driver_id = None
    request.status = RideStatus.WAITING
    print(f"❌ {driver.name} rejected ride {ride_request_id[:8]}")
    
    # Add to rejected list
    request.rejected_by.append(driver_id)
    
    # Check if max rejections reached
    MAX_REJECTIONS = 3
    if len(request.rejected_by) >= MAX_REJECTIONS:
        request.status = RideStatus.FAILED
        return {"success": True, "message": "Ride failed - too many rejections"}
    
    # Try to find another driver
    next_driver = find_best_driver(request)
    if next_driver:
        offer_ride_to_driver(request, next_driver)
        print(f"🔔 Ride re-offered to {next_driver.name}")
        return {"success": True, "message": f"Ride rejected by {driver.name}, offered to {next_driver.name}"}
    else:
        request.status = RideStatus.FAILED
        return {"success": True, "message": "Ride failed - no more available drivers"}