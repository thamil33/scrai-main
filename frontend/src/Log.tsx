import React, { useState, useEffect } from 'react';

interface Event {
  // Define the structure of your event data here
  // For now, we'll just display the raw JSON
  [key: string]: any;
}

const Log: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch('/api/events');

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setEvents(data);
      } catch (e) {
        if (e instanceof Error) {
          setError(e.message);
        } else {
          setError('An unknown error occurred.');
        }
      }
    };

    const interval = setInterval(fetchEvents, 1000); // Fetch events every second

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2>Event Log</h2>
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {events.length > 0 ? (
        <ul>
          {events.map((event, index) => (
            <li key={index}>
              <pre>{JSON.stringify(event, null, 2)}</pre>
            </li>
          ))}
        </ul>
      ) : (
        <p>No events yet...</p>
      )}
    </div>
  );
};

export default Log;
