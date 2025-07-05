// Authentication Service - Abstraction layer for auth providers
// Switches between placeholder auth (development) and MSAL (production)

import { authConfig, spiritualRoles, type SpiritualRole } from './msalConfig';

// Unified VedUser interface from Apps_Auth_Requirement.md
export interface AuthUser {
  // Core VedUser interface (required)
  id: string;           // Entra ID subject claim (primary user identifier)
  email: string;        // User's email address
  name: string;         // Full display name
  givenName: string;    // First name
  familyName: string;   // Last name
  permissions: string[]; // App-specific permissions from JWT claims
  vedProfile: {
    profileId: string;                           // Vedprakash domain profile ID
    subscriptionTier: 'free' | 'premium' | 'enterprise';
    appsEnrolled: string[];                      // List of enrolled apps
    preferences: Record<string, any>;            // User preferences
  };
  
  // Vimarsh-specific fields (backward compatibility)
  preferredLanguage?: 'English' | 'Hindi';
  spiritualInterests?: string[];
  role?: SpiritualRole;
  joinedDate?: string;
  sessionCount?: number;
  lastActiveDate?: string;
  profilePicture?: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: AuthUser | null;
  isLoading: boolean;
  error: string | null;
}

export interface AuthService {
  login(options?: any): Promise<AuthUser>;
  logout(): Promise<void>;
  getUser(): Promise<AuthUser | null>;  // Changed from getCurrentUser to match MSALAuthService
  getToken(): Promise<string>;  // Changed from refreshToken and returns string not string | null
  refreshToken(): Promise<string>; // Added explicit refreshToken method
  isAuthenticated(): boolean;
}

// Placeholder Authentication Service (Development)
class PlaceholderAuthService implements AuthService {
  private currentUser: AuthUser | null = null;
  private mockUsers: AuthUser[] = [
    {
      id: 'dev-user-arjuna',
      name: 'Arjuna Dev',
      email: 'arjuna@vimarsh.dev',
      givenName: 'Arjuna',
      familyName: 'Dev',
      permissions: ['user', 'seeker'],
      vedProfile: {
        profileId: 'dev-user-arjuna',
        subscriptionTier: 'free',
        appsEnrolled: ['vimarsh'],
        preferences: {
          language: 'English',
          spiritualInterests: ['Bhagavad Gita', 'Dharma', 'Self-realization', 'Karma Yoga'],
          communicationStyle: 'contemplative'
        }
      },
      preferredLanguage: 'English',
      spiritualInterests: ['Bhagavad Gita', 'Dharma', 'Self-realization', 'Karma Yoga'],
      role: spiritualRoles.SEEKER,
      joinedDate: '2024-01-15',
      sessionCount: 42,
      lastActiveDate: new Date().toISOString(),
      profilePicture: '🏹'
    },
    {
      id: 'dev-user-meera',
      name: 'Meera भक्त',
      email: 'meera@vimarsh.dev',
      givenName: 'Meera',
      familyName: 'भक्त',
      permissions: ['user', 'devotee'],
      vedProfile: {
        profileId: 'dev-user-meera',
        subscriptionTier: 'premium',
        appsEnrolled: ['vimarsh', 'sutra'],
        preferences: {
          language: 'Hindi',
          spiritualInterests: ['Krishna Bhakti', 'Devotional Songs', 'Temple Worship', 'Raas Leela'],
          communicationStyle: 'devotional'
        }
      },
      preferredLanguage: 'Hindi',
      spiritualInterests: ['Krishna Bhakti', 'Devotional Songs', 'Temple Worship', 'Raas Leela'],
      role: spiritualRoles.DEVOTEE,
      joinedDate: '2024-02-01',
      sessionCount: 128,
      lastActiveDate: new Date().toISOString(),
      profilePicture: '🎶'
    },
    {
      id: 'dev-user-scholar',
      name: 'Pandit सत्यार्थी',
      email: 'scholar@vimarsh.dev',
      givenName: 'Pandit',
      familyName: 'सत्यार्थी',
      permissions: ['user', 'scholar', 'expert'],
      vedProfile: {
        profileId: 'dev-user-scholar',
        subscriptionTier: 'enterprise',
        appsEnrolled: ['vimarsh', 'sutra', 'pathfinder'],
        preferences: {
          language: 'English',
          spiritualInterests: ['Vedanta', 'Sanskrit Studies', 'Philosophical Inquiry', 'Upanishads'],
          communicationStyle: 'scholarly'
        }
      },
      preferredLanguage: 'English',
      spiritualInterests: ['Vedanta', 'Sanskrit Studies', 'Philosophical Inquiry', 'Upanishads'],
      role: spiritualRoles.SCHOLAR,
      joinedDate: '2024-03-10',
      sessionCount: 67,
      lastActiveDate: new Date().toISOString(),
      profilePicture: '📚'
    }
  ];

