/**
 * Ethical Crawler Tool
 *
 * Implements ethical web crawling with robots.txt compliance,
 * rate limiting, and transparent user agent identification.
 *
 * Part of PNKLN Core Stack™ Intelligence Layer
 */

import { tool } from "@anthropic-ai/claude-agent-sdk";
import fetch from "node-fetch";
import robotsParser from "robots-parser";

// In-memory cache for robots.txt rules
const robotsCache = new Map();
const CACHE_TTL = 3600 * 1000; // 1 hour

// Rate limiting state
const lastRequestTime = new Map();

/**
 * Parse and cache robots.txt for a domain
 */
async function getRobotRules(url) {
  const urlObj = new URL(url);
  const domain = `${urlObj.protocol}//${urlObj.host}`;
  const robotsUrl = `${domain}/robots.txt`;

  // Check cache
  const cached = robotsCache.get(domain);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.robots;
  }

  try {
    const response = await fetch(robotsUrl, {
      headers: {
        "User-Agent": "PNKLN-Intelligence-Bot/1.0 (+https://pnkln.ai/bot)",
      },
      timeout: 5000,
    });

    const robotsTxt = await response.text();
    const robots = robotsParser(robotsUrl, robotsTxt);

    // Cache the rules
    robotsCache.set(domain, {
      robots,
      timestamp: Date.now(),
    });

    return robots;
  } catch (error) {
    console.warn(`Failed to fetch robots.txt for ${domain}:`, error.message);
    // Return permissive default if robots.txt not available
    return robotsParser(robotsUrl, "User-agent: *\nAllow: /");
  }
}

/**
 * Check if URL is allowed by robots.txt
 */
async function isAllowed(url, userAgent = "PNKLN-Intelligence-Bot") {
  const robots = await getRobotRules(url);
  return robots.isAllowed(url, userAgent);
}

/**
 * Get crawl delay for a domain
 */
async function getCrawlDelay(url, defaultDelay = 1000) {
  const robots = await getRobotRules(url);
  const delay = robots.getCrawlDelay("PNKLN-Intelligence-Bot");
  return (delay || defaultDelay / 1000) * 1000; // Convert to milliseconds
}

/**
 * Enforce rate limiting
 */
async function enforceRateLimit(url, customDelay = null) {
  const urlObj = new URL(url);
  const domain = `${urlObj.protocol}//${urlObj.host}`;

  const delay = customDelay || (await getCrawlDelay(url));
  const lastRequest = lastRequestTime.get(domain);

  if (lastRequest) {
    const timeSinceLastRequest = Date.now() - lastRequest;
    if (timeSinceLastRequest < delay) {
      const waitTime = delay - timeSinceLastRequest;
      await new Promise((resolve) => setTimeout(resolve, waitTime));
    }
  }

  lastRequestTime.set(domain, Date.now());
}

export const ethicalCrawlerTool = tool({
  name: "ethical_crawler",
  description: "Ethically crawl web sources with robots.txt compliance and rate limiting",
  parameters: {
    type: "object",
    properties: {
      url: {
        type: "string",
        description: "The URL to crawl",
      },
      respectRobots: {
        type: "boolean",
        description: "Whether to respect robots.txt (default: true)",
        default: true,
      },
      customDelay: {
        type: "number",
        description: "Custom delay in milliseconds (overrides robots.txt crawl-delay)",
      },
      userAgent: {
        type: "string",
        description: "Custom user agent string",
        default: "PNKLN-Intelligence-Bot/1.0 (+https://pnkln.ai/bot)",
      },
      maxRetries: {
        type: "number",
        description: "Maximum number of retries on failure",
        default: 3,
      },
      timeout: {
        type: "number",
        description: "Request timeout in milliseconds",
        default: 30000,
      },
    },
    required: ["url"],
  },
  execute: async ({
    url,
    respectRobots = true,
    customDelay = null,
    userAgent = "PNKLN-Intelligence-Bot/1.0 (+https://pnkln.ai/bot)",
    maxRetries = 3,
    timeout = 30000,
  }) => {
    const result = {
      url,
      timestamp: new Date().toISOString(),
      allowed: true,
      crawlDelay: null,
      content: null,
      metadata: {},
      ethical: {
        robotsChecked: respectRobots,
        rateLimited: true,
        userAgent,
      },
    };

    try {
      // Step 1: Check robots.txt compliance
      if (respectRobots) {
        const allowed = await isAllowed(url, userAgent);
        result.allowed = allowed;

        if (!allowed) {
          return {
            success: false,
            error: "URL disallowed by robots.txt",
            data: result,
            metadata: {
              ethical: true,
              reason: "robots-txt-disallow",
            },
          };
        }

        result.crawlDelay = await getCrawlDelay(url);
      }

      // Step 2: Enforce rate limiting
      await enforceRateLimit(url, customDelay);

      // Step 3: Fetch content with retries
      let lastError = null;
      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          const response = await fetch(url, {
            headers: {
              "User-Agent": userAgent,
              Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
              "Accept-Language": "en-US,en;q=0.5",
              DNT: "1",
            },
            timeout,
            redirect: "follow",
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          const contentType = response.headers.get("content-type") || "";
          result.content = await response.text();
          result.metadata = {
            statusCode: response.status,
            contentType,
            contentLength: result.content.length,
            finalUrl: response.url,
            attempt,
          };

          return {
            success: true,
            data: result,
            metadata: {
              ethical: true,
              robotsCompliant: respectRobots,
              rateLimited: true,
              attempts: attempt,
            },
          };
        } catch (error) {
          lastError = error;
          if (attempt < maxRetries) {
            // Exponential backoff
            const backoffTime = 2 ** attempt * 1000;
            await new Promise((resolve) => setTimeout(resolve, backoffTime));
          }
        }
      }

      // All retries failed
      return {
        success: false,
        error: `Failed after ${maxRetries} attempts: ${lastError.message}`,
        data: result,
        metadata: {
          ethical: true,
          attempts: maxRetries,
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        data: result,
        metadata: {
          ethical: true,
          robotsCompliant: respectRobots,
        },
      };
    }
  },
});

export default ethicalCrawlerTool;
