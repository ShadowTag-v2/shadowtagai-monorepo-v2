# User Researcher - Usage Examples

This document provides detailed examples of how to use the User Researcher Product Strategy service.

## Table of Contents

1. [Basic Session Tracking](#basic-session-tracking)
2. [Advanced Flow Analysis](#advanced-flow-analysis)
3. [Pain Point Detection](#pain-point-detection)
4. [Generating Recommendations](#generating-recommendations)
5. [Feedback Collection](#feedback-collection)
6. [Flow Optimization](#flow-optimization)
7. [Real-World Scenarios](#real-world-scenarios)

## Basic Session Tracking

### Example 1: Track a Simple User Journey

```typescript
import { userResearcherService } from './dist/index.js';

async function trackUserJourney() {
  // 1. Create a new session
  const sessionResp = await userResearcherService.handleRequest('POST', '/api/sessions', {
    body: { userId: 'user-789' }
  });

  const sessionId = sessionResp.data.id;

  // 2. Track page view
  await userResearcherService.handleRequest('POST', '/api/sessions/:sessionId/events', {
    params: { sessionId },
    body: {
      sessionId,
      timestamp: new Date(),
      eventType: 'page_view',
      page: '/home'
    }
  });

  // 3. Track navigation
  await userResearcherService.handleRequest('POST', '/api/sessions/:sessionId/events', {
    params: { sessionId },
    body: {
      sessionId,
      timestamp: new Date(),
      eventType: 'navigation',
      page: '/products',
      previousPage: '/home'
    }
  });

  // 4. Track click on product
  await userResearcherService.handleRequest('POST', '/api/sessions/:sessionId/events', {
    params: { sessionId },
    body: {
      sessionId,
      timestamp: new Date(),
      eventType: 'click',
      page: '/products',
      elementId: 'product-123',
      elementType: 'button'
    }
  });

  // 5. End session (goal completed)
  await userResearcherService.handleRequest('POST', '/api/sessions/:sessionId/end', {
    params: { sessionId },
    body: { completedGoal: true }
  });

  console.log('User journey tracked successfully!');
}
```

### Example 2: Track a Failed Checkout Flow

```typescript
async function trackFailedCheckout() {
  const sessionResp = await userResearcherService.handleRequest('POST', '/api/sessions', {
    body: { userId: 'user-456' }
  });

  const sessionId = sessionResp.data.id;

  // User navigates to checkout
  await userResearcherService.handleRequest('POST', '/api/sessions/:sessionId/events', {
    params: { sessionId },
    body: {
      sessionId,
      timestamp: new Date(),
      eventType: 'page_view',
      page: '/checkout'
    }
  });

  // User focuses on payment form
  await userResearcherService.handleRequest('POST', '/api/sessions/:sessionId/events', {
    params: { sessionId },
    body: {
      sessionId,
      timestamp: new Date(),
      eventType: 'input_focus',
      page: '/checkout',
      elementId: 'payment-form',
      elementType: 'form'
    }
  });

  // User encounters error
  await userResearcherService.handleRequest('POST', '/api/sessions/:sessionId/events', {
    params: { sessionId },
    body: {
      sessionId,
      timestamp: new Date(),
      eventType: 'error',
      page: '/checkout',
      metadata: {
        errorMessage: 'Invalid credit card number',
        errorCode: 'PAYMENT_001'
      }
    }
  });

  // Multiple retry attempts (rage clicking)
  for (let i = 0; i < 5; i++) {
    await userResearcherService.handleRequest('POST', '/api/sessions/:sessionId/events', {
      params: { sessionId },
      body: {
        sessionId,
        timestamp: new Date(Date.now() + i * 1000),
        eventType: 'click',
        page: '/checkout',
        elementId: 'submit-payment',
        elementType: 'button'
      }
    });
  }

  // User exits (rage quit)
  await userResearcherService.handleRequest('POST', '/api/sessions/:sessionId/events', {
    params: { sessionId },
    body: {
      sessionId,
      timestamp: new Date(),
      eventType: 'exit',
      page: '/checkout'
    }
  });

  // End session (goal NOT completed)
  await userResearcherService.handleRequest('POST', '/api/sessions/:sessionId/end', {
    params: { sessionId },
    body: { completedGoal: false }
  });

  console.log('Failed checkout tracked!');
}
```

## Advanced Flow Analysis

### Example 3: Comprehensive Flow Analysis

```typescript
async function analyzeUserFlows() {
  // Create some test sessions first
  await createTestSessions();

  // Perform comprehensive analysis
  const analysis = await userResearcherService.handleRequest('POST', '/api/analysis/flow', {
    body: {
      timeRange: {
        start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // Last 7 days
        end: new Date()
      },
      includeRecommendations: true
    }
  });

  const { data } = analysis;

  console.log('\n=== Flow Analysis Results ===');
  console.log(`Total Sessions: ${data.totalSessions}`);
  console.log(`Total Users: ${data.totalUsers}`);
  console.log(`Completion Rate: ${(data.flowMetrics.completionRate * 100).toFixed(2)}%`);
  console.log(`Drop-off Rate: ${(data.flowMetrics.dropOffRate * 100).toFixed(2)}%`);
  console.log(`Avg Session Duration: ${(data.flowMetrics.averageSessionDuration / 1000).toFixed(2)}s`);

  console.log('\n=== Most Common Path ===');
  console.log(data.flowMetrics.mostCommonPath.join(' → '));

  console.log('\n=== Top Exit Pages ===');
  data.flowMetrics.exitPages.slice(0, 5).forEach(exit => {
    console.log(`${exit.page}: ${exit.count} exits (${exit.percentage.toFixed(2)}%)`);
  });

  console.log('\n=== Pain Points Detected ===');
  data.painPoints.forEach(pp => {
    console.log(`[${pp.severity.toUpperCase()}] ${pp.type} on ${pp.page}`);
    console.log(`  ${pp.description}`);
    console.log(`  Affected: ${pp.affectedUsers} users, Frequency: ${pp.frequency}`);
  });

  console.log('\n=== Top Recommendations ===');
  data.recommendations.slice(0, 3).forEach(rec => {
    console.log(`\n${rec.title} [${rec.priority}]`);
    console.log(`Category: ${rec.category}`);
    console.log(`Effort: ${rec.implementation.effort}, Impact: ${rec.implementation.impact}`);
    console.log(`Expected Outcome: ${rec.expectedOutcome}`);
  });
}
```

## Pain Point Detection

### Example 4: Detect and Categorize Pain Points

```typescript
async function detectAndCategorizePainPoints() {
  // Detect pain points
  const painPoints = await userResearcherService.handleRequest(
    'POST',
    '/api/analysis/pain-points'
  );

  // Group by severity
  const bySeverity = painPoints.data.reduce((acc, pp) => {
    if (!acc[pp.severity]) acc[pp.severity] = [];
    acc[pp.severity].push(pp);
    return acc;
  }, {});

  console.log('\n=== Pain Points by Severity ===');

  ['critical', 'high', 'medium', 'low'].forEach(severity => {
    if (bySeverity[severity]) {
      console.log(`\n${severity.toUpperCase()} (${bySeverity[severity].length})`);
      bySeverity[severity].forEach(pp => {
        console.log(`  - ${pp.type} on ${pp.page}: ${pp.description}`);
      });
    }
  });
}
```

### Example 5: Rage Quit Analysis

```typescript
async function analyzeRageQuits() {
  const rageQuitAnalysis = await userResearcherService.handleRequest(
    'GET',
    '/api/analysis/rage-quits'
  );

  console.log('\n=== Rage Quit Analysis ===');
  console.log(rageQuitAnalysis.data.analysis);

  console.log('\n=== Pages with Highest Rage Quit Rates ===');
  rageQuitAnalysis.data.rageQuitPages
    .sort((a, b) => b.percentage - a.percentage)
    .slice(0, 5)
    .forEach(page => {
      console.log(`${page.page}: ${page.count} rage quits (${page.percentage.toFixed(2)}%)`);
    });
}
```

## Generating Recommendations

### Example 6: Get Prioritized Recommendations

```typescript
async function getPrioritizedRecommendations() {
  // Get critical priority recommendations
  const critical = await userResearcherService.handleRequest(
    'GET',
    '/api/recommendations',
    { query: { priority: 'critical' } }
  );

  console.log('\n=== CRITICAL PRIORITY FIXES ===');
  critical.data.forEach((rec, idx) => {
    console.log(`\n${idx + 1}. ${rec.title}`);
    console.log(`   Category: ${rec.category}`);
    console.log(`   Description: ${rec.description}`);
    console.log(`   Implementation:`);
    console.log(`     - Effort: ${rec.implementation.effort}`);
    console.log(`     - Impact: ${rec.implementation.impact}`);
    console.log(`   Steps:`);
    rec.implementation.steps.forEach((step, i) => {
      console.log(`     ${i + 1}. ${step}`);
    });

    if (rec.implementation.codeChanges) {
      console.log(`   Code Changes:`);
      rec.implementation.codeChanges.forEach(change => {
        console.log(`     - ${change.file}: ${change.description}`);
      });
    }
  });
}
```

## Feedback Collection

### Example 7: Collect and Analyze Feedback

```typescript
async function collectAndAnalyzeFeedback() {
  // Submit various feedback
  const feedbacks = [
    {
      sessionId: 'session-1',
      type: 'usability_issue',
      page: '/checkout',
      message: 'The payment form is confusing and hard to understand',
      rating: 2,
      sentiment: 'negative'
    },
    {
      sessionId: 'session-2',
      type: 'bug_report',
      page: '/products',
      message: 'Search results not showing up correctly',
      rating: 1,
      sentiment: 'negative'
    },
    {
      sessionId: 'session-3',
      type: 'feature_request',
      page: '/account',
      message: 'Would love to see saved payment methods',
      rating: 4,
      sentiment: 'positive'
    }
  ];

  for (const feedback of feedbacks) {
    await userResearcherService.handleRequest('POST', '/api/feedback', {
      body: feedback
    });
  }

  // Analyze all feedback
  const analysis = await userResearcherService.handleRequest(
    'POST',
    '/api/analysis/feedback'
  );

  console.log('\n=== Feedback Analysis ===');
  console.log(analysis.data.summary);

  console.log('\n=== Common Themes ===');
  analysis.data.themes.forEach(theme => {
    console.log(`${theme.theme} (${theme.count} mentions) - ${theme.sentiment}`);
  });

  console.log('\n=== Priority Issues ===');
  analysis.data.priorityIssues.forEach((issue, idx) => {
    console.log(`${idx + 1}. ${issue}`);
  });
}
```

## Flow Optimization

### Example 8: Optimize Checkout Flow

```typescript
async function optimizeCheckoutFlow() {
  const currentFlow = [
    '/products',
    '/product-details',
    '/cart',
    '/shipping-info',
    '/payment-info',
    '/review-order',
    '/confirmation'
  ];

  const optimization = await userResearcherService.handleRequest(
    'POST',
    '/api/analysis/optimize-flow',
    {
      body: {
        currentFlow,
        goalPage: '/confirmation'
      }
    }
  );

  console.log('\n=== Flow Optimization Results ===');
  console.log('\nCurrent Flow:');
  console.log(currentFlow.join(' → '));

  console.log('\nOptimized Flow:');
  console.log(optimization.data.optimizedFlow.join(' → '));

  console.log('\nRemoved Steps:');
  optimization.data.removedSteps.forEach(step => {
    console.log(`  - ${step}`);
  });

  console.log('\nAdded Steps:');
  optimization.data.addedSteps.forEach(step => {
    console.log(`  + ${step}`);
  });

  console.log('\nRationale:');
  console.log(optimization.data.rationale);
}
```

## Real-World Scenarios

### Example 9: E-commerce Site Analysis

```typescript
async function ecommerceAnalysis() {
  console.log('=== E-commerce Site UX Analysis ===\n');

  // 1. Track multiple user sessions (simulate real traffic)
  console.log('1. Tracking user sessions...');
  await simulateEcommerceTraffic(50); // 50 sessions

  // 2. Detect pain points
  console.log('2. Detecting pain points...');
  const painPoints = await userResearcherService.handleRequest(
    'POST',
    '/api/analysis/pain-points'
  );
  console.log(`   Found ${painPoints.data.length} pain points`);

  // 3. Identify rage quit pages
  console.log('3. Analyzing rage quits...');
  const rageQuits = await userResearcherService.handleRequest(
    'GET',
    '/api/analysis/rage-quits'
  );
  console.log(`   ${rageQuits.data.rageQuitPages.length} pages identified`);

  // 4. Generate recommendations
  console.log('4. Generating recommendations...');
  const recs = await userResearcherService.handleRequest(
    'POST',
    '/api/recommendations'
  );
  console.log(`   ${recs.data.length} recommendations generated`);

  // 5. Get analytics
  console.log('5. Getting analytics...');
  const analytics = await userResearcherService.handleRequest(
    'GET',
    '/api/analytics'
  );

  console.log('\n=== Summary ===');
  console.log(`Sessions: ${analytics.data.totalSessions}`);
  console.log(`Users: ${analytics.data.totalUsers}`);
  console.log(`Pain Points: ${analytics.data.totalPainPoints} (${analytics.data.criticalPainPoints} critical)`);
  console.log(`Recommendations: ${analytics.data.totalRecommendations}`);

  // 6. Display top 3 critical issues with fixes
  const criticalRecs = recs.data
    .filter(r => r.priority === 'critical')
    .slice(0, 3);

  console.log('\n=== Top 3 Critical Issues to Fix ===');
  criticalRecs.forEach((rec, idx) => {
    console.log(`\n${idx + 1}. ${rec.title}`);
    console.log(`   Impact: ${rec.implementation.impact} | Effort: ${rec.implementation.effort}`);
    console.log(`   Fix: ${rec.implementation.steps[0]}`);
  });
}
```

### Example 10: SaaS Application Onboarding Analysis

```typescript
async function onboardingAnalysis() {
  console.log('=== SaaS Onboarding Flow Analysis ===\n');

  const onboardingFlow = [
    '/signup',
    '/verify-email',
    '/welcome',
    '/setup-profile',
    '/choose-plan',
    '/payment',
    '/dashboard'
  ];

  // Simulate onboarding sessions
  await simulateOnboardingSessions(30);

  // Analyze the flow
  const analysis = await userResearcherService.handleRequest(
    'POST',
    '/api/analysis/flow',
    {
      body: {
        pages: onboardingFlow,
        includeRecommendations: true
      }
    }
  );

  console.log('=== Onboarding Metrics ===');
  console.log(`Completion Rate: ${(analysis.data.flowMetrics.completionRate * 100).toFixed(2)}%`);
  console.log(`Drop-off Rate: ${(analysis.data.flowMetrics.dropOffRate * 100).toFixed(2)}%`);

  // Find where users drop off most
  const dropOffPoints = analysis.data.flowMetrics.exitPages
    .filter(exit => onboardingFlow.includes(exit.page))
    .sort((a, b) => b.percentage - a.percentage);

  console.log('\n=== Top Drop-off Points ===');
  dropOffPoints.slice(0, 3).forEach(point => {
    console.log(`${point.page}: ${point.percentage.toFixed(2)}% of users exit here`);
  });

  // Optimize the flow
  const optimization = await userResearcherService.handleRequest(
    'POST',
    '/api/analysis/optimize-flow',
    {
      body: {
        currentFlow: onboardingFlow,
        goalPage: '/dashboard'
      }
    }
  );

  console.log('\n=== Optimized Onboarding Flow ===');
  console.log(optimization.data.optimizedFlow.join(' → '));
  console.log('\nOptimization Rationale:');
  console.log(optimization.data.rationale);
}
```

## Running the Examples

To run these examples:

1. Build the project:

   ```bash
   npm run build
   ```

2. Create a file `examples.ts` in the project root with the examples you want to run

3. Run with Node.js:

   ```bash
   node -r ts-node/register examples.ts
   ```

Or import the service in your own application and use the examples as reference.
