// agent-worker.js
const { Firestore } = require('@google-cloud/firestore');
const { Storage } = require('@google-cloud/storage');
const { VertexAI } = require('@google-cloud/vertexai');
const fs = require('fs-extra');
const axios = require('axios');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

// --- CONFIGURATION ---
const PROJECT_ID = process.env.GOOGLE_CLOUD_PROJECT || 'shadowtag-omega-v2';
const REGION = 'us-central1';
const BRIDGE_URL = 'http://localhost:8080/control'; // The Bridge Server
const FILESTORE_PATH = process.env.FILESTORE_PATH || '/mnt/agent_share';
const LAKE_BUCKET = process.env.LAKE_BUCKET_NAME || `${PROJECT_ID}-agent-lake`;

// --- CLIENTS ---
const firestore = new Firestore({ projectId: PROJECT_ID });
const storage = new Storage({ projectId: PROJECT_ID });
const vertexAI = new VertexAI({ project: PROJECT_ID, location: REGION });
const model = vertexAI.getGenerativeModel({ model: 'gemini-1.5-pro-preview-0409' });

// --- MAIN LOOP ---
async function startWorker() {
  console.log("🚀 Agent Worker Started. Waiting for tasks...");
  
  // Listen to the 'tasks' collection for status = 'queued'
  const taskCollection = firestore.collection('agent_tasks');
  const query = taskCollection.where('status', '==', 'queued').limit(1);

  query.onSnapshot(async (snapshot) => {
    if (snapshot.empty) return;

    const doc = snapshot.docs[0];
    const task = doc.data();
    
    // 1. Claim the task (Atomic lock)
    try {
      await firestore.runTransaction(async (t) => {
        const freshDoc = await t.get(doc.ref);
        if (freshDoc.data().status !== 'queued') throw "Already taken";
        t.update(doc.ref, { status: 'processing', workerId: process.env.HOSTNAME || 'local-worker', startTime: new Date() });
      });
    } catch (e) {
      return; // Another worker grabbed it
    }

    console.log(`\n💼 Processing Task ${doc.id}: ${task.goal}`);

    try {
      // 2. Execute The Agent Logic
      const resultData = await runAgentTask(task.goal);
      
      // 3. Handle Data (The "Lake" Logic)
      const storagePath = await persistData(doc.id, resultData);

      // 4. Mark Complete
      await doc.ref.update({ 
        status: 'completed', 
        resultPath: storagePath,
        endTime: new Date(),
        a2ui_render: generateA2UI(doc.id, resultData, storagePath) # A2UI Output
      });
      console.log(`✅ Task ${doc.id} Complete.`);

    } catch (err) {
      console.error(`❌ Task Failed:`, err);
      await doc.ref.update({ status: 'failed', error: err.message });
    }
  });
}

// --- THE INTELLIGENT AGENT ---
async function runAgentTask(goal) {
  let step = 0;
  const context = []; // Keep track of what we've done

  while (step < 10) {
    // A. Get State from Browser (via Bridge)
    // We assume the bridge has a /snapshot endpoint, or we ask it to execute extraction
    try {
        const screenshotResp = await axios.post(BRIDGE_URL, { 
          action: "exec", 
          payload: { code: "await chrome.tabs.captureVisibleTab(null, {format: 'png'})" } 
        });
        var base64Image = screenshotResp.data.result; // The Bridge returns the raw result
    } catch (e) {
        console.warn("Bridge snapshot failed (is it running?), using Mock Image");
        var base64Image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";
    }

    // B. Ask Gemini (Vertex AI)
    const prompt = `
      Goal: "${goal}"
      History: ${JSON.stringify(context)}
      Screen: [Attached]
      
      Output JSON ONLY:
      {
        "thought": "Reasoning here...",
        "action": "navigate" | "click" | "type" | "extract_and_finish",
        "params": { ... }
      }
    `;

    const req = {
      contents: [{ role: 'user', parts: [{ text: prompt }, { inlineData: { mimeType: 'image/png', data: base64Image } }] }]
    };

    const streamingResp = await model.generateContentStream(req);
    const response = await streamingResp.response;
    const text = response.candidates[0].content.parts[0].text;
    
    // Parse JSON safely (Gemini sometimes adds markdown backticks)
    const cleanJson = text.replace(/```json|```/g, '').trim();
    const decision = JSON.parse(cleanJson);

    console.log(`Step ${step}: ${decision.thought}`);
    context.push(decision.thought);

    // C. Execute Action
    if (decision.action === 'extract_and_finish') {
      return decision.params.data; // Return the scraped data
    }

    // Map Gemini action to Bridge Action
    let bridgePayload = {};
    
    if (decision.action === 'navigate') {
        bridgePayload = { action: "navigate", payload: { url: decision.params.url }};
    } else if (decision.action === 'click') {
        bridgePayload = { 
            action: "exec", 
            payload: { code: `document.querySelector('${decision.params.selector}').click()` } 
        };
    } else if (decision.action === 'type') {
        bridgePayload = { 
            action: "exec", 
            payload: { code: `document.querySelector('${decision.params.selector}').value = '${decision.params.text}'` } 
        };
    }

    await axios.post(BRIDGE_URL, bridgePayload);
    
    // Wait for page load/interaction
    await new Promise(r => setTimeout(r, 4000));
    step++;
  }
  throw new Error("Max steps reached without result");
}

// --- THE DATA ENGINEER ---
async function persistData(taskId, dataObj) {
  // 1. Save to FILESTORE (Hot/Shared)
  const localDir = path.join(FILESTORE_PATH, 'processed_tasks');
  await fs.ensureDir(localDir);
  
  const fileName = `task_${taskId}_${Date.now()}.json`;
  const localPath = path.join(localDir, fileName);
  
  await fs.writeJson(localPath, dataObj);
  console.log(`💾 Saved to Filestore: ${localPath}`);

  // 2. Upload to DATA LAKE (Cold/Analytical)
  const date = new Date();
  const partition = `year=${date.getFullYear()}/month=${date.getMonth()+1}/day=${date.getDate()}`;
  const gcsPath = `raw_data/${partition}/${fileName}`;

  await storage.bucket(LAKE_BUCKET).upload(localPath, {
    destination: gcsPath,
    metadata: {
      contentType: 'application/json',
      metadata: {
        taskId: taskId,
        source: 'agent-v1'
      }
    }
  });
  
  console.log(`🌊 Uploaded to Lake: gs://${LAKE_BUCKET}/${gcsPath}`);
  return `gs://${LAKE_BUCKET}/${gcsPath}`;
}

// --- A2UI GENERATOR ---
function generateA2UI(taskId, dataObj, storagePath) {
  return {
    "component": "Panel",
    "title": "Extraction Complete",
    "children": [
      { 
        "component": "InteractiveChart", 
        "type": "summary",
        "data": { "value": dataObj.total || 0, "label": "Total Value" } 
      },
      { 
        "component": "DynamicForm",
        "fields": [
            { "label": "Source", "value": dataObj.vendor || "Unknown", "readonly": true },
            { "label": "Date", "value": new Date().toISOString(), "readonly": true },
            { "label": "GCS Link", "value": storagePath, "type": "link", "readonly": true }
        ]
      }
    ]
  };
}

startWorker().catch(console.error);
