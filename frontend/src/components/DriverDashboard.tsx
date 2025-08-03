import React, { useState, useEffect } from 'react';
import { getDriverPendingRides, acceptRide, rejectRide } from '../services/api';
import { Driver } from '../types';

interface DriverDashboardProps {
  drivers: Driver[];
  onRideAction: () => void; // Callback to refresh system state
}

interface PendingRide {
  ride_id: string;
  rider_id: string;
  pickup_location: { x: number; y: number };
  dropoff_location: { x: number; y: number };
  estimated_distance: number;
}

interface DriverPendingRides {
  driver_id: string;
  driver_name: string;
  pending_rides: PendingRide[];
}

const DriverDashboard: React.FC<DriverDashboardProps> = ({ drivers, onRideAction }) => {
  const [selectedDriverId, setSelectedDriverId] = useState<string>('');
  const [pendingRides, setPendingRides] = useState<DriverPendingRides | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null); // Track which ride is being processed

  const fetchPendingRides = async (driverId: string) => {
    if (!driverId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await getDriverPendingRides(driverId);
      setPendingRides(data);
    } catch (err: any) {
      setError(err.message);
      setPendingRides(null);
    } finally {
      setLoading(false);
    }
  };

  const handleDriverSelect = (driverId: string) => {
    setSelectedDriverId(driverId);
    fetchPendingRides(driverId);
  };

  const handleAcceptRide = async (rideId: string) => {
    if (!selectedDriverId) return;
    
    setActionLoading(rideId);
    try {
      await acceptRide(rideId, selectedDriverId);
      // Refresh pending rides and system state
      await fetchPendingRides(selectedDriverId);
      onRideAction();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setActionLoading(null);
    }
  };

  const handleRejectRide = async (rideId: string) => {
    if (!selectedDriverId) return;
    
    setActionLoading(rideId);
    try {
      await rejectRide(rideId, selectedDriverId);
      // Refresh pending rides and system state
      await fetchPendingRides(selectedDriverId);
      onRideAction();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setActionLoading(null);
    }
  };

  // Auto-refresh pending rides every 3 seconds for selected driver
  useEffect(() => {
    if (!selectedDriverId) return;
    
    const interval = setInterval(() => {
      fetchPendingRides(selectedDriverId);
    }, 3000);
    
    return () => clearInterval(interval);
  }, [selectedDriverId]);

  return (
    <div className="driver-dashboard">
      <h3>🚗 Driver Dashboard</h3>
      
      {/* Driver Selection */}
      <div className="driver-selection">
        <label htmlFor="driver-select">Select Driver:</label>
        <select 
          id="driver-select"
          value={selectedDriverId} 
          onChange={(e) => handleDriverSelect(e.target.value)}
          className="driver-select"
        >
          <option value="">-- Select a Driver --</option>
          {drivers.map(driver => (
            <option key={driver.id} value={driver.id}>
              {driver.name} - ({driver.location.x}, {driver.location.y}) - Status: {driver.status}
            </option>
          ))}
        </select>
      </div>

      {/* Error Display */}
      {error && (
        <div className="dashboard-error">
          <p>❌ Error: {error}</p>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="dashboard-loading">
          <p>🔄 Loading pending rides...</p>
        </div>
      )}

      {/* Pending Rides Display */}
      {pendingRides && !loading && (
        <div className="pending-rides-section">
          <h4>📋 Pending Rides for {pendingRides.driver_name}</h4>
          
          {pendingRides.pending_rides.length === 0 ? (
            <div className="no-pending-rides">
              <p>✅ No pending rides</p>
              <span>You're all caught up! New ride offers will appear here.</span>
            </div>
          ) : (
            <div className="pending-rides-list">
              {pendingRides.pending_rides.map((ride) => (
                <div key={ride.ride_id} className="pending-ride-card">
                  <div className="ride-info">
                    <div className="ride-header">
                      <span className="ride-id">Ride #{ride.ride_id.slice(0, 8)}</span>
                      <span className="distance-badge">{ride.estimated_distance} blocks away</span>
                    </div>
                    
                    <div className="ride-locations">
                      <div className="location">
                        <strong>📍 Pickup:</strong> ({ride.pickup_location.x}, {ride.pickup_location.y})
                      </div>
                      <div className="location">
                        <strong>🎯 Destination:</strong> ({ride.dropoff_location.x}, {ride.dropoff_location.y})
                      </div>
                    </div>
                  </div>
                  
                  <div className="ride-actions">
                    <button
                      onClick={() => handleAcceptRide(ride.ride_id)}
                      disabled={actionLoading === ride.ride_id}
                      className="accept-button"
                    >
                      {actionLoading === ride.ride_id ? '⏳' : '✅'} Accept
                    </button>
                    
                    <button
                      onClick={() => handleRejectRide(ride.ride_id)}
                      disabled={actionLoading === ride.ride_id}
                      className="reject-button"
                    >
                      {actionLoading === ride.ride_id ? '⏳' : '❌'} Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DriverDashboard;