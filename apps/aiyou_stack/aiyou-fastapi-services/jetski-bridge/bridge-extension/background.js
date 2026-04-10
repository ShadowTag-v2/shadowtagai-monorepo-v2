let socket = null;
const BRIDGE_URL = "ws://localhost:8081";

function connectToBridge() {
  console.log("Attempting to connect to Bridge...");
  socket = new WebSocket(BRIDGE_URL);

  socket.onopen = () => console.log("Bridge Connected");

  socket.onmessage = async (event) => {
    const msg = JSON.parse(event.data);
    if (!msg.action) return;

    try {
      let result = null;

      // --- ACTION HANDLERS ---
      if (msg.action === "navigate") {
        const tab = await chrome.tabs.create({ url: msg.payload.url });
        result = { tabId: tab.id, status: "navigated" };
      } else if (msg.action === "exec") {
        // Execute arbitrary JS in the active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab) {
          const injection = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: (code) => eval(code), // DANGEROUS: For internal agent use only
            args: [msg.payload.code],
          });
          result = injection[0].result;
        }
      }
      // -----------------------

      // Send result back to Bridge
      socket.send(JSON.stringify({ id: msg.id, result: result }));
    } catch (err) {
      socket.send(JSON.stringify({ id: msg.id, error: err.message }));
    }
  };

  socket.onclose = () => {
    console.log("Bridge lost. Reconnecting in 5s...");
    setTimeout(connectToBridge, 5000);
  };

  socket.onerror = (err) => {
    console.error("WebSocket Error:", err);
    socket.close();
  };
}

// Ensure connection starts immediately and persists
chrome.runtime.onStartup.addListener(connectToBridge);
connectToBridge();
