// Debug Authentication Configuration
// Open http://localhost:3000 and paste this in browser console

console.log('🔍 Current Authentication Configuration Debug:');
console.log('Current URL:', window.location.href);
console.log('Environment variables available to React app:');

// Check all React environment variables
Object.keys(window).forEach(key => {
  if (key.startsWith('REACT_APP_')) {
    console.log(`${key}:`, window[key]);
  }
});

// Try to access internal React env (if exposed)
if (typeof process !== 'undefined' && process.env) {
  console.log('NODE_ENV:', process.env.NODE_ENV);
  console.log('REACT_APP_CLIENT_ID:', process.env.REACT_APP_CLIENT_ID);
  console.log('REACT_APP_AUTHORITY:', process.env.REACT_APP_AUTHORITY);
  console.log('REACT_APP_TENANT_ID:', process.env.REACT_APP_TENANT_ID);
}

// Check for exposed configuration objects
if (window.AUTH_IDS) {
  console.log('AUTH_IDS Config:', window.AUTH_IDS.getConfigSummary());
}

if (window.msalInstance) {
  const config = window.msalInstance.getConfiguration();
  console.log('🔐 MSAL Configuration:');
  console.log('Authority:', config.auth.authority);
  console.log('Client ID:', config.auth.clientId);
  console.log('Redirect URI:', config.auth.redirectUri);
}

// Check localStorage for any cached auth data
console.log('🗄️ Local Storage Keys:');
Object.keys(localStorage).forEach(key => {
  if (key.includes('msal') || key.includes('auth')) {
    console.log(`${key}:`, localStorage.getItem(key));
  }
});
