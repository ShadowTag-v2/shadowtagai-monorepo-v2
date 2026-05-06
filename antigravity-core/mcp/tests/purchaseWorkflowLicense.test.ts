import { purchaseWorkflowLicense } from '../src/tools/purchase_workflow_license.js';

// Mock dependencies
jest.mock('stripe', () => {
  return jest.fn().mockImplementation(() => ({
    paymentIntents: {
      create: jest.fn().mockImplementation((params) => {
        if (params.amount >= 299) {
          return Promise.resolve({ status: 'succeeded' });
        }
        return Promise.resolve({ status: 'failed' });
      })
    }
  }));
});

jest.mock('../src/utils/firebase-data-connect.js', () => ({
  executeGrantLicenseMutation: jest.fn().mockResolvedValue({ success: true })
}));

describe('purchaseWorkflowLicense', () => {
  it('should fail with invalid agent token', async () => {
    const result = await purchaseWorkflowLicense('demo-123', 'invalid_token', 'test_auth');
    expect(result.content[0].text).toContain('Transaction Failed: Invalid agent wallet token.');
  });

  it('should succeed with valid token and sufficient funds', async () => {
    const result = await purchaseWorkflowLicense('demo-123', 'agnt_valid_token', 'test_auth');
    expect(result.content[0].text).toContain('License Granted. Workflow data unlocked for agent');
  });
});
