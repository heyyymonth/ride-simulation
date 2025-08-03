from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import uuid
from datetime import datetime, timedelta

class DriverStatus(Enum):
    AVAILABLE = "available"
    ON_TRIP = "on_trip" 
    OFFLINE = "offline"

class RideStatus(Enum):
    WAITING = "waiting"
    PENDING_ACCEPTANCE = "pending_acceptance"  # Offered to a driver, awaiting response
    ASSIGNED = "assigned"  # Driver accepted, ride in progress
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
    last_ride_end_time: Optional[datetime] = None  # For idle time calculation
    recent_rides: List[datetime] = field(default_factory=list)  # Time-windowed ride history
    
    def get_idle_time_minutes(self) -> float:
        """Calculate idle time since last ride ended (in minutes)"""
        if self.last_ride_end_time is None:
            # Never had a ride, use a large idle time
            return 1000.0
        return (datetime.now() - self.last_ride_end_time).total_seconds() / 60.0
    
    def get_recent_rides_count(self, window_hours: int = 1) -> int:
        """Count rides in the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=window_hours)
        return sum(1 for ride_time in self.recent_rides if ride_time >= cutoff_time)
    
    @classmethod
    def create_new(cls, name: str, location: Location):
        return cls(
            id=str(uuid.uuid4()), 
            name=name, 
            location=location, 
            completed_rides=0,
            last_ride_end_time=None,
            recent_rides=[]
        )

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
    offered_to_driver_id: Optional[str] = None  # Driver currently being offered the ride
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