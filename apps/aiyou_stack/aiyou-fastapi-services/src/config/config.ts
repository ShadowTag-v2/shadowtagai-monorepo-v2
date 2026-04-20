export interface Config {
  anthropic: {
    apiKey: string;
    model: string;
  };
  server: {
    port: number;
    host: string;
  };
  analytics: {
    retentionDays: number;
    minSessionsForAnalysis: number;
  };
}

export const config: Config = {
  anthropic: {
    apiKey: process.env.ANTHROPIC_API_KEY || '',
    model: 'claude-sonnet-4-5-20250929',
  },
  server: {
    port: parseInt(process.env.PORT || '3000'),
    host: process.env.HOST || 'localhost',
  },
  analytics: {
    retentionDays: parseInt(process.env.RETENTION_DAYS || '30'),
    minSessionsForAnalysis: parseInt(process.env.MIN_SESSIONS || '10'),
  },
};
