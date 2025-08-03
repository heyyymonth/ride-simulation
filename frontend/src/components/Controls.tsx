// Minimal controls - basic buttons, no complex UI
import React from 'react';
import { advanceTick } from '../services/api';

interface ControlsProps {
  onTick: () => void;
  currentTick: number;
}

const Controls: React.FC<ControlsProps> = ({ onTick, currentTick }) => {
  const handleTick = async (): Promise<void> => {
    try {
      await advanceTick();
      onTick(); // Refresh system state
    } catch (error: any) {
      alert('Failed to advance tick: ' + error.message);
    }
  };

  return (
    <div className="controls">
      <h3>Simulation Controls</h3>
      
      <div className="tick-control">
        <button onClick={handleTick} className="tick-button">
          ⏭️ Next Tick
        </button>
        <span className="tick-display">Current Tick: {currentTick}</span>
      </div>

      <div className="system-stats">
        <h4>Quick Stats</h4>
        <p>Use the tick button to advance simulation time</p>
        <p>Drivers move 1 unit per tick toward their destinations</p>
      </div>
    </div>
  );
};

export default Controls;