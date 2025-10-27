import React from 'react';
import Simulation from './Simulation';
import Log from './Log';

const App: React.FC = () => {
  return (
    <div>
      <h1>scrAI Simulation</h1>
      <Simulation />
      <Log />
    </div>
  );
};

export default App;
