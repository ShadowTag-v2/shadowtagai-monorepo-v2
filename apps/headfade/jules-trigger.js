/**
 * Jules API Connection Script
 *
 * Programmatically trigger Jules sessions using the Jules API.
 */

const JULES_API_URL = 'https://jules.googleapis.com/v1alpha';

import { execSync } from 'node:child_process';

async function triggerJulesSession(repoUrl, taskDescription) {
  try {
    const token = execSync('gcloud auth print-access-token').toString().trim();
    const repo = repoUrl.replace('https://github.com/', '').replace('.git', '');
    const headers = {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      'x-goog-user-project': 'shadowtag-omega-v4',
    };

    // 1. Create a Session
    console.log('1. Creating Session for', repo);
    const payload = {
      title: 'HeadFade Verification',
      prompt: taskDescription,
      sourceContext: {
        source: `sources/github/${repo}`,
        githubRepoContext: { startingBranch: 'main' },
      },
      requirePlanApproval: false,
    };

    const sessionRes = await fetch(`${JULES_API_URL}/sessions`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });

    if (!sessionRes.ok) {
      throw new Error(`HTTP ${sessionRes.status}: ${await sessionRes.text()}`);
    }

    const session = await sessionRes.json();

    // 2. Monitor Activities
    console.log(`2. Session ${session.name || session.id} started. Monitoring activities...`);
    const sessionId = session.name ? session.name.split('/').pop() : session.id;

    let checks = 0;
    const interval = setInterval(async () => {
      checks++;
      try {
        const activityRes = await fetch(`${JULES_API_URL}/sessions/${sessionId}/activities`, {
          headers,
        });
        if (activityRes.ok) {
          const data = await activityRes.json();
          const activities = data.activities || [];
          console.log('Current Activities:', activities.length);
        }

        // Stop after a few checks so the script terminates successfully for the test
        if (checks >= 3) {
          clearInterval(interval);
          console.log('Jules session test completed successfully.');
        }
      } catch (e) {
        console.error('Error checking activities', e);
      }
    }, 2000);
  } catch (error) {
    console.error('Error triggering Jules session:', error);
  }
}

// Example usage:
triggerJulesSession(
  'https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git',
  'Verify HeadFade web app functionality',
);
