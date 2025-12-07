/**
 * End-to-End Tests for User Settings Feature
 * Tests complete settings configuration flows across all tabs
 */

describe('User Settings - E2E', () => {
  beforeEach(() => {
    // Mock authentication
    cy.intercept('GET', '**/api/auth/profile', {
      statusCode: 200,
      body: {
        user_id: 'test-user-e2e',
        email: 'seeker@vimarsh.app',
        name: 'E2E Test Seeker',
        created_at: '2024-01-01T00:00:00Z',
        subscription_tier: 'free',
        subscription_status: 'active',
      },
    }).as('getProfile');

    // Mock preferences
    cy.intercept('GET', '**/api/user/preferences', {
      statusCode: 200,
      body: {
        notification_preferences: {
          enabled: true,
          daily_wisdom_enabled: true,
          preferred_time: '09:00',
          timezone: 'UTC',
          quiet_hours_enabled: false,
          notification_types: {
            daily_wisdom: true,
            streak_reminders: true,
            achievements: true,
            weekly_summary: false,
          },
        },
        memory_preferences: {
          remember_conversations: true,
          connect_insights: true,
          track_emotions: false,
          suggest_topics: true,
          privacy_mode: 'standard',
          allow_analytics: true,
          allow_research: false,
          data_retention_days: 90,
        },
        ui_preferences: {
          conversation_style: 'balanced',
          language: 'english',
          formality: 'respectful',
          favorite_personalities: ['krishna', 'marcus-aurelius'],
          theme: 'light',
          show_citations: true,
        },
      },
    }).as('getPreferences');

    // Mock usage summary
    cy.intercept('GET', '**/api/user/usage-summary', {
      statusCode: 200,
      body: {
        total_conversations: 87,
        total_messages: 456,
        guidance_received: 125,
        streak_days: 14,
        monthly_conversations: 28,
        monthly_limit: 50,
        daily_messages: 12,
        daily_limit: 20,
      },
    }).as('getUsageSummary');

    // Mock preferences update
    cy.intercept('PATCH', '**/api/user/preferences', {
      statusCode: 200,
      body: { success: true },
    }).as('updatePreferences');

    // Visit settings page
    cy.visit('/settings');
    cy.wait(['@getProfile', '@getPreferences', '@getUsageSummary']);
  });

  describe('Page Load and Navigation', () => {
    it('loads settings page successfully', () => {
      cy.get('h1').should('contain', 'Settings');
    });

    it('displays all navigation tabs', () => {
      cy.get('[role="tab"]').should('have.length', 5);
      cy.contains('[role="tab"]', 'My Profile').should('be.visible');
      cy.contains('[role="tab"]', 'Experience').should('be.visible');
      cy.contains('[role="tab"]', 'Notifications').should('be.visible');
      cy.contains('[role="tab"]', 'Memory & Privacy').should('be.visible');
      cy.contains('[role="tab"]', 'Account').should('be.visible');
    });

    it('shows My Profile tab by default', () => {
      cy.get('[data-testid="my-profile-tab"]').should('be.visible');
    });

    it('navigates between tabs correctly', () => {
      // Navigate to Experience
      cy.contains('[role="tab"]', 'Experience').click();
      cy.get('[data-testid="experience-tab"]').should('be.visible');

      // Navigate to Notifications
      cy.contains('[role="tab"]', 'Notifications').click();
      cy.get('[data-testid="notifications-tab"]').should('be.visible');

      // Navigate to Memory & Privacy
      cy.contains('[role="tab"]', 'Memory & Privacy').click();
      cy.get('[data-testid="memory-privacy-tab"]').should('be.visible');

      // Navigate to Account
      cy.contains('[role="tab"]', 'Account').click();
      cy.get('[data-testid="account-tab"]').should('be.visible');
    });

    it('updates URL hash when switching tabs', () => {
      cy.contains('[role="tab"]', 'Experience').click();
      cy.location('hash').should('eq', '#experience');

      cy.contains('[role="tab"]', 'Notifications').click();
      cy.location('hash').should('eq', '#notifications');
    });

    it('loads correct tab from URL hash', () => {
      cy.visit('/settings#notifications');
      cy.wait('@getPreferences');
      cy.get('[data-testid="notifications-tab"]').should('be.visible');
      cy.contains('[role="tab"]', 'Notifications').should('have.attr', 'aria-selected', 'true');
    });
  });

  describe('My Profile Tab', () => {
    it('displays user profile information', () => {
      cy.contains('E2E Test Seeker').should('be.visible');
      cy.contains('seeker@vimarsh.app').should('be.visible');
    });

    it('shows journey statistics', () => {
      cy.contains('87').should('be.visible'); // Total conversations
      cy.contains('456').should('be.visible'); // Total messages
      cy.contains('14').should('be.visible'); // Streak days
    });

    it('displays favorite personalities', () => {
      cy.contains('krishna').should('be.visible');
      cy.contains('marcus-aurelius').should('be.visible');
    });

    it('shows member since date', () => {
      cy.contains('Member since').should('be.visible');
      cy.contains('January 2024').should('be.visible');
    });
  });

  describe('Experience Tab', () => {
    beforeEach(() => {
      cy.contains('[role="tab"]', 'Experience').click();
    });

    it('displays conversation style selector', () => {
      cy.contains('Conversation Style').should('be.visible');
      cy.contains('button', 'Balanced').should('be.visible');
    });

    it('changes conversation style', () => {
      cy.contains('button', 'Contemplative').click();
      cy.wait('@updatePreferences').its('request.body').should('deep.include', {
        ui_preferences: {
          conversation_style: 'contemplative',
        },
      });
      cy.contains('Saved').should('be.visible');
    });

    it('adjusts formality level', () => {
      cy.contains('Formality').parent().find('select').select('casual');
      cy.wait('@updatePreferences');
      cy.contains('Saved').should('be.visible');
    });

    it('manages favorite personalities', () => {
      cy.contains('Favorite Personalities').should('be.visible');
      cy.contains('2 of 5 selected').should('be.visible');

      // Add a new favorite
      cy.contains('button', 'Buddha').click();
      cy.wait('@updatePreferences');

      // Should show updated count
      cy.contains('3 of 5 selected').should('be.visible');
    });

    it('prevents adding more than 5 favorites', () => {
      // Add favorites until limit
      cy.contains('button', 'Buddha').click();
      cy.wait('@updatePreferences');
      cy.contains('button', 'Jesus Christ').click();
      cy.wait('@updatePreferences');
      cy.contains('button', 'Lao Tzu').click();
      cy.wait('@updatePreferences');

      // Try to add 6th favorite
      cy.contains('button', 'Confucius').click();
      cy.contains('Maximum 5 personalities').should('be.visible');
    });

    it('toggles citation display', () => {
      cy.contains('Show Citations').parent().find('input[type="checkbox"]').click();
      cy.wait('@updatePreferences').its('request.body').should('deep.include', {
        ui_preferences: {
          show_citations: false,
        },
      });
    });

    it('changes theme', () => {
      cy.contains('Theme').parent().find('select').select('dark');
      cy.wait('@updatePreferences');
      cy.contains('Saved').should('be.visible');
    });
  });

  describe('Notifications Tab', () => {
    beforeEach(() => {
      cy.contains('[role="tab"]', 'Notifications').click();
    });

    it('displays notification settings', () => {
      cy.contains('Daily Wisdom').should('be.visible');
      cy.contains('Notification Types').should('be.visible');
    });

    it('toggles daily wisdom', () => {
      cy.contains('Daily Wisdom').parent().find('input[type="checkbox"]').first().click();
      cy.wait('@updatePreferences').its('request.body').should('deep.include', {
        notification_preferences: {
          daily_wisdom_enabled: false,
        },
      });
    });

    it('changes preferred notification time', () => {
      cy.contains('Preferred Time').parent().find('select').select('18:00');
      cy.wait('@updatePreferences');
      cy.contains('Saved').should('be.visible');
    });

    it('selects timezone', () => {
      cy.contains('Timezone').parent().find('select').select('America/New_York');
      cy.wait('@updatePreferences').its('request.body').should('deep.include', {
        notification_preferences: {
          timezone: 'America/New_York',
        },
      });
    });

    it('configures quiet hours', () => {
      // Enable quiet hours
      cy.contains('Quiet Hours').parent().find('input[type="checkbox"]').click();
      cy.wait('@updatePreferences');

      // Set start time
      cy.contains('Start Time').parent().find('select').select('22:00');
      cy.wait('@updatePreferences');

      // Set end time
      cy.contains('End Time').parent().find('select').select('07:00');
      cy.wait('@updatePreferences');
    });

    it('manages notification types', () => {
      // Toggle individual notification types
      cy.contains('Streak Reminders').parent().find('input[type="checkbox"]').click();
      cy.wait('@updatePreferences');

      cy.contains('Weekly Summary').parent().find('input[type="checkbox"]').click();
      cy.wait('@updatePreferences');
    });

    it('sends test notification', () => {
      cy.stub(Notification, 'requestPermission').resolves('granted');
      cy.stub(Notification.prototype, 'Notification');

      cy.contains('button', 'Send Test').click();
      cy.contains('Test notification sent').should('be.visible');
    });
  });

  describe('Memory & Privacy Tab', () => {
    beforeEach(() => {
      cy.contains('[role="tab"]', 'Memory & Privacy').click();
    });

    it('displays memory features', () => {
      cy.contains('Remember Conversations').should('be.visible');
      cy.contains('Connect Insights').should('be.visible');
      cy.contains('Track Emotions').should('be.visible');
    });

    it('toggles memory features', () => {
      cy.contains('Track Emotions').parent().find('input[type="checkbox"]').click();
      cy.wait('@updatePreferences').its('request.body').should('deep.include', {
        memory_preferences: {
          track_emotions: true,
        },
      });
    });

    it('changes privacy mode', () => {
      cy.contains('button', 'Private').click();
      cy.wait('@updatePreferences').its('request.body').should('deep.include', {
        memory_preferences: {
          privacy_mode: 'private',
        },
      });

      // Verify warning for minimal mode
      cy.contains('button', 'Minimal').click();
      cy.contains('disable').should('be.visible');
    });

    it('adjusts data retention period', () => {
      cy.contains('Data Retention').parent().find('select').select('30');
      cy.wait('@updatePreferences').its('request.body').should('deep.include', {
        memory_preferences: {
          data_retention_days: 30,
        },
      });
    });

    it('toggles data transparency options', () => {
      cy.contains('Analytics').parent().find('input[type="checkbox"]').click();
      cy.wait('@updatePreferences');

      cy.contains('Research').parent().find('input[type="checkbox"]').click();
      cy.wait('@updatePreferences');
    });

    it('exports user data', () => {
      cy.intercept('POST', '**/api/user/export', {
        statusCode: 200,
        body: { success: true, file: 'export.json' },
      }).as('exportData');

      cy.contains('button', 'Export Data').click();
      cy.wait('@exportData');
      cy.contains('Export successful').should('be.visible');
    });

    it('clears conversation history with confirmation', () => {
      cy.intercept('DELETE', '**/api/user/history', {
        statusCode: 200,
        body: { success: true },
      }).as('clearHistory');

      cy.contains('button', 'Clear History').click();

      // Verify confirmation modal
      cy.contains('Confirm').should('be.visible');
      cy.contains('cannot be undone').should('be.visible');

      // Confirm deletion
      cy.contains('button', 'Confirm').click();
      cy.wait('@clearHistory');
      cy.contains('History cleared').should('be.visible');
    });
  });

  describe('Account Tab', () => {
    beforeEach(() => {
      cy.contains('[role="tab"]', 'Account').click();
    });

    it('displays subscription information', () => {
      cy.contains('Free Tier').should('be.visible');
      cy.contains('Active').should('be.visible');
    });

    it('shows usage progress', () => {
      cy.contains('28 / 50').should('be.visible'); // Monthly conversations
      cy.contains('12 / 20').should('be.visible'); // Daily messages
      cy.get('[role="progressbar"]').should('have.length', 2);
    });

    it('displays account security section', () => {
      cy.contains('Account Security').should('be.visible');
      cy.contains('seeker@vimarsh.app').should('be.visible');
      cy.contains('button', 'Change Email').should('be.visible');
      cy.contains('button', 'Change Password').should('be.visible');
    });

    it('navigates to upgrade from free tier', () => {
      cy.contains('button', 'Upgrade').click();
      cy.location('pathname').should('eq', '/pricing');
    });
  });

  describe('Auto-Save Functionality', () => {
    it('shows saving indicator during preference update', () => {
      cy.intercept('PATCH', '**/api/user/preferences', (req) => {
        req.reply((res) => {
          res.delay = 1000; // Simulate slow network
          res.send({ statusCode: 200, body: { success: true } });
        });
      }).as('slowUpdate');

      cy.contains('[role="tab"]', 'Experience').click();
      cy.contains('button', 'Contemplative').click();

      cy.contains('Saving...').should('be.visible');
      cy.wait('@slowUpdate');
      cy.contains('Saved').should('be.visible');
    });

    it('shows error on failed save', () => {
      cy.intercept('PATCH', '**/api/user/preferences', {
        statusCode: 500,
        body: { error: 'Server error' },
      }).as('failedUpdate');

      cy.contains('[role="tab"]', 'Experience').click();
      cy.contains('button', 'Contemplative').click();

      cy.wait('@failedUpdate');
      cy.contains('Failed to save').should('be.visible');
    });

    it('debounces rapid preference changes', () => {
      let updateCount = 0;
      cy.intercept('PATCH', '**/api/user/preferences', (req) => {
        updateCount++;
        req.reply({ statusCode: 200, body: { success: true } });
      }).as('debouncedUpdate');

      cy.contains('[role="tab"]', 'Notifications').click();

      // Make rapid changes
      cy.contains('Daily Wisdom').parent().find('input[type="checkbox"]').click();
      cy.contains('Streak Reminders').parent().find('input[type="checkbox"]').click();
      cy.contains('Achievements').parent().find('input[type="checkbox"]').click();

      // Should batch or debounce requests
      cy.wait(1000).then(() => {
        expect(updateCount).to.be.lessThan(3); // Should be batched
      });
    });
  });

  describe('Complete Settings Configuration Flow', () => {
    it('completes full settings configuration journey', () => {
      // Step 1: Update Experience preferences
      cy.contains('[role="tab"]', 'Experience').click();
      cy.contains('button', 'Contemplative').click();
      cy.wait('@updatePreferences');
      cy.contains('Saved').should('be.visible');

      cy.contains('button', 'Buddha').click();
      cy.wait('@updatePreferences');

      // Step 2: Configure Notifications
      cy.contains('[role="tab"]', 'Notifications').click();
      cy.contains('Preferred Time').parent().find('select').select('18:00');
      cy.wait('@updatePreferences');

      cy.contains('Timezone').parent().find('select').select('America/Los_Angeles');
      cy.wait('@updatePreferences');

      // Step 3: Adjust Memory & Privacy
      cy.contains('[role="tab"]', 'Memory & Privacy').click();
      cy.contains('Track Emotions').parent().find('input[type="checkbox"]').click();
      cy.wait('@updatePreferences');

      cy.contains('Data Retention').parent().find('select').select('180');
      cy.wait('@updatePreferences');

      // Step 4: Verify changes persist
      cy.reload();
      cy.wait(['@getProfile', '@getPreferences', '@getUsageSummary']);

      // Verify Experience changes
      cy.contains('[role="tab"]', 'Experience').click();
      cy.contains('button', 'Contemplative').should('have.class', 'selected');

      // Verify Notifications changes
      cy.contains('[role="tab"]', 'Notifications').click();
      cy.contains('Preferred Time').parent().find('select').should('have.value', '18:00');

      // Verify Memory changes
      cy.contains('[role="tab"]', 'Memory & Privacy').click();
      cy.contains('Track Emotions').parent().find('input[type="checkbox"]').should('be.checked');
    });
  });

  describe('Keyboard Navigation', () => {
    it('navigates tabs with arrow keys', () => {
      cy.contains('[role="tab"]', 'My Profile').focus();
      cy.focused().type('{rightarrow}');
      cy.contains('[role="tab"]', 'Experience').should('have.focus');

      cy.focused().type('{rightarrow}');
      cy.contains('[role="tab"]', 'Notifications').should('have.focus');

      cy.focused().type('{leftarrow}');
      cy.contains('[role="tab"]', 'Experience').should('have.focus');
    });

    it('uses Home/End keys for first/last tab', () => {
      cy.contains('[role="tab"]', 'My Profile').focus();
      cy.focused().type('{end}');
      cy.contains('[role="tab"]', 'Account').should('have.focus');

      cy.focused().type('{home}');
      cy.contains('[role="tab"]', 'My Profile').should('have.focus');
    });
  });

  describe('Responsive Design', () => {
    it('works on mobile viewport', () => {
      cy.viewport('iphone-x');
      cy.visit('/settings');
      cy.wait('@getPreferences');

      // Should show mobile-optimized layout
      cy.get('[role="tablist"]').should('have.class', 'flex-col');

      // Navigation should still work
      cy.contains('[role="tab"]', 'Experience').click();
      cy.get('[data-testid="experience-tab"]').should('be.visible');
    });

    it('works on tablet viewport', () => {
      cy.viewport('ipad-2');
      cy.visit('/settings');
      cy.wait('@getPreferences');

      // Should adapt to tablet layout
      cy.contains('[role="tab"]', 'Notifications').click();
      cy.get('[data-testid="notifications-tab"]').should('be.visible');
    });
  });

  describe('Error Handling', () => {
    it('handles failed preference load', () => {
      cy.intercept('GET', '**/api/user/preferences', {
        statusCode: 500,
        body: { error: 'Server error' },
      }).as('failedLoad');

      cy.visit('/settings');
      cy.wait('@failedLoad');

      cy.contains('Failed to load').should('be.visible');
      cy.contains('button', 'Retry').should('be.visible');
    });

    it('retries failed requests', () => {
      let attemptCount = 0;
      cy.intercept('GET', '**/api/user/preferences', (req) => {
        attemptCount++;
        if (attemptCount === 1) {
          req.reply({ statusCode: 500, body: { error: 'Server error' } });
        } else {
          req.reply({ statusCode: 200, body: { /* valid preferences */ } });
        }
      }).as('retryLoad');

      cy.visit('/settings');
      cy.wait('@retryLoad');
      cy.contains('button', 'Retry').click();
      cy.wait('@retryLoad');

      cy.get('[data-testid="my-profile-tab"]').should('be.visible');
    });
  });

  describe('Accessibility', () => {
    it('has no accessibility violations', () => {
      cy.injectAxe();
      cy.checkA11y();
    });

    it('announces tab changes to screen readers', () => {
      cy.contains('[role="tab"]', 'Experience').click();
      cy.get('[role="status"]').should('contain', 'Experience');
    });

    it('has proper ARIA attributes', () => {
      cy.get('[role="tablist"]').should('exist');
      cy.get('[role="tab"]').should('have.length', 5);
      cy.get('[role="tabpanel"]').should('exist');

      cy.get('[role="tab"]').first().should('have.attr', 'aria-selected');
      cy.get('[role="tabpanel"]').should('have.attr', 'aria-labelledby');
    });
  });
});
