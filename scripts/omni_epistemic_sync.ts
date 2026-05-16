import { writeFileSync, readFileSync, existsSync } from "node:fs";
import { randomUUID } from "node:crypto";

const args = process.argv.slice(2);
if (args.length < 2) {
    console.error("❌ Usage: bun run scripts/omni_epistemic_sync.ts <atom_type> \"<knowledge_content>\" \"<optional_text_to_supersede>\"");
    process.exit(1);
}

const [atomType, content, supersedes] = args;
const id = randomUUID().split('-')[0];
const timestamp = new Date().toISOString();

console.log(`⚡ [Omni-Sync] Initiating 14-Point Epistemic Broadcast...`);

// Helper for surgical file overwrites/appends
function syncFile(path: string, header: string, payload: string, overwriteTarget?: string) {
    if (!existsSync(path)) writeFileSync(path, `# ${header}\n`);
    let fileData = readFileSync(path, "utf8");
    if (overwriteTarget && fileData.includes(overwriteTarget)) {
        const regex = new RegExp(`.*${overwriteTarget}.*\\n?`, 'gi');
        fileData = fileData.replace(regex, '');
        console.log(`   ✂️ Superseded stale knowledge in ${path}`);
    }
    writeFileSync(path, fileData + `\n- [${timestamp}] [${atomType.toUpperCase()}] ${payload}\n`);
    console.log(`   ✅ Synced: ${path}`);
}

try {
    // BOXES 1-6: Local Workspace Contexts
    syncFile(".agents/skills/global_epistemics.md", "Custom Skills", content, supersedes);
    syncFile("operator-invariants.md", "Operator Invariants", content, supersedes);
    syncFile("gemini.md", "Gemini Context", content, supersedes);
    syncFile("claude.md", "Claude Context", content, supersedes);
    syncFile("agent.md", "Global Agent Map", content, supersedes);
    syncFile("memory.md", "General Memory Logs", content, supersedes);

    // BOXES 7-9: The Memory Kernel & Immutable Beads
    const atomPayload = `---\nid: ${id}\natom_type: ${atomType}\ncreated_at: ${timestamp}\n---\n${content}\n`;
    writeFileSync(`.agents/memory_kernel/${atomType}_${id}.md`, atomPayload);
    writeFileSync(`.beads/bead_${Date.now()}_${id}.json`, JSON.stringify({ id, timestamp, atomType, content }));
    console.log(`   ✅ Synced: Memory Kernel & Immutable Beads.`);

    // BOX 10 & 11: Antigravity Knowledge (KI) & MCP Triggers
    // Antigravity's KI engine reads artifacts from the conversation to generate KIs.
    // By outputting this specific markdown block to the terminal, Antigravity parses it natively.
    console.log(`\n==================================================`);
    console.log(`[ANTIGRAVITY KNOWLEDGE ITEM ARTIFACT FOR EXTRACTION]`);
    console.log(`Title: Epistemic Update - ${atomType.toUpperCase()}`);
    console.log(`Summary: ${content}`);
    console.log(`Status: MCP Reload Required`);
    console.log(`==================================================\n`);

    // BOXES 12-14: The Cloud Queue (Drive API, BigQuery, Spanner)
    // We do NOT block the agent waiting for Google Cloud APIs. We queue them for the daemon.
    const cloudQueuePath = `.beads/cloud_sync_queue.json`;
    let cloudQueue: any[] = [];
    if (existsSync(cloudQueuePath)) {
        try { cloudQueue = JSON.parse(readFileSync(cloudQueuePath, "utf8")); } catch(e) {}
    }
    cloudQueue.push({
        id, timestamp, atomType, content, supersedes: supersedes || null,
        targets: ["google_drive_api", "bigquery_table", "spanner_instance", "anthropic_memory_mcp"]
    });
    writeFileSync(cloudQueuePath, JSON.stringify(cloudQueue, null, 2));
    console.log(`   ✅ Queued: Google Drive, BigQuery, Spanner, and MCP payloads for Dream Consolidation Daemon.`);

    console.log(`\n🎉 [SUCCESS] 14-Point Omni-Sync Complete. Context permanently frozen.`);
} catch (e) {
    console.error("❌ Sync Failed:", e);
}
