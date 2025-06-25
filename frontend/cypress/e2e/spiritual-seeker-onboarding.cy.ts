/**
 * End-to-end tests for complete spiritual seeker user journey
 * 
 * Tests cover the primary user flows defined in User_Experience.md:
 * - Discovery & Onboarding
 * - First spiritual question experience  
 * - Regular usage patterns
 * - Deep conversation flows
 */

describe('Spiritual Seeker Journey - Discovery & Onboarding', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should complete the full first-time user journey', () => {
    // Phase 1.1: Initial Landing (First Visit)
    cy.get('[data-testid="hero-section"]')
      .should('be.visible')
      .and('contain.text', 'Wisdom from the Divine')
    
    // Verify Lord Krishna imagery and sacred aesthetics
    cy.get('[data-testid="krishna-image"]').should('be.visible')
    cy.get('[data-testid="om-symbol"]').should('be.visible')
    
    // Check for welcoming and culturally appropriate language
    cy.get('body').should('contain.text', 'spiritual journey')
    cy.get('body').should('not.contain.text', 'cool')
    cy.get('body').should('not.contain.text', 'awesome')
    
    // Verify language selection prompt
    cy.get('[data-testid="language-selector"]').should('be.visible')
    
    // Phase 1.2: First Interaction Setup
    cy.get('[data-testid="begin-journey-button"]')
      .should('be.visible')
      .and('contain.text', 'Begin Your Spiritual Journey')
      .click()
    
    // Verify brief introduction appears
    cy.get('[data-testid="introduction-section"]', { timeout: 5000 })
      .should('be.visible')
      .and('contain.text', 'Vimarsh')
    
    // Check example questions are displayed
    cy.get('[data-testid="example-questions"]').should('be.visible')
    cy.get('[data-testid="example-question"]').should('have.length.at.least', 3)
    
    // Verify input methods are available
    cy.get('[data-testid="spiritual-input"]').should('be.visible')
    cy.get('[data-testid="voice-button"]').should('be.visible')
    
    // Optional account creation (should not be mandatory)
    cy.get('body').then(($body) => {
      if ($body.find('[data-testid="account-creation"]').length > 0) {
        cy.get('[data-testid="account-creation"]').should('not.be.visible')
      }
    })
  })

  it('should demonstrate core value with first question', () => {
    // Navigate to main interface
    cy.visit('/')
    cy.get('[data-testid="begin-journey-button"]').click()
    
    // Phase 1.3: First Question Experience
    cy.askSpiritualQuestion('What is the nature of duty?')
    
    // Verify processing indication with spiritual aesthetics
    cy.get('[data-testid="loading-lotus"]', { timeout: 2000 })
      .should('be.visible')
    
    // Wait for and verify spiritual response
    cy.wait('@getSpiritualGuidance')
    cy.verifySpiritualResponse()
    
    // Verify citations are visible and properly formatted
    cy.verifyCitations()
    
    // Check for follow-up suggestions
    cy.get('[data-testid="follow-up-suggestions"]')
      .should('be.visible')
      .find('[data-testid="suggestion-item"]')
      .should('have.length.at.least', 2)
    
    // Verify feedback mechanism
    cy.get('[data-testid="response-feedback"]').should('be.visible')
    cy.get('[data-testid="thumbs-up"]').should('be.visible')
    cy.get('[data-testid="thumbs-down"]').should('be.visible')
  })

  it('should maintain spiritual authenticity throughout onboarding', () => {
    cy.visit('/')
    
    // Check cultural sensitivity throughout the page
    cy.checkCulturalSensitivity()
    
    // Verify no inappropriate casual language
    cy.get('body')
      .should('not.contain.text', 'hey')
      .should('not.contain.text', 'cool')
      .should('not.contain.text', 'awesome')
      .should('not.contain.text', 'dude')
    
    // Verify respectful spiritual language
    cy.get('body').should('satisfy', (body) => {
      const text = body.text().toLowerCase()
      return text.includes('sacred') || 
             text.includes('divine') || 
             text.includes('wisdom') ||
             text.includes('spiritual')
    })
    
    // Navigate to main interface and test spiritual question
    cy.get('[data-testid="begin-journey-button"]').click()
    cy.askSpiritualQuestion('What is dharma?')
    
    // Verify response maintains Lord Krishna persona
    cy.get('[data-testid="response-text"]', { timeout: 15000 })
      .should('contain.text', 'dear')
      .and('satisfy', (el) => {
        const text = el.text().toLowerCase()
        return text.includes('arjuna') || text.includes('devotee') || text.includes('beloved')
      })
  })
})
