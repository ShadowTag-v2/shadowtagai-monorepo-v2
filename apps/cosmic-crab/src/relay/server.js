const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

/**
 * ShadowTag Omega V7 Nervous System (Relay)
 * Simple WebSocket relay for real-time state synchronization.
 */
const state = {
  status: 'IDLE',
  lastAction: null,
  riskLevel: 'LOW',
  stagedFiles: [],
};

wss.on('connection', function connection(ws) {
  console.log('🔗 Sentinel Connected');

  // Send initial state
  ws.send(JSON.stringify({ type: 'INIT', payload: state }));

  ws.on('message', function message(data) {
    console.log('📩 received: %s', data);
    try {
      const action = JSON.parse(data);
      switch (action.type) {
        case 'UPDATE_STATUS':
          state.status = action.payload;
          break;
        case 'LOG_ACTION':
          state.lastAction = action.payload;
          break;
        case 'SET_RISK':
          state.riskLevel = action.payload;
          break;
        default:
          console.warn('❓ Unknown action type:', action.type);
      }

      // Broadcast state update
      const update = JSON.stringify({ type: 'STATE_REFRESH', payload: state });
      wss.clients.forEach(function each(client) {
        if (client.readyState === WebSocket.OPEN) {
          client.send(update);
        }
      });
    } catch (e) {
      console.error('❌ Error parsing message:', e);
    }
  });
});

console.log('⚡ Omega Relay running on ws://localhost:8080');
