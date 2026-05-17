/* eslint-env node */
const { Firestore } = require("@google-cloud/firestore");
const { chromium } = require("playwright"); // The Jetski Engine

const db = new Firestore();
const COLLECTION = "agent_queue";

async function main() {
  console.log("🚤 Jetski Worker (Playwright) Active. Polling Firestore...");

  const query = db.collection(COLLECTION).where("status", "==", "queued");

  // Use a more robust polling mechanism to avoid race conditions and ensure single-worker processing.
  // Instead of onSnapshot, we'll periodically query and attempt to claim a task.
  // This also allows for better error handling within the loop.
  setInterval(async () => {
    try {
      const snapshot = await query.limit(1).get(); // Get one queued task
      if (snapshot.empty) {
        // console.log("No queued tasks found. Waiting...");
        return;
      }

      const doc = snapshot.docs[0];
      const taskId = doc.id;
      const task = doc.data();

      // Attempt to atomically update the task status to 'processing'
      // This prevents multiple workers from picking up the same task.
      const docRef = db.collection(COLLECTION).doc(taskId);
      await db.runTransaction(async (transaction) => {
        const currentDoc = await transaction.get(docRef);
        if (!currentDoc.exists) {
          throw new Error("Document does not exist!");
        }
        if (currentDoc.data().status === "queued") {
          transaction.update(docRef, {
            status: "processing",
            worker: process.env.HOSTNAME,
            processedAt: Firestore.FieldValue.serverTimestamp(),
          });
          console.log(`>>> Acquired Target: ${taskId}`);
          await executeMission(taskId, task.goal);
        } else {
          console.log(`Task ${taskId} already processed or being processed by another worker.`);
        }
      });
    } catch (error) {
      console.error("Error polling or processing task:", error);
    }
  }, 5000); // Poll every 5 seconds

  // Handle graceful shutdown
  const shutdown = async () => {
    console.log("Shutting down worker. Marking active tasks as failed or re-queued...");
    // In a real-world scenario, you'd iterate through tasks currently marked
    // with this worker's hostname and set them back to 'queued' or 'failed'.
    // For this example, we'll just log.
    console.log("Graceful shutdown complete.");
    process.exit(0);
  };

  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

async function executeMission(taskId, goal) {
  const docRef = db.collection(COLLECTION).doc(taskId);
  await docRef.update({ status: "processing", worker: process.env.HOSTNAME });

  console.log(`Executing Goal: ${goal}`); // Use variable to satisfy lint

  let browser = null;
  try {
    // Allow headless mode to be configurable via environment variable for debugging
    const headless = process.env.HEADLESS !== "false";
    browser = await chromium.launch({ headless: headless }); // Headless for speed
    const page = await browser.newPage();

    // --- JETSKI LOGIC HERE ---
    // For demo: verify internet and perform a basic 'search' action
    console.log(`[Task ${taskId}] Navigating to example.com...`);
    await page.goto("https://example.com");
    const title = await page.title();
    const screenshot = await page.screenshot({ type: "png" });

    await docRef.update({
      status: "completed",
      result: {
        title: title,
        screenshot_base64: screenshot.toString("base64"),
        note: "Mission Accomplished via Playwright",
      },
      completedAt: Firestore.FieldValue.serverTimestamp(),
    });
    console.log(`[Task ${taskId}] Mission Complete.`);
  } catch (err) {
    console.error(`[Task ${taskId}] Mission Failed:`, err);
    await docRef.update({
      status: "failed",
      error: err.message,
      failedAt: Firestore.FieldValue.serverTimestamp(),
    });
  } finally {
    if (browser) {
      console.log(`[Task ${taskId}] Closing browser.`);
      await browser.close();
    }
  }
}

main();
