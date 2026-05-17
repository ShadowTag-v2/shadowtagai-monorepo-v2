// 05_worker.js
// Save in src/hands/

const { Firestore } = require("@google-cloud/firestore");
const puppeteer = require("puppeteer-core");
const db = new Firestore();

async function start() {
  console.log("🖐️ ShadowTag Hands Listening...");

  // Watch for new tasks
  db.collection("agent_queue")
    .where("status", "==", "queued")
    .onSnapshot((snapshot) => {
      snapshot.docChanges().forEach(async (change) => {
        if (change.type === "added") {
          console.log(`Task Received: ${change.doc.id}`);
          await processTask(change.doc.id, change.doc.data().goal);
        }
      });
    });
}

async function processTask(taskId, goal) {
  const docRef = db.collection("agent_queue").doc(taskId);
  await docRef.update({ status: "processing" });

  try {
    // Connect to the local Chrome (installed via startup script)
    const browser = await puppeteer.launch({
      executablePath: "/usr/bin/google-chrome",
      args: ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
    });
    const page = await browser.newPage();
    await page.goto("https://google.com"); // Placeholder logic

    const title = await page.title();
    await browser.close();

    // Report Result via A2UI
    await docRef.update({
      status: "completed",
      result: {
        component: "Panel",
        title: "Task Complete",
        children: [{ component: "Markdown", content: `Visited: **${title}**` }],
      },
    });
  } catch (err) {
    console.error(err);
    await docRef.update({ status: "failed", error: err.message });
  }
}

start();
