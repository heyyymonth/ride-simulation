// Typed API service - direct integration with tested backend
import { SystemState, TickResponse, Driver, Rider, RideRequest, ActiveRide } from '../types';

const API_BASE = 'http://localhost:8000';

// Driver Management (tested ✅)
export const createDriver = async (name: string, x: number, y: number): Promise<Driver> => {
  const response = await fetch(`${API_BASE}/drivers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: name, location: { x, y } })
  });
  if (!response.ok) throw new Error('Failed to create driver');
  return response.json();
};

export const deleteDriver = async (driverId: string): Promise<{ message: string }> => {
  const response = await fetch(`${API_BASE}/drivers/${driverId}`, {
    method: 'DELETE'
  });
  if (!response.ok) throw new Error('Failed to delete driver');
  return response.json();
};

// Rider Management (tested ✅)
export const createRider = async (
  name: string,
  pickupX: number, 
  pickupY: number, 
  dropoffX: number, 
  dropoffY: number
): Promise<Rider> => {
  const response = await fetch(`${API_BASE}/riders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: name,
      pickup_location: { x: pickupX, y: pickupY },
      dropoff_location: { x: dropoffX, y: dropoffY }
    })
  });
  if (!response.ok) throw new Error('Failed to create rider');
  return response.json();
};

export const deleteRider = async (riderId: string): Promise<{ message: string }> => {
  const response = await fetch(`${API_BASE}/riders/${riderId}`, {
    method: 'DELETE'
  });
  if (!response.ok) throw new Error('Failed to delete rider');
  return response.json();
};

export const getRiders = async (): Promise<{ riders: Rider[] }> => {
  const response = await fetch(`${API_BASE}/riders`);
  if (!response.ok) throw new Error('Failed to get riders');
  return response.json();
};

// Ride Operations (tested ✅)
export const requestRide = async (riderId: string): Promise<RideRequest> => {
  const response = await fetch(`${API_BASE}/rides/request`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rider_id: riderId })
  });
  if (!response.ok) throw new Error('Failed to request ride');
  return response.json();
};

// Simulation Control (tested ✅)
export const advanceTick = async (): Promise<TickResponse> => {
  const response = await fetch(`${API_BASE}/tick`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to advance tick');
  return response.json();
};

// System State (tested ✅)
export const getSystemState = async (): Promise<SystemState> => {
  const response = await fetch(`${API_BASE}/state`);
  if (!response.ok) throw new Error('Failed to get system state');
  return response.json();
};

// Active Rides Management
export const getActiveRides = async (): Promise<{ active_rides: ActiveRide[] }> => {
  const response = await fetch(`${API_BASE}/active-rides`);
  if (!response.ok) throw new Error('Failed to get active rides');
  return response.json();
};

// Driver Ride Management
export const getDriverPendingRides = async (driverId: string): Promise<{
  driver_id: string;
  driver_name: string;
  pending_rides: Array<{
    ride_id: string;
    rider_id: string;
    pickup_location: { x: number; y: number };
    dropoff_location: { x: number; y: number };
    estimated_distance: number;
  }>;
}> => {
  const response = await fetch(`${API_BASE}/drivers/${driverId}/pending-rides`);
  if (!response.ok) throw new Error('Failed to get driver pending rides');
  return response.json();
};

export const acceptRide = async (rideId: string, driverId: string): Promise<{ message: string; status: string }> => {
  const response = await fetch(`${API_BASE}/rides/${rideId}/accept`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ driver_id: driverId })
  });
  if (!response.ok) throw new Error('Failed to accept ride');
  return response.json();
};

export const rejectRide = async (rideId: string, driverId: string): Promise<{ message: string; status: string }> => {
  const response = await fetch(`${API_BASE}/rides/${rideId}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ driver_id: driverId })
  });
  if (!response.ok) throw new Error('Failed to reject ride');
  return response.json();
};