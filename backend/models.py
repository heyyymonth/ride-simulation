from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import uuid

class DriverStatus(Enum):
    AVAILABLE = "available"
    ON_TRIP = "on_trip" 
    OFFLINE = "offline"

class RideStatus(Enum):
    WAITING = "waiting"
    ASSIGNED = "assigned"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Location:
    x: int
    y: int
    
    def distance_to(self, other: 'Location') -> int:
        """Manhattan distance calculation for ETA"""
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

@dataclass
class Driver:
    id: str
    name: str
    location: Location
    status: DriverStatus = DriverStatus.AVAILABLE
    current_ride_id: Optional[str] = None
    completed_rides: int = 0  # Track fairness - number of completed rides
    
    @classmethod
    def create_new(cls, name: str, location: Location):
        return cls(id=str(uuid.uuid4()), name=name, location=location, completed_rides=0)

@dataclass  
class Rider:
    id: str
    name: str
    pickup_location: Location
    dropoff_location: Location
    
    @classmethod
    def create_new(cls, name: str, pickup: Location, dropoff: Location):
        return cls(id=str(uuid.uuid4()), name=name, pickup_location=pickup, dropoff_location=dropoff)

@dataclass
class RideRequest:
    id: str
    rider_id: str
    pickup_location: Location
    dropoff_location: Location
    status: RideStatus = RideStatus.WAITING
    assigned_driver_id: Optional[str] = None
    rejected_by: List[str] = None
    pickup_completed: bool = False
    
    def __post_init__(self):
        if self.rejected_by is None:
            self.rejected_by = []
    
    @classmethod
    def create_new(cls, rider_id: str, pickup: Location, dropoff: Location):
        return cls(
            id=str(uuid.uuid4()),
            rider_id=rider_id,
            pickup_location=pickup,
            dropoff_location=dropoff
        )