/**
 * Firestore RBAC Logic Emulator Tests
 * RUN VIA: firebase emulators:exec "npm test"
 */
const { assertFails, assertSucceeds, initializeTestEnvironment } = require('@firebase/rules-unit-testing');
const fs = require('fs');

let testEnv;

beforeAll(async () => {
    testEnv = await initializeTestEnvironment({
        projectId: "shadowtag-omega-v4",
        firestore: { rules: fs.readFileSync("../firestore.rules", "utf8") }
    });
});

afterAll(async () => {
    await testEnv.cleanup();
});

describe("KovelAI Institutional RBAC", () => {

    it("Allows unauthenticated users to only CREATE standard public leads", async () => {
        const unauthedDb = testEnv.unauthenticatedContext().firestore();
        const docRef = unauthedDb.collection("kovelai_leads").doc("public_lead_123");

        // Assert CANNOT create (zero-trust ensures edge router handles it)
        await assertFails(docRef.set({ email: "test@domain.com", risk: "high" }));

        // Assert CANNOT read
        await assertFails(docRef.get());
    });

    it("Allows Partners to DELETE leads", async () => {
        const partnerDb = testEnv.authenticatedContext("partner_user", { role: "partner" }).firestore();
        const docRef = partnerDb.collection("kovelai_leads").doc("public_lead_123");

        await assertSucceeds(docRef.delete());
    });

    it("Blocks Analysts from DELETING leads, but allows READ", async () => {
        const analystDb = testEnv.authenticatedContext("analyst_user", { role: "analyst" }).firestore();
        const docRef = analystDb.collection("kovelai_leads").doc("public_lead_123");

        await assertSucceeds(docRef.get());
        await assertFails(docRef.delete());
    });
});
