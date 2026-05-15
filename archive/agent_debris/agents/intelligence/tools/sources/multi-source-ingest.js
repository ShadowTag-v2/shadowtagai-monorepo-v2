/**
 * Multi-Source Ingestion Tool
 *
 * Handles data collection from multiple sources:
 * - YouTube (via API)
 * - Twitter/X (via API)
 * - News sites (RSS/Atom feeds, web scraping)
 * - Reddit (via API)
 * - Generic RSS feeds
 *
 * Part of PNKLN Core Stack™ Intelligence Layer
 */

import { tool } from '@anthropic-ai/claude-agent-sdk';
import ethicalCrawlerTool from './ethical-crawler.js';

/**
 * Source-specific ingestion handlers
 */
const sourceHandlers = {
  youtube: async (config) => {
    // YouTube Data API v3 integration
    const { apiKey, channelId, maxResults = 50, publishedAfter } = config;

    const params = new URLSearchParams({
      part: 'snippet,contentDetails,statistics',
      channelId,
      maxResults,
      order: 'date',
      type: 'video',
      key: apiKey,
    });

    if (publishedAfter) {
      params.append('publishedAfter', publishedAfter);
    }

    const url = `https://www.googleapis.com/youtube/v3/search?${params}`;

    try {
      const response = await fetch(url);
      const data = await response.json();

      return {
        source: 'youtube',
        items: data.items || [],
        metadata: {
          totalResults: data.pageInfo?.totalResults || 0,
          resultsPerPage: data.pageInfo?.resultsPerPage || 0,
          nextPageToken: data.nextPageToken,
        },
      };
    } catch (error) {
      throw new Error(`YouTube ingestion failed: ${error.message}`);
    }
  },

  twitter: async (config) => {
    // Twitter API v2 integration
    const { bearerToken, query, maxResults = 100, startTime } = config;

    const params = new URLSearchParams({
      query,
      max_results: maxResults,
      'tweet.fields': 'created_at,author_id,public_metrics,entities',
      'user.fields': 'username,verified',
      expansions: 'author_id',
    });

    if (startTime) {
      params.append('start_time', startTime);
    }

    const url = `https://api.twitter.com/2/tweets/search/recent?${params}`;

    try {
      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${bearerToken}`,
          'User-Agent': 'PNKLN-Intelligence-Bot/1.0',
        },
      });

      const data = await response.json();

      return {
        source: 'twitter',
        items: data.data || [],
        metadata: {
          resultCount: data.meta?.result_count || 0,
          nextToken: data.meta?.next_token,
        },
      };
    } catch (error) {
      throw new Error(`Twitter ingestion failed: ${error.message}`);
    }
  },

  reddit: async (config) => {
    // Reddit API integration
    const { subreddit, limit = 100, timeframe = 'day' } = config;

    const url = `https://www.reddit.com/r/${subreddit}/top.json?t=${timeframe}&limit=${limit}`;

    try {
      const response = await fetch(url, {
        headers: {
          'User-Agent': 'PNKLN-Intelligence-Bot/1.0 (+https://pnkln.ai/bot)',
        },
      });

      const data = await response.json();
      const posts = data.data?.children || [];

      return {
        source: 'reddit',
        items: posts.map((p) => p.data),
        metadata: {
          subreddit,
          timeframe,
          count: posts.length,
        },
      };
    } catch (error) {
      throw new Error(`Reddit ingestion failed: ${error.message}`);
    }
  },

  rss: async (config) => {
    // RSS/Atom feed parsing
    const { feedUrl } = config;

    try {
      // Use ethical crawler for RSS feeds
      const crawlResult = await ethicalCrawlerTool.execute({
        url: feedUrl,
        respectRobots: true,
      });

      if (!crawlResult.success) {
        throw new Error(crawlResult.error);
      }

      // Simple RSS parsing (in production, use a proper RSS parser library)
      const content = crawlResult.data.content;
      const items = [];

      // Extract items from RSS/Atom
      const itemRegex = /<item>[\s\S]*?<\/item>/gi;
      const matches = content.match(itemRegex) || [];

      for (const match of matches) {
        const titleMatch = match.match(/<title>(.*?)<\/title>/i);
        const linkMatch = match.match(/<link>(.*?)<\/link>/i);
        const descMatch = match.match(/<description>(.*?)<\/description>/i);
        const pubDateMatch = match.match(/<pubDate>(.*?)<\/pubDate>/i);

        items.push({
          title: titleMatch ? titleMatch[1] : null,
          link: linkMatch ? linkMatch[1] : null,
          description: descMatch ? descMatch[1] : null,
          pubDate: pubDateMatch ? pubDateMatch[1] : null,
        });
      }

      return {
        source: 'rss',
        items,
        metadata: {
          feedUrl,
          count: items.length,
        },
      };
    } catch (error) {
      throw new Error(`RSS ingestion failed: ${error.message}`);
    }
  },

  news: async (config) => {
    // News API or web scraping
    const { apiKey, query, sources, language = 'en', pageSize = 100 } = config;

    if (apiKey) {
      // Use News API
      const params = new URLSearchParams({
        q: query,
        language,
        pageSize,
        apiKey,
      });

      if (sources) {
        params.append('sources', sources);
      }

      const url = `https://newsapi.org/v2/everything?${params}`;

      try {
        const response = await fetch(url);
        const data = await response.json();

        return {
          source: 'news',
          items: data.articles || [],
          metadata: {
            totalResults: data.totalResults || 0,
            status: data.status,
          },
        };
      } catch (error) {
        throw new Error(`News API ingestion failed: ${error.message}`);
      }
    } else {
      // Fallback to ethical web scraping
      throw new Error('News scraping requires ethical crawler implementation');
    }
  },
};

export const multiSourceIngestTool = tool({
  name: 'multi_source_ingest',
  description:
    'Ingest data from multiple sources (YouTube, Twitter, News, Reddit, RSS) with ethical crawling',
  parameters: {
    type: 'object',
    properties: {
      sources: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            type: {
              type: 'string',
              enum: ['youtube', 'twitter', 'reddit', 'rss', 'news'],
            },
            config: {
              type: 'object',
              description: 'Source-specific configuration',
            },
          },
          required: ['type', 'config'],
        },
        description: 'Array of sources to ingest from',
      },
      timeWindow: {
        type: 'string',
        description: "Time window for data collection (e.g., '24h', '7d')",
        default: '24h',
      },
      maxItemsPerSource: {
        type: 'number',
        description: 'Maximum items to collect per source',
        default: 100,
      },
      deduplication: {
        type: 'boolean',
        description: 'Enable deduplication across sources',
        default: true,
      },
    },
    required: ['sources'],
  },
  execute: async ({
    sources,
    timeWindow = '24h',
    maxItemsPerSource = 100,
    deduplication = true,
  }) => {
    const result = {
      timestamp: new Date().toISOString(),
      timeWindow,
      sources: [],
      summary: {
        totalItems: 0,
        bySource: {},
        errors: [],
      },
    };

    // Process each source
    for (const sourceConfig of sources) {
      const { type, config } = sourceConfig;

      try {
        const handler = sourceHandlers[type];
        if (!handler) {
          throw new Error(`Unknown source type: ${type}`);
        }

        // Add max results limit
        const configWithLimit = {
          ...config,
          maxResults: config.maxResults || maxItemsPerSource,
          limit: config.limit || maxItemsPerSource,
        };

        // Execute source-specific handler
        const sourceResult = await handler(configWithLimit);

        result.sources.push({
          type,
          success: true,
          ...sourceResult,
        });

        result.summary.bySource[type] = sourceResult.items.length;
        result.summary.totalItems += sourceResult.items.length;
      } catch (error) {
        result.sources.push({
          type,
          success: false,
          error: error.message,
          items: [],
        });

        result.summary.errors.push({
          source: type,
          error: error.message,
        });
      }
    }

    // Deduplication (simple title-based for demo)
    if (deduplication && result.sources.length > 1) {
      const allItems = result.sources.flatMap((s) => s.items || []);
      const seen = new Set();
      const uniqueItems = [];

      for (const item of allItems) {
        const key = item.title || item.text || item.id;
        if (key && !seen.has(key)) {
          seen.add(key);
          uniqueItems.push(item);
        }
      }

      result.summary.beforeDedup = result.summary.totalItems;
      result.summary.afterDedup = uniqueItems.length;
      result.summary.duplicatesRemoved = result.summary.totalItems - uniqueItems.length;
    }

    return {
      success: result.summary.errors.length === 0,
      data: result,
      metadata: {
        totalSources: sources.length,
        successfulSources: result.sources.filter((s) => s.success).length,
        totalItems: result.summary.totalItems,
        errors: result.summary.errors.length,
      },
    };
  },
});

export default multiSourceIngestTool;
