import React, { useState } from 'react';
import { CriticalTile } from './components/CriticalTile';
import './index.css';

function App() {
  const [activeTileIndex, setActiveTileIndex] = useState(0);

  // Mock data pulled from the Zero-Trust PostGIS backend
  const tiles = [
    {
      imperativeAction: 'FILE',
      matterName: 'Stark v. Rogers',
      deadlineIso: '2026-04-15T17:00:00Z',
      ruleCitation: 'FRCP Rule 12(a)(1)(a)(i)',
      intensityLevel: 'no-slack' as const,
    },
    {
      imperativeAction: 'REVIEW',
      matterName: 'Wayne Enterprises Merger',
      deadlineIso: '2026-04-20T12:00:00Z',
      ruleCitation: 'INTERNAL SLA',
      intensityLevel: 'moderate' as const,
    },
  ];

  const handleTap = () => {
    // Escalate or route to the exact workflow (e.g opening drafted document)
    // NY SB S7263 compliance: Route the human, do not generate human advice.
    if (activeTileIndex < tiles.length - 1) {
      setActiveTileIndex(activeTileIndex + 1);
    } else {
      setActiveTileIndex(0); // Reset for demo purposes
    }
  };

  const currentTile = tiles[activeTileIndex];

  return (
    <div className="min-h-screen bg-black text-white w-full h-full overflow-hidden">
      <CriticalTile
        imperativeAction={currentTile.imperativeAction}
        matterName={currentTile.matterName}
        deadlineIso={currentTile.deadlineIso}
        ruleCitation={currentTile.ruleCitation}
        intensityLevel={currentTile.intensityLevel}
        onTap={handleTap}
      />
    </div>
  );
}

export default App;
