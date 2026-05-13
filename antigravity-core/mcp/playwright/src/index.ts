import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { type Browser, chromium, type Page } from 'playwright';

const server = new Server(
  {
    name: 'antigravity-playwright',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  },
);

let browser: Browser | null = null;
let page: Page | null = null;

async function getPage() {
  if (!browser) {
    browser = await chromium.launch({ headless: true });
    page = await browser.newPage();
  }
  return page!;
}

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'navigate',
        description: 'Navigate to a URL',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string' },
          },
          required: ['url'],
        },
      },
      {
        name: 'get_content',
        description: 'Get the current page content as text',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'screenshot',
        description: 'Take a screenshot of the current page',
        inputSchema: {
          type: 'object',
          properties: {
            fullPage: { type: 'boolean', description: 'Take a full page screenshot' },
          },
        },
      },
      {
        name: 'click',
        description: 'Click an element by selector',
        inputSchema: {
          type: 'object',
          properties: {
            selector: { type: 'string' },
          },
          required: ['selector'],
        },
      },
      {
        name: 'fill',
        description: 'Fill an input element',
        inputSchema: {
          type: 'object',
          properties: {
            selector: { type: 'string' },
            value: { type: 'string' },
          },
          required: ['selector', 'value'],
        },
      },
      {
        name: 'evaluate',
        description: 'Evaluate Javascript in the browser context',
        inputSchema: {
          type: 'object',
          properties: {
            script: { type: 'string', description: 'JavaScript code to execute' },
          },
          required: ['script'],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const p = await getPage();

  try {
    switch (request.params.name) {
      case 'navigate': {
        const url = String(request.params.arguments?.url);
        await p.goto(url, { waitUntil: 'networkidle' });
        return {
          content: [{ type: 'text', text: `Navigated to ${url}` }],
        };
      }
      case 'get_content': {
        const text = await p.evaluate(() => document.body.innerText);
        return {
          content: [{ type: 'text', text }],
        };
      }
      case 'screenshot': {
        const fullPage = Boolean(request.params.arguments?.fullPage);
        const buffer = await p.screenshot({ fullPage });
        return {
          content: [{ type: 'text', text: `Screenshot taken (${buffer.length} bytes)` }],
        };
      }
      case 'click': {
        const selector = String(request.params.arguments?.selector);
        await p.click(selector);
        return {
          content: [{ type: 'text', text: `Clicked ${selector}` }],
        };
      }
      case 'fill': {
        const selector = String(request.params.arguments?.selector);
        const value = String(request.params.arguments?.value);
        await p.fill(selector, value);
        return {
          content: [{ type: 'text', text: `Filled ${selector} with value` }],
        };
      }
      case 'evaluate': {
        const script = String(request.params.arguments?.script);
        const result = await p.evaluate(script);
        return {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        };
      }
      default:
        throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${request.params.name}`);
    }
  } catch (error: any) {
    return {
      content: [{ type: 'text', text: `Error: ${error.message}` }],
      isError: true,
    };
  }
});

async function run() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

run().catch((_error) => {
  process.exit(1);
});

process.on('SIGINT', async () => {
  if (browser) {
    await browser.close();
  }
  process.exit(0);
});
