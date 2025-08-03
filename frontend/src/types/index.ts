// TypeScript type definitions matching backend models
export interface Location {
  x: number;
  y: number;
}

export interface Driver {
  id: string;
  name: string;
  location: Location;
  status: 'available' | 'on_trip' | 'offline';
  current_ride_id: string | null;
  completed_rides: number;
  idle_time_minutes: number;
  recent_rides_count: number;
}

export interface Rider {
  id: string;
  name: string;
  pickup_location: Location;
  dropoff_location: Location;
}

export interface RideRequest {
  id: string;
  rider_id: string;
  status: 'waiting' | 'pending_acceptance' | 'assigned' | 'rejected' | 'completed' | 'failed';
  assigned_driver_id: string | null;
  offered_to_driver_id: string | null;
  pickup_location: Location;
  dropoff_location: Location;
  rejected_by: string[];
  pickup_completed: boolean;
}

export interface SystemState {
  drivers: Driver[];
  riders: Rider[];
  ride_requests: RideRequest[];
  current_tick: number;
}

// API Response types
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
}

export interface TickResponse {
  current_tick: number;
  moved_drivers: number;
  message: string;
}

export interface ActiveRide {
  ride_id: string;
  status: string;
  pickup_completed: boolean;
  pickup_location: Location;
  dropoff_location: Location;
  driver: {
    id: string;
    name: string;
    location: Location;
    completed_rides: number;
  };
  rider: {
    id: string;
    name: string;
    pickup_location: Location;
    dropoff_location: Location;
  };
}