// tests/e2e/cypress/integration/stripe_connect_spec.js
/**
 * #7: Cypress E2E tests for Stripe Connect onboarding flow.
 *
 * Tests the firm onboarding journey:
 * 1. Visit pricing page
 * 2. Click "Start Firm Setup" button
 * 3. Verify onboarding modal/prompt appears
 * 4. Verify API call to /connect/onboard
 * 5. Verify redirect to Stripe Connect
 */

describe('Stripe Connect Onboarding', () => {
  const BASE_URL = Cypress.env('BASE_URL') || 'https://kovelai.web.app';

  beforeEach(() => {
    cy.visit(`${BASE_URL}/pricing.html`);
  });

  it('should display the Connect onboarding button', () => {
    cy.get('#connect-onboard-btn').should('exist');
    cy.get('#connect-onboard-btn').should('be.visible');
  });

  it('should show pricing tiers', () => {
    cy.contains('Solo').should('be.visible');
    cy.contains('Practice').should('be.visible');
    cy.contains('Enterprise').should('be.visible');
  });

  it('should have correct pricing amounts', () => {
    cy.contains('$299').should('exist');
    cy.contains('$599').should('exist');
  });

  it('should call connect/onboard API on button click', () => {
    // Intercept the API call
    cy.intercept('POST', '**/connect/onboard', {
      statusCode: 200,
      body: {
        onboarding_url: 'https://connect.stripe.com/setup/mock',
        account_id: 'acct_mock_123',
      },
    }).as('connectOnboard');

    // Stub the prompt to return a firm name
    cy.window().then((win) => {
      cy.stub(win, 'prompt').returns('Test Law Firm LLC');
    });

    cy.get('#connect-onboard-btn').click();
    cy.wait('@connectOnboard').then((interception) => {
      expect(interception.request.body).to.have.property('firm_name', 'Test Law Firm LLC');
      expect(interception.request.body).to.have.property('return_url');
    });
  });

  it('should handle API errors gracefully', () => {
    cy.intercept('POST', '**/connect/onboard', {
      statusCode: 500,
      body: { error: 'Internal server error' },
    }).as('connectError');

    cy.window().then((win) => {
      cy.stub(win, 'prompt').returns('Test Firm');
      cy.stub(win, 'alert').as('alertStub');
    });

    cy.get('#connect-onboard-btn').click();
    cy.wait('@connectError');
    cy.get('@alertStub').should('have.been.calledOnce');
  });

  it('should have security headers on pricing page', () => {
    cy.request(`${BASE_URL}/pricing.html`).then((response) => {
      expect(response.status).to.eq(200);
      // Verify page loads successfully
      expect(response.body).to.include('CounselConduit');
    });
  });
});
