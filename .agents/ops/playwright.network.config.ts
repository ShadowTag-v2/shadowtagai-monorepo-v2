import { defineConfig, devices } from '@playwright/test';
export default defineConfig({ 
  projects: [{ 
    name: 'Reality Check', 
    use: { 
      ...devices['iPhone SE'], 
      offline: false, 
      actionTimeout: 30000, // 30-Second UX Fail Rule (2026 #5)
      launchOptions: { args: ['--force-effective-connection-type=3G'] } // Real network constraint (2026 #8)
    } 
  }] 
});
