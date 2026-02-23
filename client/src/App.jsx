import React, { useEffect } from 'react';
import { useSnapshot } from 'valtio';

import config from './config/config';
import state from './store';
import { ProfessionalRecommendations } from './pages';
import Home from "./pages/Home";

function App() {
  const snap = useSnapshot(state);
  return (
    <main className="app transition-all ease-in">
      <Home />
      {snap.view === "recs" && <ProfessionalRecommendations />}
    </main>
  );
}

export default App;
