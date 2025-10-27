import React, { useState, useEffect } from 'react';

// Temporary interfaces, we'll refine these later
interface Agent {
  [key: string]: any;
}

interface Memory {
  [key: string]: any;
}

interface DashboardData {
  agents: Agent[];
  memories: Memory[];
}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/dashboard');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        setData(result);
      } catch (e) {
        if (e instanceof Error) {
          setError(e.message);
        } else {
          setError('An unknown error occurred.');
        }
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {data ? (
        <div>
          <h2>Agents</h2>
          <ul>
            {data.agents.map((agent, index) => (
              <li key={index}>{JSON.stringify(agent, null, 2)}</li>
            ))}
          </ul>
          <h2>Recent Memories</h2>
          <ul>
            {data.memories.map((memory, index) => (
              <li key={index}>{JSON.stringify(memory, null, 2)}</li>
            ))}
          </ul>
        </div>
      ) : (
        <p>Loading dashboard data...</p>
      )}
    </div>
  );
};

export default Dashboard;