  async login(options?: { userType?: string }): Promise<AuthUser> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 800));

    let selectedUser: AuthUser;
    
    if (options?.userType) {
      const userIndex = this.mockUsers.findIndex(u => u.role === options.userType);
      selectedUser = userIndex >= 0 ? this.mockUsers[userIndex] : this.mockUsers[0];
    } else {
      selectedUser = this.mockUsers[Math.floor(Math.random() * this.mockUsers.length)];
    }

    // Update session info
    selectedUser = {
      ...selectedUser,
      sessionCount: (selectedUser.sessionCount || 0) + 1,
      lastActiveDate: new Date().toISOString()
    };

    this.currentUser = selectedUser;
    
    // Persist to localStorage for development
    localStorage.setItem('vimarsh_auth_user', JSON.stringify(selectedUser));
    localStorage.setItem('vimarsh_auth_timestamp', new Date().toISOString());

    console.log('🕉️ Placeholder auth: Spiritual seeker connected -', selectedUser.name);
    return selectedUser;
  }

  async logout(): Promise<void> {
    this.currentUser = null;
    localStorage.removeItem('vimarsh_auth_user');
    localStorage.removeItem('vimarsh_auth_timestamp');
    console.log('🙏 Placeholder auth: Spiritual seeker disconnected peacefully');
  }

  async getUser(): Promise<AuthUser | null> {
    if (this.currentUser) {
      return this.currentUser;
    }

    // Try to restore from localStorage
    try {
      const savedUser = localStorage.getItem('vimarsh_auth_user');
      const timestamp = localStorage.getItem('vimarsh_auth_timestamp');
      
      if (savedUser && timestamp) {
        const user = JSON.parse(savedUser) as AuthUser;
        const savedTime = new Date(timestamp).getTime();
        const now = new Date().getTime();
        
        // Session expires after 24 hours in development
        if (now - savedTime < 24 * 60 * 60 * 1000) {
          this.currentUser = user;
          return user;
        } else {
          await this.logout(); // Clean expired session
        }
      }
    } catch (error) {
      console.warn('Failed to restore auth session:', error);
      await this.logout();
    }

    return null;
  }

  async getToken(): Promise<string> {
    // In placeholder mode, return a mock token
    if (!this.currentUser) {
      throw new Error('No authenticated user');
    }
    return `mock-token-${Date.now()}`;
  }

  async refreshToken(): Promise<string> {
    // In placeholder mode, return a mock token
    if (!this.currentUser) {
      throw new Error('No authenticated user');
    }
    return `mock-refreshed-token-${Date.now()}`;
  }

  isAuthenticated(): boolean {
    return this.currentUser !== null;
  }
}

// Authentication Service Factory
export const createAuthService = (): AuthService => {
  // Check environment variables for auth configuration
  const enableAuth = process.env.REACT_APP_ENABLE_AUTH === 'true';
  const hasValidClientId = process.env.REACT_APP_CLIENT_ID && 
                           process.env.REACT_APP_CLIENT_ID !== 'placeholder-client-id' &&
                           process.env.REACT_APP_CLIENT_ID !== 'your-vimarsh-app-client-id';
  
  if (enableAuth && hasValidClientId && !authConfig.usePlaceholder) {
    console.log('🔐 Creating MSAL authentication service for production');
    // Import the actual MSALAuthService implementation
    try {
      const { MSALAuthService } = require('./msalAuthService');
      return new MSALAuthService();
    } catch (error) {
      console.warn('🔧 MSAL service not available, falling back to placeholder:', error);
      console.log('🔧 Creating placeholder authentication service for development');
      return new PlaceholderAuthService();
    }
  } else {
    console.log('🔧 Creating placeholder authentication service for development');
    return new PlaceholderAuthService();
  }
};

// Singleton auth service instance
export const authService = createAuthService();

// Auth utilities
export const getAuthHeaders = async (): Promise<Record<string, string>> => {
  const token = await authService.getToken().catch(() => null);
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const handleAuthError = (error: any): string => {
  if (error?.code === 'NETWORK_ERROR') {
    return 'Network connection issue. Please check your internet and try again.';
  }
  if (error?.code === 'UNAUTHORIZED') {
    return 'Authentication required. Please sign in to continue.';
  }
  if (error?.message) {
    return error.message;
  }
  return 'An unexpected authentication error occurred. Please try again.';
};

// Export auth service for easy import
export default authService;
