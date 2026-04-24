describe('Cor.Cursor VDI Telemetry Validation', () => {
  it('Should successfully connect to the A2UI Matrix and render telemetry streams', () => {
    // 1. Visit the local Tauri React Server
    cy.visit('/');

    // 2. Validate the CISO Dashboard is rendered
    cy.contains('ATP 5-19 SHIELD : PIPELINE TELEMETRY').should('be.visible');

    // 3. Wait for the A2UI SSE Stream to resolve logic
    cy.contains('Aggregating Swarm Telemetry...').should('exist');

    // 4. Validate Native Streaming resolution
    // The SSE payload should push Layer 14 instantly via the Backend Python Matrix
    cy.contains('Layer 14', { timeout: 10000 }).should('be.visible');
    cy.contains('66 FAILURES MITIGATED').should('exist');

    // Natively hold the view for a moment to record the matrix UI in the .mp4 artifact
    cy.wait(2000);
  });
});
