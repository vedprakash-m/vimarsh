// jest-dom adds custom jest matchers for asserting on DOM nodes.
import '@testing-library/jest-dom';

// Import test utilities
import { setupWebApiMocks } from './test-utils/webApiMocks';

// Mock axios globally to avoid ESM issues
jest.mock('axios', () => ({
  get: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  put: jest.fn(() => Promise.resolve({ data: {} })),
  delete: jest.fn(() => Promise.resolve({ data: {} })),
  create: jest.fn(() => ({
    get: jest.fn(() => Promise.resolve({ data: {} })),
    post: jest.fn(() => Promise.resolve({ data: {} })),
    put: jest.fn(() => Promise.resolve({ data: {} })),
    delete: jest.fn(() => Promise.resolve({ data: {} })),
    interceptors: {
      request: { use: jest.fn(), eject: jest.fn() },
      response: { use: jest.fn(), eject: jest.fn() }
    }
  })),
  interceptors: {
    request: { use: jest.fn(), eject: jest.fn() },
    response: { use: jest.fn(), eject: jest.fn() }
  },
  defaults: {
    headers: {
      common: {}
    }
  }
}));

// Suppress act() warnings and MSAL warnings for tests - React 18 compatibility
const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOMTestUtils.act is deprecated') ||
       args[0].includes('Warning: An update to') ||
       args[0].includes('was not wrapped in act'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
  
  console.warn = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Unknown domain detected')
    ) {
      return; // Suppress MSAL domain warnings in test environment
    }
    originalWarn.call(console, ...args);
  };
  
  // Setup comprehensive Web API mocks
  setupWebApiMocks();
});

afterAll(() => {
  console.error = originalError;
  console.warn = originalWarn;
});

// Mock IntersectionObserver
(global as any).IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
};

// Mock ResizeObserver
(global as any).ResizeObserver = class ResizeObserver {
  constructor() {}
  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
};

// Mock MSAL and crypto for testing environment
global.crypto = {
  getRandomValues: (arr: any) => {
    for (let i = 0; i < arr.length; i++) {
      arr[i] = Math.floor(Math.random() * 256);
    }
    return arr;
  },
  subtle: {
    digest: jest.fn(),
    importKey: jest.fn(),
    sign: jest.fn(),
    verify: jest.fn()
  } as any
} as any;

// Mock TextEncoder/TextDecoder for Node.js test environment
if (typeof TextEncoder === 'undefined') {
  global.TextEncoder = require('util').TextEncoder;
}
if (typeof TextDecoder === 'undefined') {
  global.TextDecoder = require('util').TextDecoder;
}

// Mock MSAL dependencies
jest.mock('@azure/msal-browser', () => ({
  PublicClientApplication: jest.fn().mockImplementation(() => ({
    initialize: jest.fn().mockResolvedValue(undefined),
    loginPopup: jest.fn().mockResolvedValue({ account: { username: 'test@test.com' } }),
    logout: jest.fn().mockResolvedValue(undefined),
    getAllAccounts: jest.fn().mockReturnValue([]),
    getAccountByUsername: jest.fn().mockReturnValue(null),
    acquireTokenSilent: jest.fn().mockResolvedValue({ accessToken: 'mock-token' }),
    addEventCallback: jest.fn(),
    removeEventCallback: jest.fn()
  })),
  LogLevel: {
    Error: 0,
    Warning: 1,
    Info: 2,
    Verbose: 3,
    Trace: 4
  },
  EventType: {
    LOGIN_SUCCESS: 'msal:loginSuccess',
    LOGIN_FAILURE: 'msal:loginFailure',
    LOGOUT_SUCCESS: 'msal:logoutSuccess'
  },
  InteractionType: {
    POPUP: 'popup',
    REDIRECT: 'redirect'
  }
}));

// Mock MSAL React context
jest.mock('@azure/msal-react', () => ({
  useMsal: jest.fn(() => ({
    instance: {
      initialize: jest.fn().mockResolvedValue(undefined),
      loginPopup: jest.fn().mockResolvedValue({ account: { username: 'test@test.com' } }),
      logout: jest.fn().mockResolvedValue(undefined),
      getAllAccounts: jest.fn().mockReturnValue([]),
      getAccountByUsername: jest.fn().mockReturnValue(null),
      acquireTokenSilent: jest.fn().mockResolvedValue({ accessToken: 'mock-token' }),
      addEventCallback: jest.fn(),
      removeEventCallback: jest.fn()
    },
    accounts: [],
    inProgress: 'None'
  })),
  useAccount: jest.fn(() => null),
  useIsAuthenticated: jest.fn(() => false),
  MsalProvider: ({ children }: { children: React.ReactNode }) => children,
  AuthenticatedTemplate: ({ children }: { children: React.ReactNode }) => null,
  UnauthenticatedTemplate: ({ children }: { children: React.ReactNode }) => children
}));

