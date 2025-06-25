// Authentication Service - Abstraction layer for auth providers
// Switches between placeholder auth (development) and MSAL (production)

import { authConfig, spiritualRoles, type SpiritualRole } from './msalConfig';

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  preferredLanguage: 'English' | 'Hindi';
  spiritualInterests: string[];
  role: SpiritualRole;
  joinedDate: string;
  sessionCount: number;
  lastActiveDate: string;
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
  getCurrentUser(): Promise<AuthUser | null>;
  refreshToken(): Promise<string | null>;
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
      sessionCount: selectedUser.sessionCount + 1,
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

  async getCurrentUser(): Promise<AuthUser | null> {
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

  async refreshToken(): Promise<string | null> {
    // In placeholder mode, return a mock token
    return this.currentUser ? `mock-token-${Date.now()}` : null;
  }

  isAuthenticated(): boolean {
    return this.currentUser !== null;
  }
}

// MSAL Authentication Service (Production)
class MSALAuthService implements AuthService {
  async login(): Promise<AuthUser> {
    // TODO: Implement actual MSAL login
    throw new Error('MSAL authentication not yet implemented');
  }

  async logout(): Promise<void> {
    // TODO: Implement actual MSAL logout
    throw new Error('MSAL authentication not yet implemented');
  }

  async getCurrentUser(): Promise<AuthUser | null> {
    // TODO: Implement actual MSAL user retrieval
    return null;
  }

  async refreshToken(): Promise<string | null> {
    // TODO: Implement actual MSAL token refresh
    return null;
  }

  isAuthenticated(): boolean {
    // TODO: Implement actual MSAL auth check
    return false;
  }
}

// Authentication Service Factory
export const createAuthService = (): AuthService => {
  if (authConfig.usePlaceholder) {
    console.log('🔧 Creating placeholder authentication service for development');
    return new PlaceholderAuthService();
  } else {
    console.log('🔐 Creating MSAL authentication service for production');
    return new MSALAuthService();
  }
};

// Singleton auth service instance
export const authService = createAuthService();

// Auth utilities
export const getAuthHeaders = async (): Promise<Record<string, string>> => {
  const token = await authService.refreshToken();
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
