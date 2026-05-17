/**
 * Single-Agent Pattern Reference Implementation
 *
 * This example demonstrates a production-ready single-agent for customer support.
 * Key features:
 * - Dynamic decision-making
 * - Context maintenance across interactions
 * - Tool selection based on situation
 * - Comprehensive error handling
 * - Self-validation
 */

import { query, tool } from "@anthropic-ai/claude-agent-sdk";

// ==================== Types ====================

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
}

interface CustomerContext {
  customerId?: string;
  conversationHistory: Message[];
  issueResolved: boolean;
  issueType?: string;
  priority?: "low" | "medium" | "high" | "critical";
}

interface CustomerAccount {
  id: string;
  name: string;
  email: string;
  tier: "free" | "pro" | "enterprise";
  status: "active" | "suspended" | "cancelled";
  accountBalance: number;
}

interface SupportTicket {
  id: string;
  title: string;
  description: string;
  status: "open" | "in_progress" | "resolved" | "escalated";
  priority: "low" | "medium" | "high" | "critical";
}

// ==================== System Prompt ====================

const SUPPORT_AGENT_PROMPT = `
<agent_configuration>
  <metadata>
    <agent_name>Customer Support Agent</agent_name>
    <pattern>single-agent</pattern>
    <version>1.0.0</version>
  </metadata>

  <role>
You are a customer support agent for TechCorp, specializing in resolving
technical issues, billing questions, and account management. You have 5 years
of experience and are known for patient, clear communication and problem-solving.
  </role>

  <core_capabilities>
Primary Capabilities:
- Diagnose technical issues through systematic questioning
- Access and review customer account information
- Process refunds and billing adjustments (within limits)
- Escalate complex issues appropriately
- Provide clear, step-by-step guidance

Available Tools:
- account_lookup: Get customer account information
- order_history: View past orders and transactions
- process_refund: Issue refunds (up to $500)
- create_ticket: Escalate to specialists
- knowledge_search: Search help documentation
  </core_capabilities>

  <execution_philosophy>
Core Loop:
1. Gather context → Ask clarifying questions, look up account
2. Take action → Use appropriate tools to resolve issue
3. Verify work → Confirm resolution with customer
4. Iterate or complete → Continue until resolved or escalated

Communication Style:
- Empathetic and patient
- Clear and concise
- Professional but friendly
- Proactive in offering help

Default Behavior:
- Ask clarifying questions before making assumptions
- Explain what you're doing and why
- Confirm before taking major actions (refunds, cancellations)
- Offer alternatives when primary solution isn't available
  </execution_philosophy>

  <quality_standards>
Every interaction must:
- Resolve issue or provide clear next steps
- Maintain professional, empathetic tone
- Complete within 5 minutes (target)
- Document all actions taken

Before completing:
1. Confirm customer satisfaction
2. Verify issue is fully resolved or escalated
3. Document resolution in system
4. Offer additional assistance
  </quality_standards>

  <constraints>
Must NOT:
- Issue refunds >$500 without manager approval
- Access accounts without verification
- Make promises outside company policy
- Share sensitive customer data
- Modify account without explicit customer request

Resource Limits:
- Maximum 10 tool calls per interaction
- Escalate if unable to resolve within 15 minutes
- Request manager approval for exceptions

Always:
- Verify customer identity before account access
- Log all actions and decisions
- Provide ticket number for unresolved issues
- Follow up on escalations
  </constraints>

  <error_handling>
When errors occur:
1. Apologize professionally
2. Explain what went wrong (if appropriate)
3. Offer alternative solution
4. Escalate if necessary
5. Log error for review

Never:
- Blame the customer
- Make excuses
- Ignore the error
- Proceed without resolution
  </error_handling>
</agent_configuration>
`;

// ==================== Tools ====================

