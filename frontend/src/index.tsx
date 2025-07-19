import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/spiritual-theme.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

// Remove React.StrictMode to prevent MSAL double-mounting issues
// StrictMode causes components to mount twice, corrupting MSAL cache
root.render(<App />);
