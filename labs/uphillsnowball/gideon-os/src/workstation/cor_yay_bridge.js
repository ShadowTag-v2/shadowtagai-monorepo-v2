// src/workstation/cor_yay_bridge.js
// ============================================================================
// Cor.Yay Serverless WebSocket Relay
// ============================================================================
// Block 10 of the Ex Toto Omni-Compile (Gideon OS Architecture)
// Bridges Cloud Tasks (Pub/Sub) to the React UI via WebSocket.
// ============================================================================
const WebSocket = require('ws');
const { PubSub } = require('@google-cloud/pubsub');

const wss = new WebSocket.Server({ port: 3000 });
const pubsub = new PubSub();
const globalState = { thoughts: {}, active_track: 'REALITY' };

wss.on('connection', (ws) => {
  ws.send(JSON.stringify({ type: 'SYNC', data: globalState }));
});

// Listen for Serverless Cloud Tasks pushing progress updates
const subscription = pubsub.subscription('omega-swarm-progress');
subscription.on('message', (message) => {
  const data = JSON.parse(message.data.toString());

  if (data.type === 'AGENT_THOUGHT_CHUNK') {
    globalState.thoughts[data.taskId] = (globalState.thoughts[data.taskId] || '') + data.text;
    for (const c of wss.clients) {
      c.send(JSON.stringify({ type: 'THOUGHT_STREAM', payload: data }));
    }
  }
  if (data.type === 'UI_RENDER_COMPONENT') {
    for (const c of wss.clients) {
      c.send(JSON.stringify({ type: 'UI_RENDER_COMPONENT', payload: data }));
    }
  }
  message.ack();
});

console.log('Cor.Yay Serverless Bridge listening on 3000');
