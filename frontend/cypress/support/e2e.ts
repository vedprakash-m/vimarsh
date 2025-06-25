// ***********************************************************
// This example support/e2e.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Configure Cypress for spiritual content testing
beforeEach(() => {
  // Set up consistent viewport for spiritual interface testing
  cy.viewport(1280, 720)
  
  // Mock API responses for predictable testing
  cy.intercept('POST', '**/api/spiritual-guidance', { fixture: 'spiritual-response.json' }).as('getSpiritualGuidance')
  cy.intercept('GET', '**/api/health', { statusCode: 200, body: { status: 'healthy' } }).as('healthCheck')
})

// Global error handling for spiritual content tests
Cypress.on('uncaught:exception', (err, runnable) => {
  // Don't fail tests on unhandled promise rejections from voice APIs
  if (err.message.includes('speech') || err.message.includes('audio')) {
    return false
  }
  return true
})
