from typing import Dict, List, Optional
from models import Driver, Rider, RideRequest, DriverStatus, RideStatus

class InMemoryStorage:
    def __init__(self):
        self.drivers: Dict[str, Driver] = {}
        self.riders: Dict[str, Rider] = {}
        self.ride_requests: Dict[str, RideRequest] = {}
        self.current_tick: int = 0
    
    # Driver operations
    def add_driver(self, driver: Driver) -> Driver:
        self.drivers[driver.id] = driver
        return driver
    
    def get_driver(self, driver_id: str) -> Optional[Driver]:
        return self.drivers.get(driver_id)
    
    def get_all_drivers(self) -> List[Driver]:
        return list(self.drivers.values())
    
    def remove_driver(self, driver_id: str) -> bool:
        if driver_id in self.drivers:
            del self.drivers[driver_id]
            return True
        return False
    
    def get_available_drivers(self) -> List[Driver]:
        return [d for d in self.drivers.values() if d.status == DriverStatus.AVAILABLE]
    
    # Rider operations
    def add_rider(self, rider: Rider) -> Rider:
        self.riders[rider.id] = rider
        return rider
    
    def get_rider(self, rider_id: str) -> Optional[Rider]:
        return self.riders.get(rider_id)
    
    def get_all_riders(self) -> List[Rider]:
        return list(self.riders.values())
    
    def remove_rider(self, rider_id: str) -> bool:
        if rider_id in self.riders:
            del self.riders[rider_id]
            return True
        return False
    
    # RideRequest operations
    def add_ride_request(self, request: RideRequest) -> RideRequest:
        self.ride_requests[request.id] = request
        return request
    
    def get_ride_request(self, request_id: str) -> Optional[RideRequest]:
        return self.ride_requests.get(request_id)
    
    def get_all_ride_requests(self) -> List[RideRequest]:
        return list(self.ride_requests.values())
    
    def get_pending_requests(self) -> List[RideRequest]:
        return [r for r in self.ride_requests.values() if r.status == RideStatus.WAITING]
    
    # Simulation state
    def advance_tick(self) -> int:
        self.current_tick += 1
        return self.current_tick
    
    def get_current_tick(self) -> int:
        return self.current_tick
    
    def get_system_state(self) -> dict:
        return {
            "drivers": list(self.drivers.values()),
            "riders": list(self.riders.values()),
            "ride_requests": list(self.ride_requests.values()),
            "current_tick": self.current_tick
        }

# Global storage instance
storage = InMemoryStorage()