const accountLookupTool = tool({
  name: "account_lookup",
  description:
    "Look up customer account information by customer ID or email. Use when you need to verify account details or check account status.",
  parameters: {
    type: "object",
    properties: {
      identifier: {
        type: "string",
        description: "Customer ID or email address",
      },
    },
    required: ["identifier"],
  },
  execute: async ({ identifier }): Promise<CustomerAccount> => {
    // Simulate database lookup
    console.log(`[Tool] Looking up account: ${identifier}`);

    // Mock data
    return {
      id: "CUST-12345",
      name: "John Doe",
      email: identifier.includes("@") ? identifier : "redacted@shadowtag-v4.local",
      tier: "pro",
      status: "active",
      accountBalance: 150.0,
    };
  },
});

const orderHistoryTool = tool({
  name: "order_history",
  description:
    "View customer's order history and transactions. Use when investigating billing issues or order problems.",
  parameters: {
    type: "object",
    properties: {
      customerId: {
        type: "string",
        description: "Customer ID",
      },
      limit: {
        type: "number",
        description: "Number of orders to retrieve (default: 10)",
      },
    },
    required: ["customerId"],
  },
  execute: async ({ customerId, limit = 10 }) => {
    console.log(`[Tool] Fetching order history for: ${customerId}`);

    // Mock data
    return {
      orders: [
        {
          id: "ORD-001",
          date: "2025-11-01",
          amount: 99.99,
          status: "completed",
          items: ["Pro Plan - Monthly"],
        },
        {
          id: "ORD-002",
          date: "2025-10-01",
          amount: 99.99,
          status: "completed",
          items: ["Pro Plan - Monthly"],
        },
      ],
    };
  },
});

const processRefundTool = tool({
  name: "process_refund",
  description:
    "Process a refund for a customer. Use only after confirming the refund is warranted. Maximum $500 without approval.",
  parameters: {
    type: "object",
    properties: {
      orderId: {
        type: "string",
        description: "Order ID to refund",
      },
      amount: {
        type: "number",
        description: "Refund amount in USD",
      },
      reason: {
        type: "string",
        description: "Reason for refund",
      },
    },
    required: ["orderId", "amount", "reason"],
  },
  execute: async ({ orderId, amount, reason }) => {
    console.log(`[Tool] Processing refund: ${orderId} - $${amount}`);

    if (amount > 500) {
      throw new Error("Refund amount exceeds $500 limit. Manager approval required.");
    }

    // Mock refund processing
    return {
      refundId: `REF-${Date.now()}`,
      orderId,
      amount,
      status: "processed",
      estimatedDays: 3,
      message: `Refund of $${amount} will appear in 3-5 business days`,
    };
  },
});

const createTicketTool = tool({
  name: "create_ticket",
  description:
    "Create a support ticket for escalation to specialists. Use when issue requires expert assistance or is beyond your scope.",
  parameters: {
    type: "object",
    properties: {
      title: {
        type: "string",
        description: "Brief ticket title",
      },
      description: {
        type: "string",
        description: "Detailed issue description",
      },
      priority: {
        type: "string",
        enum: ["low", "medium", "high", "critical"],
        description: "Issue priority",
      },
      customerId: {
        type: "string",
        description: "Customer ID",
      },
    },
    required: ["title", "description", "priority", "customerId"],
  },
  execute: async ({ title, description, priority, customerId }) => {
    console.log(`[Tool] Creating ticket: ${title} [${priority}]`);

    // Mock ticket creation
    const ticketId = `TICKET-${Date.now()}`;

    return {
      ticketId,
      title,
      status: "open",
      priority,
      estimatedResponse: priority === "critical" ? "1 hour" : "24 hours",
      message: `Ticket ${ticketId} created. Specialist will respond within ${priority === "critical" ? "1 hour" : "24 hours"}.`,
    };
  },
});

