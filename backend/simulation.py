from models import Driver, RideRequest, DriverStatus, RideStatus, Location
from storage import storage

def advance_simulation_tick() -> dict:
    """
    Advance simulation by one tick and update all driver positions
    Returns updated system state
    """
    # Increment tick counter
    current_tick = storage.advance_tick()
    
    # Move all drivers who are on trips
    active_drivers = [d for d in storage.get_all_drivers() if d.status == DriverStatus.ON_TRIP]
    
    for driver in active_drivers:
        move_driver_one_step(driver)
    
    return {
        "current_tick": current_tick,
        "moved_drivers": len(active_drivers),
        "system_state": storage.get_system_state()
    }

def move_driver_one_step(driver: Driver):
    """
    Move driver one unit toward their destination (pickup first, then dropoff)
    Movement: exactly one unit per tick as per requirements
    Phase 1: Driver moves alone to pickup location
    Phase 2: Driver + Rider move together to dropoff location
    """
    if not driver.current_ride_id:
        return
    
    ride_request = storage.get_ride_request(driver.current_ride_id)
    if not ride_request:
        return
    
    # Determine target location (pickup first, then dropoff)
    if not ride_request.pickup_completed:
        target = ride_request.pickup_location
        is_pickup_phase = True
    else:
        target = ride_request.dropoff_location
        is_pickup_phase = False
    
    # Move one step toward target using Manhattan movement
    new_location = calculate_next_position(driver.location, target)
    driver.location = new_location
    
    # If rider has been picked up, move rider with driver
    if ride_request.pickup_completed:
        rider = storage.get_rider(ride_request.rider_id)
        if rider:
            rider.pickup_location = driver.location
    
    # Check if reached destination
    if driver.location == target:
        handle_destination_reached(driver, ride_request, is_pickup_phase)

def calculate_next_position(current: Location, target: Location) -> Location:
    """
    Calculate next position moving one unit toward target
    Uses Manhattan distance movement (horizontal first, then vertical)
    """
    new_x, new_y = current.x, current.y
    
    # Move horizontally first
    if new_x < target.x:
        new_x += 1
    elif new_x > target.x:
        new_x -= 1
    # If x matches, move vertically
    elif new_y < target.y:
        new_y += 1
    elif new_y > target.y:
        new_y -= 1
    
    return Location(new_x, new_y)

def handle_destination_reached(driver: Driver, request: RideRequest, is_pickup_phase: bool):
    """
    Handle when driver reaches pickup or dropoff location
    """
    if is_pickup_phase:
        # Reached pickup - passenger picked up, rider now moves with driver
        request.pickup_completed = True  # Mark pickup as completed
        rider = storage.get_rider(request.rider_id)
        if rider:
            # Update rider's current location to match driver (rider is now in the car)
            rider.pickup_location = driver.location
        # Driver continues moving toward dropoff with rider
        
    else:
        # Reached dropoff - trip completed, drop off rider
        rider = storage.get_rider(request.rider_id)
        if rider:
            # Update rider's final location to dropoff
            rider.pickup_location = driver.location  # Rider's final location
            
            # Remove rider from system - trip is complete
            storage.remove_rider(request.rider_id)
            
        # Complete the trip
        request.status = RideStatus.COMPLETED
        driver.status = DriverStatus.AVAILABLE
        driver.current_ride_id = None

def get_simulation_state() -> dict:
    """Get current simulation state for frontend"""
    return storage.get_system_state()