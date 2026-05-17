Object.defineProperty(exports, "__esModule", { value: true });
// Mock server to test Lead Capture Router locally without Firebase emulator
const express_1 = require("express");
const index_1 = require("./index");
const app = (0, express_1.default)();
app.use(express_1.default.json());
// Forward requests to the exported Cloud Function (assumes simple HTTP routing)
app.post("/shadowtag-omega-v4/us-central1/captureLead", (req, res) => {
  // Basic catch-all CORS for local testing without Firebase v2 wrapper
  res.set("Access-Control-Allow-Origin", "*");
  res.set("Access-Control-Allow-Methods", "GET, POST");
  res.set("Access-Control-Allow-Headers", "Content-Type, Accept");
  (0, index_1.captureLead)(req, res);
});
// also handle OPTIONS preflight
app.options("/shadowtag-omega-v4/us-central1/captureLead", (_req, res) => {
  res.set("Access-Control-Allow-Origin", "*");
  res.set("Access-Control-Allow-Methods", "GET, POST");
  res.set("Access-Control-Allow-Headers", "Content-Type, Accept");
  res.status(204).send("");
});
const PORT = 5001;
app.listen(PORT, () => {
  console.log(`Mock emulator listening on port ${PORT}`);
});
//# sourceMappingURL=mock.js.map
