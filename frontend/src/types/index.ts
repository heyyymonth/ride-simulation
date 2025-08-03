// TypeScript type definitions matching backend models
export interface Location {
  x: number;
  y: number;
}

export interface Driver {
  id: string;
  location: Location;
  status: 'available' | 'on_trip' | 'offline';
  current_ride_id: string | null;
}

export interface Rider {
  id: string;
  pickup_location: Location;
  dropoff_location: Location;
}

export interface RideRequest {
  id: string;
  rider_id: string;
  status: 'waiting' | 'assigned' | 'rejected' | 'completed' | 'failed';
  assigned_driver_id: string | null;
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