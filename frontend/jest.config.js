module.exports = {
  // Extend Create React App's Jest configuration
  ...require('react-scripts/scripts/utils/createJestConfig')(
    filePath => filePath.replace('<rootDir>', '.')
  ),
  
  // Gradual coverage improvement strategy
  coverageThreshold: {
    global: {
      branches: 30,    // Start at 30%, increase gradually
      functions: 30,   // Start at 30%, increase gradually  
      lines: 30,       // Start at 30%, increase gradually
      statements: 30   // Start at 30%, increase gradually
    },
    // Critical files should have higher coverage
    './src/components/SpiritualGuidanceInterface.tsx': {
      branches: 50,
      functions: 50,
      lines: 50,
      statements: 50
    },
    './src/services/adminService.ts': {
      branches: 60,
      functions: 60,
      lines: 60,
      statements: 60
    }
  },
  
  // Test environment setup
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  
  // Module name mapping for better imports
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  
  // Transform configuration
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { presets: ['react-app'] }]
  },
  
  // Test match patterns
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.(test|spec).{js,jsx,ts,tsx}'
  ],
  
  // Ignore patterns
  testPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/build/'
  ],
  
  // Coverage collection
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/reportWebVitals.ts',
    '!src/setupTests.ts'
  ]
};
