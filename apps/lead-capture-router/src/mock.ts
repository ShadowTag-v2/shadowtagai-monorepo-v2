// Mock server to test Lead Capture Router locally without Firebase emulator
import express from 'express';
import { captureLead } from './index';

const app = express();
app.use(express.json());

// Forward requests to the exported Cloud Function (assumes simple HTTP routing)
app.post('/shadowtag-omega-v4/us-central1/captureLead', (req, res) => {
    // Basic catch-all CORS for local testing without Firebase v2 wrapper
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Methods', 'GET, POST');
    res.set('Access-Control-Allow-Headers', 'Content-Type, Accept');
    
    captureLead(req as any, res as any);
});

// also handle OPTIONS preflight
app.options('/shadowtag-omega-v4/us-central1/captureLead', (req, res) => {
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Methods', 'GET, POST');
    res.set('Access-Control-Allow-Headers', 'Content-Type, Accept');
    res.status(204).send('');
});

const PORT = 5001;
app.listen(PORT, () => {
    console.log(`Mock emulator listening on port ${PORT}`);
});
