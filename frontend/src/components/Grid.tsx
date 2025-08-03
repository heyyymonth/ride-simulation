// Minimal grid - simple div-based display, no canvas complexity
import React from 'react';
import { SystemState } from '../types';

interface GridProps {
  systemState: SystemState;
}

const Grid: React.FC<GridProps> = ({ systemState }) => {
  const { drivers, riders } = systemState;
  
  // Simple grid rendering - 20x20 visible (scaled from 100x100)
  const renderGrid = (): React.ReactElement[] => {
    const cells: React.ReactElement[] = [];
    const scale = 5; // Show every 5th cell (20x20 display)
    
    for (let y = 0; y < 100; y += scale) {
      for (let x = 0; x < 100; x += scale) {
        cells.push(
          <div
            key={`${x}-${y}`}
            className="grid-cell"
            style={{
              left: `${(x / scale) * 20}px`,
              top: `${(y / scale) * 20}px`
            }}
          />
        );
      }
    }
    return cells;
  };

  // Render drivers on grid
  const renderDrivers = (): React.ReactElement[] => {
    return drivers.map(driver => (
      <div
        key={driver.id}
        className={`entity driver ${driver.status}`}
        style={{
          left: `${(driver.location.x / 5) * 20}px`,
          top: `${(driver.location.y / 5) * 20}px`
        }}
        title={`Driver ${driver.id.slice(0, 8)} - ${driver.status}`}
      >
        🚗
      </div>
    ));
  };

  // Render riders on grid
  const renderRiders = (): React.ReactElement[] => {
    return riders.map(rider => (
      <div key={rider.id}>
        {/* Pickup location */}
        <div
          className="entity rider pickup"
          style={{
            left: `${(rider.pickup_location.x / 5) * 20}px`,
            top: `${(rider.pickup_location.y / 5) * 20}px`
          }}
          title={`${rider.name} - Pickup`}
        >
          🧍
        </div>
        {/* Dropoff location */}
        <div
          className="entity rider dropoff"
          style={{
            left: `${(rider.dropoff_location.x / 5) * 20}px`,
            top: `${(rider.dropoff_location.y / 5) * 20}px`
          }}
          title={`${rider.name} - Dropoff`}
        >
          📍
        </div>
      </div>
    ));
  };

  return (
    <div className="grid-container">
      <h3>City Grid (100x100)</h3>
      <div className="grid">
        {renderGrid()}
        {renderDrivers()}
        {renderRiders()}
      </div>
      <div className="legend">
        <span>🚗 Driver (Green=Available, Red=On Trip)</span>
        <span>🧍 Pickup Location</span>
        <span>📍 Dropoff Location</span>
      </div>
    </div>
  );
};

export default Grid;