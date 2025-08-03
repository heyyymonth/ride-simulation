import React, { useState, useEffect } from 'react';
import { getActiveRides } from '../services/api';
import { ActiveRide } from '../types';

const ActiveRides: React.FC = () => {
  const [activeRides, setActiveRides] = useState<ActiveRide[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchActiveRides = async () => {
    try {
      const response = await getActiveRides();
      setActiveRides(response.active_rides);
      setLoading(false);
      setError(null);
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActiveRides();
    const interval = setInterval(fetchActiveRides, 2000); // Update every 2 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="active-rides-loading">Loading active rides...</div>;
  if (error) return <div className="active-rides-error">Error: {error}</div>;

  return (
    <div className="active-rides-container">
      <h3>🚖 Active Rides ({activeRides.length})</h3>
      
      {activeRides.length === 0 ? (
        <div className="no-active-rides">
          <p>No active rides at the moment</p>
          <span>🕐 Create drivers and riders, then request a ride to see activity here</span>
        </div>
      ) : (
        <div className="active-rides-list">
          {activeRides.map((ride) => (
            <div key={ride.ride_id} className="active-ride-card">
              <div className="ride-header">
                <span className="ride-id">Ride #{ride.ride_id.slice(0, 8)}</span>
                <span className={`ride-status ${ride.pickup_completed ? 'to-destination' : 'to-pickup'}`}>
                  {ride.pickup_completed ? 'TO DESTINATION' : 'TO PICKUP'}
                </span>
              </div>
              
              <div className="ride-details">
                <div className="participant driver-info">
                  <strong>🚗 Driver:</strong> {ride.driver.name}
                  <div className="location">
                    Current: ({ride.driver.location.x}, {ride.driver.location.y})
                  </div>
                  <div className="stats">
                    {ride.driver.completed_rides} completed rides
                  </div>
                </div>
                
                <div className="participant rider-info">
                  <strong>🧍 Rider:</strong> {ride.rider.name}
                  <div className="location">
                    Pickup: ({ride.pickup_location.x}, {ride.pickup_location.y})
                  </div>
                  <div className="location">
                    Destination: ({ride.dropoff_location.x}, {ride.dropoff_location.y})
                  </div>
                </div>
              </div>
              
              <div className="ride-progress">
                <div className="progress-bar">
                  <div 
                    className={`progress-fill ${ride.pickup_completed ? 'phase-two' : 'phase-one'}`}
                    style={{
                      width: ride.pickup_completed ? '75%' : '25%'
                    }}
                  ></div>
                </div>
                <div className="progress-text">
                  {ride.pickup_completed 
                    ? '🎯 En route to destination' 
                    : '📍 Picking up rider'}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ActiveRides;