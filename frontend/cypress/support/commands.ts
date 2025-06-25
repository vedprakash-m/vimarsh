// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

/// <reference types="cypress" />

declare namespace Cypress {
  interface Chainable {
    /**
     * Custom command to ask a spiritual question
     * @example cy.askSpiritualQuestion('What is dharma?')
     */
    askSpiritualQuestion(question: string): Chainable<Element>
    
    /**
     * Custom command to verify spiritual response format
     * @example cy.verifySpiritualResponse()
     */
    verifySpiritualResponse(): Chainable<Element>
    
    /**
     * Custom command to check cultural sensitivity
     * @example cy.checkCulturalSensitivity()
     */
    checkCulturalSensitivity(): Chainable<Element>
    
    /**
     * Custom command to test voice interface
     * @example cy.testVoiceInput('What is moksha?')
     */
    testVoiceInput(query: string): Chainable<Element>
    
    /**
     * Custom command to switch language
     * @example cy.switchLanguage('Hindi')
     */
    switchLanguage(language: 'English' | 'Hindi'): Chainable<Element>
    
    /**
     * Custom command to verify citation format
     * @example cy.verifyCitations()
     */
    verifyCitations(): Chainable<Element>
  }
}

Cypress.Commands.add('askSpiritualQuestion', (question: string) => {
  cy.get('[data-testid="spiritual-input"]', { timeout: 10000 })
    .should('be.visible')
    .clear()
    .type(question)
  
  cy.get('[data-testid="send-button"]')
    .should('be.enabled')
    .click()
})

Cypress.Commands.add('verifySpiritualResponse', () => {
  // Wait for response to appear
  cy.get('[data-testid="spiritual-response"]', { timeout: 15000 })
    .should('be.visible')
  
  // Verify response contains appropriate spiritual language
  cy.get('[data-testid="response-text"]')
    .should('satisfy', (el) => {
      const text = el.text().toLowerCase()
      return text.includes('dear') || text.includes('beloved') || text.includes('devotee')
    })
  
  // Verify no inappropriate casual language
  cy.get('[data-testid="response-text"]')
    .should('not.contain.text', 'cool')
    .should('not.contain.text', 'awesome')
    .should('not.contain.text', 'hey')
})

Cypress.Commands.add('checkCulturalSensitivity', () => {
  // Check for proper Sanskrit terms
  cy.get('body').then(($body) => {
    if ($body.text().includes('dharma') || $body.text().includes('karma')) {
      // Sanskrit terms should be properly formatted
      cy.get('[data-testid="response-text"]')
        .should('satisfy', (el) => {
          const text = el.text()
          return /dharma|karma|moksha|yoga|Arjuna|Krishna/.test(text)
        })
    }
  })
  
  // Verify no culturally inappropriate content
  cy.get('[data-testid="response-text"]')
    .should('not.contain.text', 'weird')
    .should('not.contain.text', 'strange')
    .should('not.contain.text', 'exotic')
})

Cypress.Commands.add('testVoiceInput', (query: string) => {
  // Mock voice input since we can't actually speak in tests
  cy.get('[data-testid="voice-button"]')
    .should('be.visible')
    .click()
  
  // Simulate voice input by directly setting the input value
  cy.get('[data-testid="spiritual-input"]')
    .invoke('val', query)
    .trigger('input')
  
  cy.get('[data-testid="send-button"]').click()
})

Cypress.Commands.add('switchLanguage', (language: 'English' | 'Hindi') => {
  cy.get('[data-testid="language-selector"]')
    .should('be.visible')
    .click()
  
  cy.get(`[data-testid="language-option-${language.toLowerCase()}"]`)
    .click()
  
  // Verify language change
  cy.get('[data-testid="language-indicator"]')
    .should('contain.text', language)
})

Cypress.Commands.add('verifyCitations', () => {
  cy.get('[data-testid="citations"]')
    .should('be.visible')
  
  // Verify citation format (e.g., "Bhagavad Gita 2.47")
  cy.get('[data-testid="citation-item"]')
    .should('satisfy', (el) => {
      const text = el.text()
      return /Bhagavad Gita|Mahabharata|Srimad Bhagavatam/.test(text) &&
             /\d+\.\d+|\d+:\d+/.test(text)
    })
})
