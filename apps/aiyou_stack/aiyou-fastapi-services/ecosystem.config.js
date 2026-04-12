// PM2 configuration for Pnkln microservices
// Usage: pnpm pm2:start

module.exports = {
  apps: [
    {
      name: "auth-service",
      script: "pnpm",
      args: "start",
      cwd: "./backend/auth",
      error_file: "./backend/auth/logs/error.log",
      out_file: "./backend/auth/logs/out.log",
      env: {
        NODE_ENV: "development",
        PORT: 3001,
      },
      env_production: {
        NODE_ENV: "production",
        PORT: 3001,
      },
    },
    {
      name: "shadowtag-service",
      script: "pnpm",
      args: "start",
      cwd: "./backend/shadowtag",
      error_file: "./backend/shadowtag/logs/error.log",
      out_file: "./backend/shadowtag/logs/out.log",
      env: {
        NODE_ENV: "development",
        PORT: 3002,
      },
    },
    {
      name: "activeshield-api",
      script: "pnpm",
      args: "start",
      cwd: "./backend/activeshield",
      error_file: "./backend/activeshield/logs/error.log",
      out_file: "./backend/activeshield/logs/out.log",
      env: {
        NODE_ENV: "development",
        PORT: 3003,
      },
    },
    {
      name: "cognitive-stack",
      script: "python",
      args: "-m uvicorn main:app --reload --port 8000",
      cwd: "./backend/cognitive-stack",
      error_file: "./backend/cognitive-stack/logs/error.log",
      out_file: "./backend/cognitive-stack/logs/out.log",
      interpreter: "python3",
    },
    {
      name: "notification-service",
      script: "pnpm",
      args: "start",
      cwd: "./backend/notifications",
      error_file: "./backend/notifications/logs/error.log",
      out_file: "./backend/notifications/logs/out.log",
      env: {
        NODE_ENV: "development",
        PORT: 3004,
      },
    },
    {
      name: "workflow-engine",
      script: "pnpm",
      args: "start",
      cwd: "./backend/workflow",
      error_file: "./backend/workflow/logs/error.log",
      out_file: "./backend/workflow/logs/out.log",
      env: {
        NODE_ENV: "development",
        PORT: 3005,
      },
    },
    {
      name: "analytics-service",
      script: "pnpm",
      args: "start",
      cwd: "./backend/analytics",
      error_file: "./backend/analytics/logs/error.log",
      out_file: "./backend/analytics/logs/out.log",
      env: {
        NODE_ENV: "development",
        PORT: 3006,
      },
    },
  ],
};
