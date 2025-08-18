import React, { useState, useEffect } from 'react';
import { Download, Wifi, WifiOff, RefreshCw, X } from 'lucide-react';
import { usePWA } from '../utils/pwa';

interface PWABannerProps {
  className?: string;
}

export const PWABanner: React.FC<PWABannerProps> = ({ className = '' }) => {
  const { canInstall, showInstallPrompt, updateAvailable, updateApp } = usePWA();
  const [showInstallBanner, setShowInstallBanner] = useState(false);
  const [showUpdateBanner, setShowUpdateBanner] = useState(false);
  const [installing, setInstalling] = useState(false);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    setShowInstallBanner(canInstall);
  }, [canInstall]);

  useEffect(() => {
    setShowUpdateBanner(updateAvailable);
  }, [updateAvailable]);

  const handleInstall = async () => {
    setInstalling(true);
    try {
      await showInstallPrompt();
      setShowInstallBanner(false);
    } catch (error) {
      console.error('Install failed:', error);
    } finally {
      setInstalling(false);
    }
  };

  const handleUpdate = async () => {
    setUpdating(true);
    try {
      await updateApp();
    } catch (error) {
      console.error('Update failed:', error);
    } finally {
      setUpdating(false);
    }
  };

  const dismissInstallBanner = () => {
    setShowInstallBanner(false);
    localStorage.setItem('pwa-install-dismissed', 'true');
  };

  // Don't show if user has dismissed install prompt before
  const installDismissed = localStorage.getItem('pwa-install-dismissed') === 'true';

  if (showUpdateBanner) {
    return (
      <div style={{
        position: 'fixed',
        top: '1rem',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 1000,
        background: 'linear-gradient(135deg, #FF6B35, #F7931E)',
        borderRadius: '1rem',
        padding: '1rem 1.5rem',
        boxShadow: '0 10px 30px rgba(255, 107, 53, 0.3)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        backdropFilter: 'blur(8px)',
        color: '#ffffff',
        minWidth: '320px',
        maxWidth: '480px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}>
          <RefreshCw 
            size={20} 
            style={{
              color: '#ffffff',
              flexShrink: 0
            }}
          />
          <div style={{ flex: 1 }}>
            <span style={{
              display: 'block',
              fontWeight: '600',
              fontSize: '0.875rem',
              marginBottom: '0.25rem'
            }}>Update Available</span>
            <span style={{
              display: 'block',
              fontSize: '0.75rem',
              opacity: 0.9,
              lineHeight: '1.4'
            }}>
              A new version of Vimarsh is ready to install
            </span>
          </div>
          <button
            onClick={handleUpdate}
            disabled={updating}
            style={{
              background: 'rgba(255, 255, 255, 0.2)',
              color: '#ffffff',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '0.5rem',
              padding: '0.5rem 1rem',
              fontSize: '0.75rem',
              fontWeight: '600',
              cursor: updating ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              opacity: updating ? 0.7 : 1
            }}
            onMouseEnter={(e) => {
              if (!updating) {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
                e.currentTarget.style.transform = 'translateY(-1px)';
              }
            }}
            onMouseLeave={(e) => {
              if (!updating) {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                e.currentTarget.style.transform = 'translateY(0)';
              }
            }}
            aria-label="Update Vimarsh to latest version"
          >
            {updating ? 'Updating...' : 'Update'}
          </button>
          <button
            onClick={() => setShowUpdateBanner(false)}
            style={{
              background: 'none',
              border: 'none',
              color: '#ffffff',
              cursor: 'pointer',
              padding: '0.25rem',
              borderRadius: '0.25rem',
              opacity: 0.7,
              transition: 'opacity 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = '1';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = '0.7';
            }}
            aria-label="Dismiss update notification"
          >
            <X size={16} />
          </button>
        </div>
      </div>
    );
  }

  if (showInstallBanner && !installDismissed) {
    return (
      <div style={{
        position: 'fixed',
        bottom: '1rem',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 1000,
        background: '#ffffff',
        borderRadius: '1rem',
        padding: '1rem 1.5rem',
        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.15)',
        border: '2px solid #FF6B35',
        color: '#1e293b',
        minWidth: '320px',
        maxWidth: '480px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}>
          <Download 
            size={20} 
            style={{
              color: '#FF6B35',
              flexShrink: 0
            }}
          />
          <div style={{ flex: 1 }}>
            <span style={{
              display: 'block',
              fontWeight: '600',
              fontSize: '0.875rem',
              marginBottom: '0.25rem',
              color: '#1e293b'
            }}>Install Vimarsh</span>
            <span style={{
              display: 'block',
              fontSize: '0.75rem',
              color: '#64748b',
              lineHeight: '1.4'
            }}>
              Get the full app experience with offline access
            </span>
          </div>
          <button
            onClick={handleInstall}
            disabled={installing}
            style={{
              background: 'linear-gradient(135deg, #FF6B35, #F7931E)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '0.5rem',
              padding: '0.5rem 1rem',
              fontSize: '0.75rem',
              fontWeight: '600',
              cursor: installing ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              opacity: installing ? 0.7 : 1,
              boxShadow: '0 2px 8px rgba(255, 107, 53, 0.3)'
            }}
            onMouseEnter={(e) => {
              if (!installing) {
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(255, 107, 53, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (!installing) {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 2px 8px rgba(255, 107, 53, 0.3)';
              }
            }}
            aria-label="Install Vimarsh as an app"
          >
            {installing ? 'Installing...' : 'Install'}
          </button>
          <button
            onClick={dismissInstallBanner}
            style={{
              background: 'none',
              border: 'none',
              color: '#64748b',
              cursor: 'pointer',
              padding: '0.25rem',
              borderRadius: '0.25rem',
              opacity: 0.7,
              transition: 'opacity 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = '1';
              e.currentTarget.style.color = '#1e293b';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = '0.7';
              e.currentTarget.style.color = '#64748b';
            }}
            aria-label="Dismiss install prompt"
          >
            <X size={16} />
          </button>
        </div>
      </div>
    );
  }

  return null;
};

interface OfflineIndicatorProps {
  className?: string;
}

export const OfflineIndicator: React.FC<OfflineIndicatorProps> = ({ className = '' }) => {
  const { isOnline } = usePWA();
  const [showOfflineMessage, setShowOfflineMessage] = useState(false);

  useEffect(() => {
    if (!isOnline) {
      setShowOfflineMessage(true);
    } else {
      // Hide offline message after a delay when coming back online
      const timer = setTimeout(() => {
        setShowOfflineMessage(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isOnline]);

  if (!showOfflineMessage) {
    return null;
  }

  return (
    <div style={{
      position: 'fixed',
      top: '1rem',
      right: '1rem',
      zIndex: 1000,
      background: isOnline ? 'linear-gradient(135deg, #10b981, #059669)' : 'linear-gradient(135deg, #ef4444, #dc2626)',
      borderRadius: '0.75rem',
      padding: '0.75rem 1rem',
      boxShadow: isOnline ? '0 4px 16px rgba(16, 185, 129, 0.3)' : '0 4px 16px rgba(239, 68, 68, 0.3)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      color: '#ffffff',
      transition: 'all 0.3s ease',
      backdropFilter: 'blur(8px)'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem'
      }}>
        {isOnline ? (
          <>
            <Wifi 
              size={16} 
              style={{ color: '#ffffff' }}
            />
            <span style={{
              fontSize: '0.75rem',
              fontWeight: '600'
            }}>Back online</span>
          </>
        ) : (
          <>
            <WifiOff 
              size={16} 
              style={{ color: '#ffffff' }}
            />
            <span style={{
              fontSize: '0.75rem',
              fontWeight: '600'
            }}>You're offline</span>
          </>
        )}
      </div>
    </div>
  );
};

interface PWAStatusProps {
  className?: string;
}

export const PWAStatus: React.FC<PWAStatusProps> = ({ className = '' }) => {
  const { isInstalled, isOnline, canInstall } = usePWA();

  return (
    <div style={{
      display: 'flex',
      gap: '0.5rem',
      alignItems: 'center'
    }}>
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        alignItems: 'center'
      }}>
        {isInstalled && (
          <span style={{
            background: 'linear-gradient(135deg, #10b981, #059669)',
            color: '#ffffff',
            padding: '0.25rem 0.75rem',
            borderRadius: '9999px',
            fontSize: '0.75rem',
            fontWeight: '600'
          }}>
            App Installed
          </span>
        )}
        {canInstall && !isInstalled && (
          <span style={{
            background: 'linear-gradient(135deg, #FF6B35, #F7931E)',
            color: '#ffffff',
            padding: '0.25rem 0.75rem',
            borderRadius: '9999px',
            fontSize: '0.75rem',
            fontWeight: '600'
          }}>
            Installable
          </span>
        )}
        <span style={{
          background: isOnline ? 'linear-gradient(135deg, #10b981, #059669)' : 'linear-gradient(135deg, #ef4444, #dc2626)',
          color: '#ffffff',
          padding: '0.25rem 0.75rem',
          borderRadius: '9999px',
          fontSize: '0.75rem',
          fontWeight: '600'
        }}>
          {isOnline ? 'Online' : 'Offline'}
        </span>
      </div>
    </div>
  );
};

// Combined PWA component that includes all PWA features
interface PWAManagerProps {
  showInstallPrompt?: boolean;
  showOfflineIndicator?: boolean;
  showStatus?: boolean;
  className?: string;
}

export const PWAManager: React.FC<PWAManagerProps> = ({
  showInstallPrompt = true,
  showOfflineIndicator = true,
  showStatus = false,
  className = ''
}) => {
  return (
    <div style={{
      position: 'relative',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      {showInstallPrompt && <PWABanner />}
      {showOfflineIndicator && <OfflineIndicator />}
      {showStatus && <PWAStatus />}
    </div>
  );
};

export default PWAManager;
