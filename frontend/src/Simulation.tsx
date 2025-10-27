import React, { useState, useEffect } from 'react';

interface SimulationState {
  // Define the structure of your simulation state here
  // For now, we'll just display the raw JSON
  [key: string]: any;
}

const Simulation: React.FC = () => {
  const [simulationState, setSimulationState] = useState<SimulationState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const startSimulation = async () => {
      try {
        const response = await fetch('/api/simulation/start', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setSimulationState(data);
      } catch (e) {
        if (e instanceof Error) {
          setError(e.message);
        } else {
          setError('An unknown error occurred.');
        }
      }
    };

    startSimulation();
  }, []);

  return (
    <div>
      <h2>Simulation State</h2>
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {simulationState ? (
        <pre>{JSON.stringify(simulationState, null, 2)}</pre>
      ) : (
        <p>Loading simulation state...</p>
      )}
    </div>
  );
};

export default Simulation;
