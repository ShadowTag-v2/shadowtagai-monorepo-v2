import {
  assertFails,
  assertSucceeds,
  initializeTestEnvironment,
  RulesTestEnvironment,
} from "@firebase/rules-unit-testing";
import * as fs from "fs";
import { describe, beforeAll, afterAll, it, beforeEach } from "node:test";

let testEnv: RulesTestEnvironment;

describe("Firestore security rules", () => {
  beforeAll(async () => {
    testEnv = await initializeTestEnvironment({
      projectId: "demo-shadowtag-omega-v4",
      firestore: {
        rules: fs.readFileSync("firestore.rules", "utf8"),
      },
    });
  });

  beforeEach(async () => {
    await testEnv.clearFirestore();
  });

  afterAll(async () => {
    await testEnv.cleanup();
  });

  it("should fail when any user tries to create a contact_requests manually", async () => {
    const unauthedDb = testEnv.unauthenticatedContext().firestore();
    const docRef = unauthedDb.collection("contact_requests").doc("test-123");
    await assertFails(docRef.set({ email: "hacker@evil.com" }));
  });

  it("should fail when authed user tries to create a contact_requests manually", async () => {
    const authedDb = testEnv.authenticatedContext("user-1").firestore();
    const docRef = authedDb.collection("contact_requests").doc("test-123");
    await assertFails(docRef.set({ email: "user@legit.com" }));
  });
});
