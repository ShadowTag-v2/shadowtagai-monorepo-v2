// admin-trigger.js
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore();

async function queueTask() {
  await db.collection("agent_tasks").add({
    status: "queued",
    created_at: new Date(),
    goal: "Go to news.ycombinator.com and extract the top 5 titles and links.",
  });
  console.log("Task Queued");
}
queueTask();
