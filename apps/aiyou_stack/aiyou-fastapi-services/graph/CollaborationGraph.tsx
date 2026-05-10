import React, { useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

export const CollaborationGraph = ({ data }) => {
  const fgRef = useRef();

  return (
    <div className="p-4 bg-slate-900 border border-slate-700 rounded-lg">
      <h3 className="text-blue-400 mb-4 font-mono">/// COLLABORATION_NETWORK ///</h3>
      <ForceGraph2D
        ref={fgRef}
        graphData={data}
        nodeLabel="id"
        nodeAutoColorBy="group"
        linkDirectionalParticles={2}
        height={400}
        width={700}
        nodeCanvasObject={(node, ctx, globalScale) => {
          if (node.id === 'antigravity_agent_01') {
            // Draw a glowing square for the Agent
            ctx.fillStyle = '#ff0034'; // High-Vis Red
            ctx.fillRect(node.x - 6, node.y - 6, 12, 12);
          } else {
            // Draw standard circles for Researchers
            ctx.beginPath();
            ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
            ctx.fillStyle = '#58a6ff';
            ctx.fill();
          }
        }}
      />
    </div>
  );
};
