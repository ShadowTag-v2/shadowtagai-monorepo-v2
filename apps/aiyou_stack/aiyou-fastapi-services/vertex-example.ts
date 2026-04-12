import { AnthropicVertex } from "@anthropic-ai/vertex-sdk";

/**
 * Example demonstrating how to use the Anthropic Vertex SDK
 *
 * Required environment variables:
 * - CLOUD_ML_REGION: Google Cloud region (e.g., 'us-east5')
 * - ANTHROPIC_VERTEX_PROJECT_ID: Your Google Cloud project ID
 *
 * The SDK uses the standard google-auth-library flow for authentication.
 */

async function main() {
  // Initialize the client
  // Reads from CLOUD_ML_REGION & ANTHROPIC_VERTEX_PROJECT_ID environment variables
  // Additionally goes through the standard google-auth-library flow
  const client = new AnthropicVertex();

  const msg = await client.messages.create({
    model: "claude-opus-4-1@20250805",
    max_tokens: 20000,
    temperature: 1,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "text",
            text: "/plugin marketplace add obra/superpowers-marketplace\n/plugin install superpowers@superpowers-marketplace ",
          },
        ],
      },
      {
        role: "assistant",
        content: [
          {
            type: "text",
            text: "I'll help you add the marketplace and install the superpowers plugin.\n\n```bash\n/plugin marketplace add obra/superpowers-marketplace\n```\n\nThis command adds the superpowers marketplace to your available plugin sources.\n\n```bash\n/plugin install superpowers@superpowers-marketplace\n```\n\nThis command installs the superpowers plugin from the marketplace you just added.\n\n**What this does:**\n- The first command registers the `obra/superpowers-marketplace` as a source for plugins\n- The second command installs the `superpowers` plugin specifically from that marketplace\n- Once installed, you'll have access to whatever capabilities the superpowers plugin provides\n\nThe commands should execute successfully if:\n- The marketplace repository exists and is accessible\n- The superpowers plugin is available in that marketplace\n- You have the necessary permissions to install plugins\n\nIs there anything specific you'd like to do with the superpowers plugin once it's installed?",
          },
        ],
      },
      {
        role: "user",
        content: [
          {
            type: "text",
            text: "no, go",
          },
        ],
      },
      {
        role: "assistant",
        content: [
          {
            type: "thinking",
            thinking:
              "The user wants me to execute these commands. They've given me the go-ahead with \"no, go\" meaning they don't need anything specific after installation and want me to proceed with running the commands.\n\nHowever, I should clarify that I cannot actually execute shell commands or plugin installation commands. I'm an AI assistant that can help explain, guide, and provide information about commands, but I cannot run them directly on any system.\n\nI should explain this to the user clearly.",
            signature:
              "Eo8FCkYICRgCKkD5ZsLad5fuXNDnN8UovxZdh9dY2SKVY5BszjcGc3rOj8NbHMFrLfOJ2eUJ8slbeNPD1BCCmf9mAXxQsYT7br1TEgzu2atCfMuMSnKS9oUaDHDaiXiY1bDFKpyrjSIwP+R+a0/8C6Pfo0eGtLn2pWh/AnGBh+9YkNH/pM+2iyAjqhWeBTvhYUfnwjPBJHkLKvYDTXnjEu4hjL9qmOj1ovhS5Cz4B0RL1I2CoY52Bw/09m7xXoChf2A2o8ybrOPZ6VpaJGhc4o+Dpi/6YtFXI2mWv6jpkUkEFufT2aiMGVuMKY/iWwWxDPdRw8PMhpy63rYfekTGvwzTP2e0ujYHybZYMCbGgy1MN4YjXXpZcW81+S3Tm4/Ea/ERVnuG8Goked/pYGv9BpfCqWcjTS9o/IxHC6gGN0YMOuy29CzPwr6bffwtZeI6Edzlah91l3gK1CEzPNjKRUhw/diFvZShR38RX1dINvOSvHKJ5ckTKfpqk/3mz80ZfDVT7PNqbo7C0cPqvTE/yRUS7fNDnksabuQFjOMUDB8CBQ4uI99zXwr0idD1TFhU5XmipNyayHBy6ByCgTrr2GMmdXilw8ebYruFvhQCY82mL0E+nA1dj0Hn4Uoi7sFMeVZjMdzRaW7WrPTdm8ThjyAJ7b2saZlTJS3aFpdCuqDClLMlELaKZi4fZ5HxDSQzLiSHFm8rtYBT6BsucoAy5yG8E6TdopnAAEfbiTSZVA25ehK3CCXDQn70SRWI0koAW98vVk4YhF6GqqRHNqsQvXTYQ7hxghGuLPGEulwu0fagRDlQyN2dEwDxhU9ZqhtwRHgw8Qbil3+9SYGw0rt4sP8nvgT0Wrpm39vhr+Gsw9X8VBgB",
          },
          {
            type: "text",
            text: "I apologize for any confusion, but I cannot actually execute these commands for you. I'm an AI assistant that can help explain and guide you through processes, but I don't have the ability to run commands on your system or install plugins directly.\n\nTo run these commands, you'll need to:\n\n1. Open your terminal or command line interface\n2. Execute the commands yourself:\n   ```bash\n   /plugin marketplace add obra/superpowers-marketplace\n   /plugin install superpowers@superpowers-marketplace\n   ```\n\nThese appear to be commands for a specific plugin management system. Make sure you're:\n- In the correct directory or environment where these commands are valid\n- Have the necessary permissions to add marketplaces and install plugins\n- Connected to the internet if the marketplace needs to be fetched remotely\n\nIf you encounter any errors when running these commands yourself, feel free to share them and I can help troubleshoot!",
          },
        ],
      },
    ],
    thinking: {
      type: "enabled",
      budget_tokens: 16000,
    },
  });

  console.log(msg);
}

// Run the example
main().catch(console.error);
