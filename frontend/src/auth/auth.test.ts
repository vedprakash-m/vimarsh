/**
 * Authentication Integration Tests
 * Tests the unified VedUser interface and service integration
 */

import { createAuthService, AuthUser } from './authService';
import { MSALAuthService } from './msalAuthService';

// Mock MSAL dependencies for testing
jest.mock('@azure/msal-browser');
jest.mock('./msalConfig', () => ({
  msalConfig: { auth: { clientId: 'test-client-id' } },
  getAuthConfigStatic: () => ({ usePlaceholder: true }), // Force placeholder mode for tests
  createLoginRequest: () => ({}),
  apiTokenRequest: {},
  silentRequest: {},
  createLogoutRequest: () => ({}),
  spiritualRoles: {
    SEEKER: 'seeker',
    DEVOTEE: 'devotee',
    SCHOLAR: 'scholar',
    EXPERT: 'expert',
    ADMIN: 'admin'
  },
  AUTH_ERROR_MESSAGES: {
    NO_ACCOUNT: 'No user account found. Please sign in.',
    TOKEN_EXPIRED: 'Your session has expired. Please sign in again.',
    NETWORK_ERROR: 'Network error during authentication. Please try again.',
    INVALID_TOKEN: 'Invalid authentication token. Please sign in again.',
    PERMISSION_DENIED: 'You do not have permission to access this resource.',
    GENERAL_ERROR: 'Authentication error occurred. Please try again.'
  }
}));

