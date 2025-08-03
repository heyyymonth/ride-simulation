// Minimal forms - basic HTML inputs, no validation libraries
import React, { useState } from 'react';
import { createDriver, createRider, requestRide } from '../services/api';
import { Rider } from '../types';

interface EntityFormProps {
  onEntityCreated: () => void;
  riders: Rider[];
}

interface DriverForm {
  x: string;
  y: string;
}

interface RiderForm {
  name: string;
  pickupX: string;
  pickupY: string;
  dropoffX: string;
  dropoffY: string;
}

const EntityForm: React.FC<EntityFormProps> = ({ onEntityCreated, riders }) => {
  const [driverForm, setDriverForm] = useState<DriverForm>({ x: '', y: '' });
  const [riderForm, setRiderForm] = useState<RiderForm>({ 
    name: '', pickupX: '', pickupY: '', dropoffX: '', dropoffY: '' 
  });
  const [selectedRiderId, setSelectedRiderId] = useState<string>('');

  // Driver operations
  const handleCreateDriver = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    try {
      await createDriver(Number(driverForm.x), Number(driverForm.y));
      setDriverForm({ x: '', y: '' });
      onEntityCreated();
    } catch (error: any) {
      alert('Failed to create driver: ' + error.message);
    }
  };

  // Rider operations
  const handleCreateRider = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    try {
      await createRider(
        riderForm.name,
        Number(riderForm.pickupX), Number(riderForm.pickupY),
        Number(riderForm.dropoffX), Number(riderForm.dropoffY)
      );
      setRiderForm({ name: '', pickupX: '', pickupY: '', dropoffX: '', dropoffY: '' });
      onEntityCreated();
    } catch (error: any) {
      alert('Failed to create rider: ' + error.message);
    }
  };

  // Ride request
  const handleRequestRide = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    if (!selectedRiderId) {
      alert('Please select a rider first');
      return;
    }
    try {
      await requestRide(selectedRiderId);
      setSelectedRiderId('');
      onEntityCreated();
    } catch (error: any) {
      alert('Failed to request ride: ' + error.message);
    }
  };

  return (
    <div className="entity-forms">
      <h3>Manage Entities</h3>

      {/* Add Driver Form */}
      <form onSubmit={handleCreateDriver} className="form-section">
        <h4>Add Driver</h4>
        <input
          type="number"
          placeholder="X (0-99)"
          min="0" max="99"
          value={driverForm.x}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
            setDriverForm({...driverForm, x: e.target.value})}
          required
        />
        <input
          type="number"
          placeholder="Y (0-99)"
          min="0" max="99"
          value={driverForm.y}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
            setDriverForm({...driverForm, y: e.target.value})}
          required
        />
        <button type="submit">Add Driver 🚗</button>
      </form>

      {/* Add Rider Form */}
      <form onSubmit={handleCreateRider} className="form-section">
        <h4>Add Rider</h4>
        <input
          type="text"
          placeholder="Rider Name"
          value={riderForm.name}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
            setRiderForm({...riderForm, name: e.target.value})}
          required
          style={{width: '100%', marginBottom: '10px'}}
        />
        <div className="location-inputs">
          <label>Pickup:</label>
          <input
            type="number"
            placeholder="X" min="0" max="99"
            value={riderForm.pickupX}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
              setRiderForm({...riderForm, pickupX: e.target.value})}
            required
          />
          <input
            type="number"
            placeholder="Y" min="0" max="99"
            value={riderForm.pickupY}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
              setRiderForm({...riderForm, pickupY: e.target.value})}
            required
          />
        </div>
        <div className="location-inputs">
          <label>Dropoff:</label>
          <input
            type="number"
            placeholder="X" min="0" max="99"
            value={riderForm.dropoffX}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
              setRiderForm({...riderForm, dropoffX: e.target.value})}
            required
          />
          <input
            type="number"
            placeholder="Y" min="0" max="99"
            value={riderForm.dropoffY}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
              setRiderForm({...riderForm, dropoffY: e.target.value})}
            required
          />
        </div>
        <button type="submit">Add Rider 🧍</button>
      </form>

      {/* Request Ride Form */}
      <form onSubmit={handleRequestRide} className="form-section">
        <h4>Request Ride</h4>
        {riders.length === 0 ? (
          <p className="no-riders">No riders available. Create a rider first.</p>
        ) : (
          <select
            value={selectedRiderId}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => 
              setSelectedRiderId(e.target.value)}
            required
            className="rider-dropdown"
          >
            <option value="">Select a rider...</option>
            {riders.map(rider => (
              <option key={rider.id} value={rider.id}>
                {rider.name} - From ({rider.pickup_location.x},{rider.pickup_location.y}) to ({rider.dropoff_location.x},{rider.dropoff_location.y})
              </option>
            ))}
          </select>
        )}
        <button type="submit" disabled={!selectedRiderId}>
          Request Ride 🚖
        </button>
      </form>
    </div>
  );
};

export default EntityForm;