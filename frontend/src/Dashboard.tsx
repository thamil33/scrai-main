import React, { useState, useEffect } from 'react';
import MapComponent from './MapComponent';

// Let's keep using 'any' for now to stay focused on the map integration.
// We can come back and tighten up these types later.
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
    <div style={{ fontFamily: 'Arial, sans-serif' }}>
      <h1>scrAI Dashboard</h1>
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {data ? (
        <div>
          <h2>Agent Locations</h2>
          <MapComponent agents={data.agents} />
          <h2 style={{ marginTop: '20px' }}>Recent Memories</h2>
          <ul style={{ listStyleType: 'none', padding: 0 }}>
            {data.memories.map((memory, index) => (
              <li key={index} style={{ background: '#f0f0f0', margin: '5px 0', padding: '10px', borderRadius: '5px' }}>
                <strong>Agent {memory.agent_id}:</strong> {memory.description}
              </li>
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