const knowledgeSearchTool = tool({
  name: "knowledge_search",
  description:
    "Search help documentation and knowledge base. Use to find solutions, troubleshooting steps, or policy information.",
  parameters: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "Search query",
      },
    },
    required: ["query"],
  },
  execute: async ({ query }) => {
    console.log(`[Tool] Searching knowledge base: ${query}`);

    // Mock knowledge base search
    return {
      results: [
        {
          title: "How to reset your password",
          url: "https://help.techcorp.com/reset-password",
          excerpt:
            "Follow these steps to reset your password: 1. Click 'Forgot Password' 2. Enter your email...",
        },
        {
          title: "Billing FAQ",
          url: "https://help.techcorp.com/billing-faq",
          excerpt:
            "Common billing questions: When am I charged? How do I update payment method?...",
        },
      ],
    };
  },
});

// ==================== Agent Class ====================

class CustomerSupportAgent {
  private context: CustomerContext;
  private tools: unknown[];

  constructor() {
    this.context = {
      conversationHistory: [],
      issueResolved: false,
    };

    this.tools = [
      accountLookupTool,
      orderHistoryTool,
      processRefundTool,
      createTicketTool,
      knowledgeSearchTool,
    ];
  }

  async handleMessage(userMessage: string): Promise<string> {
    // Add user message to history
    this.context.conversationHistory.push({
      role: "user",
      content: userMessage,
      timestamp: new Date(),
    });

    console.log(`\n[User] ${userMessage}`);

    try {
      // Build prompt with conversation history
      const prompt = this.buildPrompt(userMessage);

      // Query agent
      const response = await query({
        prompt,
        options: {
          systemPrompt: SUPPORT_AGENT_PROMPT,
          tools: this.tools,
          maxTokens: 4000,
          model: "claude-sonnet-4.5-20250514",
        },
      });

      // Add assistant response to history
      this.context.conversationHistory.push({
        role: "assistant",
        content: response,
        timestamp: new Date(),
      });

      console.log(`[Agent] ${response}`);

      return response;
    } catch (error) {
      const errorResponse = `I apologize, but I encountered an error: ${error.message}. Let me create a ticket to have a specialist assist you.`;

      this.context.conversationHistory.push({
        role: "assistant",
        content: errorResponse,
        timestamp: new Date(),
      });

      return errorResponse;
    }
  }

  private buildPrompt(currentMessage: string): string {
    // Include recent conversation history for context
    const recentHistory = this.context.conversationHistory
      .slice(-6) // Last 3 exchanges
      .map((m) => `${m.role === "user" ? "Customer" : "Agent"}: ${m.content}`)
      .join("\n\n");

    return `
${recentHistory ? `Previous conversation:\n${recentHistory}\n\n` : ""}
Current customer message:
${currentMessage}

Please respond appropriately, using available tools as needed to resolve the issue.
    `.trim();
  }

  getContext(): CustomerContext {
    return { ...this.context };
  }

  resetContext(): void {
    this.context = {
      conversationHistory: [],
      issueResolved: false,
    };
  }
}

// ==================== Main ====================

async function main() {
  console.log("=== Customer Support Agent Demo ===\n");

  const agent = new CustomerSupportAgent();

  // Simulate a customer support conversation
  const conversation = [
    "Hi, I was charged twice for my subscription this month!",
    "My email is redacted@shadowtag-v4.local and my customer ID is CUST-12345",
    "Yes, please process the refund for the duplicate charge. It was $99.99.",
    "Thank you! That resolves my issue.",
  ];

  for (const message of conversation) {
    const _response = await agent.handleMessage(message);
    console.log(); // Add spacing

    // Small delay to simulate real conversation
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  console.log("\n=== Conversation Complete ===");
  console.log(`Total messages: ${agent.getContext().conversationHistory.length}`);
  console.log(`Issue resolved: ${agent.getContext().issueResolved}`);
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

// Export for use as module
export { type CustomerAccount, type CustomerContext, CustomerSupportAgent, type SupportTicket };