// Mock AuthContext globally for all tests
const mockAuthValue = {
  isAuthenticated: true,
  user: {
    id: 'test-user-123',
    email: 'test@vimarsh.app',
    name: 'Test User'
  },
  login: jest.fn(),
  logout: jest.fn(),
  loading: false
};

// Mock the auth provider for components that import from auth/AuthProvider
jest.mock('./auth/AuthProvider', () => ({
  useAuth: () => mockAuthValue,
  AuthProvider: ({ children }: { children: React.ReactNode }) => children
}));

// Mock SettingsContext globally for all tests
const mockSettings = {
  user_id: 'test-user-123',
  experience_preferences: {
    conversation_style: 'balanced',
    language: 'en',
    formality: 'respectful',
    favorite_personalities: ['krishna', 'buddha'],
    theme: 'auto',
    text_size: 'medium',
    reduce_animations: false
  },
  notification_preferences: {
    daily_wisdom_enabled: true,
    preferred_time: '09:00',
    timezone: 'UTC',
    quiet_hours_enabled: false,
    quiet_start: '22:00',
    quiet_end: '07:00',
    types: {
      daily_wisdom: true,
      streak_reminders: true,
      achievements: true,
      weekly_summary: false
    }
  },
  memory_preferences: {
    remember_conversations: true,
    connect_insights: true,
    track_emotions: false,
    suggest_topics: true,
    privacy_mode: 'standard',
    data_retention_days: 90,
    analytics_consent: true,
    research_consent: false
  },
  updated_at: '2024-01-01T00:00:00Z'
};

const mockProfile = {
  user: {
    user_id: 'test-user-123',
    email: 'test@vimarsh.app',
    name: 'Test User',
    member_since: '2024-01-01T00:00:00Z'
  },
  journey_stats: {
    current_streak: 14,
    total_conversations: 87,
    achievements_unlocked: 5,
    wisdom_level: 'Seeker',
    domain_exploration: {
      spiritual: 45,
      scientific: 12,
      philosophical: 20,
      leadership: 8,
      literary: 2,
      psychology: 0
    }
  },
  preferences: mockSettings,
  ai_usage: {
    monthly_cost: 2.34,
    monthly_limit: 10.00,
    status: 'well_within_limits',
    trend: 'similar_to_last_month'
  }
};

jest.mock('./contexts/SettingsContext', () => ({
  useSettings: () => ({
    settings: mockSettings,
    profile: mockProfile,
    loading: false,
    error: null,
    updateSettings: jest.fn().mockResolvedValue(undefined),
    refreshProfile: jest.fn().mockResolvedValue(undefined)
  }),
  SettingsProvider: ({ children }: { children: React.ReactNode }) => children
}));

// Mock PersonalityContext globally for all tests
const mockPersonalities = [
  { id: 'krishna', name: 'Krishna', domain: 'spiritual', era: 'Ancient', shortBio: 'Divine teacher' },
  { id: 'buddha', name: 'Buddha', domain: 'spiritual', era: 'Ancient', shortBio: 'Enlightened one' },
  { id: 'socrates', name: 'Socrates', domain: 'philosophical', era: 'Ancient', shortBio: 'Greek philosopher' },
  { id: 'einstein', name: 'Albert Einstein', domain: 'scientific', era: 'Modern', shortBio: 'Physicist' },
  { id: 'lincoln', name: 'Abraham Lincoln', domain: 'leadership', era: 'Modern', shortBio: 'US President' },
  { id: 'shakespeare', name: 'William Shakespeare', domain: 'literary', era: 'Renaissance', shortBio: 'Playwright' },
  { id: 'freud', name: 'Sigmund Freud', domain: 'psychology', era: 'Modern', shortBio: 'Psychoanalyst' }
];

jest.mock('./contexts/PersonalityContext', () => ({
  usePersonality: () => ({
    currentPersonality: mockPersonalities[0],
    availablePersonalities: mockPersonalities,
    setCurrentPersonality: jest.fn(),
    loading: false,
    error: null
  }),
  PersonalityProvider: ({ children }: { children: React.ReactNode }) => children
}));
