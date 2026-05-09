import { jules } from '@google-labs-code/jules-sdk';
import { stitch } from '@google-labs-code/stitch-sdk';

async function dispatchCloudDelegation(intentStr: string, domain: string) {
  console.log(`⚡ [Claude Opus 4.6] Archon Delegating to Cloud Agents for domain: ${domain}...`);
  if (domain === "ui" || domain === "fullstack") {
      await stitch.run({ prompt: intentStr, model: 'Claude Opus 4.6', source: { github: 'shadowtag-omega-v4/repo', baseBranch: 'main' } });
  }
  if (domain === "backend" || domain === "fullstack") {
      await jules.run({ prompt: intentStr, model: 'Claude Opus 4.6', source: { github: 'shadowtag-omega-v4/repo', baseBranch: 'main' } });
  }
}
dispatchCloudDelegation(process.argv[2], process.argv[3] || 'fullstack');
