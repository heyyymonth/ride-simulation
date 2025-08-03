// Minimal main component - no complex state management
import React, { useState, useEffect } from 'react';
import Grid from './components/Grid';
import Controls from './components/Controls';
import EntityForm from './components/EntityForm';
import ActiveRides from './components/ActiveRides';
import DriverDashboard from './components/DriverDashboard';
import { getSystemState } from './services/api';
import { SystemState } from './types';
import './App.css';

const App: React.FC = () => {
  const [systemState, setSystemState] = useState<SystemState>({
    drivers: [],
    riders: [],
    ride_requests: [],
    current_tick: 0
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Simple polling - refresh state every 2 seconds
  useEffect(() => {
    fetchSystemState(); // Initial load
    const interval = setInterval(fetchSystemState, 2000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemState = async (): Promise<void> => {
    try {
      const state = await getSystemState();
      setSystemState(state);
      setLoading(false);
      setError(null);
    } catch (err) {
      setError('Failed to connect to backend');
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="app">
      <h1>Ride Dispatch System</h1>
      <div className="main-content">
        <Grid systemState={systemState} />
        <div className="sidebar">
          <Controls 
            onTick={fetchSystemState}
            currentTick={systemState.current_tick}
          />
          <EntityForm 
            onEntityCreated={fetchSystemState}
            riders={systemState.riders}
            drivers={systemState.drivers}
          />
        </div>
      </div>
      <DriverDashboard 
        drivers={systemState.drivers}
        onRideAction={fetchSystemState}
      />
      <ActiveRides />
    </div>
  );
};

export default App;