describe('Authentication System Integration', () => {
  // Set up environment for tests
  beforeAll(() => {
    process.env.NODE_ENV = 'test';
    process.env.REACT_APP_CLIENT_ID = 'test-client-id';
  });

  afterEach(() => {
    // Clear any stored authentication state
    localStorage.clear();
  });
  describe('VedUser Interface Compliance', () => {
    it('should have all required VedUser properties', () => {
      const mockUser: AuthUser = {
        // Core VedUser interface (required)
        id: 'test-user-123',
        email: 'test@vimarsh.dev',
        name: 'Test User',
        givenName: 'Test',
        familyName: 'User',
        permissions: ['user', 'seeker'],
        vedProfile: {
          profileId: 'test-user-123',
          subscriptionTier: 'free',
          appsEnrolled: ['vimarsh'],
          preferences: {
            language: 'English',
            spiritualInterests: ['Bhagavad Gita'],
            communicationStyle: 'reverent'
          }
        },
        
        // Vimarsh-specific fields (optional)
        preferredLanguage: 'English',
        spiritualInterests: ['Bhagavad Gita'],
        role: 'seeker',
        joinedDate: '2024-01-01',
        sessionCount: 1,
        lastActiveDate: '2024-01-01T00:00:00Z',
        profilePicture: '🙏'
      };

      // Verify core VedUser interface compliance
      expect(mockUser.id).toBeDefined();
      expect(mockUser.email).toBeDefined();
      expect(mockUser.name).toBeDefined();
      expect(mockUser.givenName).toBeDefined();
      expect(mockUser.familyName).toBeDefined();
      expect(Array.isArray(mockUser.permissions)).toBe(true);
      expect(mockUser.vedProfile).toBeDefined();
      expect(mockUser.vedProfile.profileId).toBeDefined();
      expect(mockUser.vedProfile.subscriptionTier).toBeDefined();
      expect(Array.isArray(mockUser.vedProfile.appsEnrolled)).toBe(true);
      expect(typeof mockUser.vedProfile.preferences).toBe('object');
    });

    it('should support subscription tiers', () => {
      const tiers: Array<'free' | 'premium' | 'enterprise'> = ['free', 'premium', 'enterprise'];
      
      tiers.forEach(tier => {
        const user: Partial<AuthUser> = {
          vedProfile: {
            profileId: 'test',
            subscriptionTier: tier,
            appsEnrolled: ['vimarsh'],
            preferences: {}
          }
        };
        
        expect(user.vedProfile?.subscriptionTier).toBe(tier);
      });
    });
  });

  describe('Authentication Service Factory', () => {
    it('should create placeholder service in development', () => {
      // The factory should now use placeholder due to our mock
      const authService = createAuthService();
      expect(authService).toBeDefined();
      expect(authService.login).toBeDefined();
      expect(authService.logout).toBeDefined();
      expect(authService.getUser).toBeDefined();
      expect(authService.getToken).toBeDefined();
      expect(authService.isAuthenticated).toBeDefined();
    });

    it('should have all required AuthService methods', () => {
      const authService = createAuthService();
      
      // Verify interface compliance
      expect(typeof authService.login).toBe('function');
      expect(typeof authService.logout).toBe('function');
      expect(typeof authService.getUser).toBe('function');
      expect(typeof authService.getToken).toBe('function');
      expect(typeof authService.refreshToken).toBe('function');
      expect(typeof authService.isAuthenticated).toBe('function');
    });
  });

  describe('Placeholder Authentication Service', () => {
    let authService: any;

    beforeEach(() => {
      // Ensure we get placeholder service
      process.env.NODE_ENV = 'development';
      authService = createAuthService();
    });

    it('should login with mock user data', async () => {
      const user = await authService.login();
      
      expect(user).toBeDefined();
      expect(user.id).toBeDefined();
      expect(user.email).toBeDefined();
      expect(user.vedProfile).toBeDefined();
      expect(user.vedProfile.profileId).toBeDefined();
      expect(user.vedProfile.subscriptionTier).toBeDefined();
    });

    it('should return user after login', async () => {
      await authService.login();
      const user = await authService.getUser();
      
      expect(user).toBeDefined();
      expect(user.email).toContain('@vimarsh.dev');
    });

    it('should return token for authenticated user', async () => {
      await authService.login();
      const token = await authService.getToken();
      
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token).toContain('mock-token-');
    });

    it('should handle logout properly', async () => {
      await authService.login();
      expect(authService.isAuthenticated()).toBe(true);
      
      await authService.logout();
      expect(authService.isAuthenticated()).toBe(false);
      
      const user = await authService.getUser();
      expect(user).toBeNull();
    });
  });

  describe('Error Handling', () => {
    it('should handle authentication errors gracefully', async () => {
      const authService = createAuthService();
      
      // Test token acquisition without login
      try {
        await authService.getToken();
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error).toBeDefined();
        expect(error.message).toContain('No authenticated user');
      }
    });
  });

  describe('Security Considerations', () => {
    it('should not expose sensitive data in user object', async () => {
      const authService = createAuthService();
      const user = await authService.login();
      
      // Verify no sensitive data is exposed
      expect(user).not.toHaveProperty('password');
      expect(user).not.toHaveProperty('secret');
      expect(user).not.toHaveProperty('key');
      expect(user).not.toHaveProperty('token');
    });

    it('should include security-focused permissions array', async () => {
      const authService = createAuthService();
      const user = await authService.login();
      
      expect(Array.isArray(user.permissions)).toBe(true);
      expect(user.permissions.length).toBeGreaterThan(0);
      expect(user.permissions).toContain('user');
    });
  });
});

// Integration test for MSAL service (when mocked)
describe('MSAL Service Structure', () => {
  it('should have MSALAuthService class available', () => {
    expect(MSALAuthService).toBeDefined();
    expect(typeof MSALAuthService).toBe('function'); // Constructor function
  });

  it('should implement all required methods', () => {
    // Test that the class has the right structure (without actually instantiating due to MSAL deps)
    const prototype = MSALAuthService.prototype;
    expect(prototype.login).toBeDefined();
    expect(prototype.logout).toBeDefined();
    expect(prototype.getUser).toBeDefined();
    expect(prototype.getToken).toBeDefined();
    expect(prototype.isAuthenticated).toBeDefined();
  });
});
