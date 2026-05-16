/**
 * x402 v2 Mainnet Payment Test with CDP Facilitator
 *
 * Required env: X402_TEST_PRIVATE_KEY
 */

import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { wrapFetchWithPayment, x402Client } from "@x402/fetch";
import { privateKeyToAccount } from "viem/accounts";

// Load from environment - never hardcode private keys!
const PRIVATE_KEY = process.env.X402_TEST_PRIVATE_KEY;
if (!PRIVATE_KEY) {
  console.error("❌ X402_TEST_PRIVATE_KEY not set in environment");
  process.exit(1);
}

const API_URL = process.env.X402_TEST_API_URL || "http://localhost:3333/api/x402/chat";

async function testPayment() {
  console.log("🧪 x402 v2 MAINNET Payment Test (CDP Facilitator)\n");

  const account = privateKeyToAccount(PRIVATE_KEY as `0x${string}`);
  console.log(`💳 Wallet: ${account.address}`);

  const client = new x402Client();
  registerExactEvmScheme(client, {
    signer: account,
    networks: ["eip155:8453"], // Base mainnet
  });

  const x402Fetch = wrapFetchWithPayment(fetch, client);

  console.log(`\n📡 Calling: ${API_URL}`);
  console.log(`💰 Payment: 0.01 USDC on Base mainnet`);
  console.log(`🏦 Facilitator: CDP (api.cdp.coinbase.com)\n`);

  try {
    const response = await x402Fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "Hello mainnet!" }),
    });

    console.log(`📬 Response status: ${response.status}`);

    const text = await response.text();
    try {
      const data = JSON.parse(text);
      console.log(`\n✅ Response:`, JSON.stringify(data, null, 2));
    } catch {
      console.log(`\n📄 Raw response:`, text.slice(0, 500));
    }

    const paymentResponse = response.headers.get("PAYMENT-RESPONSE");
    if (paymentResponse) {
      const decoded = JSON.parse(atob(paymentResponse));
      console.log(`\n💸 Payment Response:`, JSON.stringify(decoded, null, 2));
    }
  } catch (error: any) {
    console.error(`\n❌ Error:`, error.message || error);
  }
}

testPayment();
