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
      <div className={`pwa-banner pwa-banner--update ${className}`}>
        <div className="pwa-banner__content">
          <RefreshCw className="pwa-banner__icon" size={20} />
          <div className="pwa-banner__text">
            <span className="pwa-banner__title">Update Available</span>
            <span className="pwa-banner__description">
              A new version of Vimarsh is ready to install
            </span>
          </div>
          <button
            onClick={handleUpdate}
            disabled={updating}
            className="pwa-banner__button pwa-banner__button--primary"
            aria-label="Update Vimarsh to latest version"
          >
            {updating ? 'Updating...' : 'Update'}
          </button>
          <button
            onClick={() => setShowUpdateBanner(false)}
            className="pwa-banner__button pwa-banner__button--dismiss"
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
      <div className={`pwa-banner pwa-banner--install ${className}`}>
        <div className="pwa-banner__content">
          <Download className="pwa-banner__icon" size={20} />
          <div className="pwa-banner__text">
            <span className="pwa-banner__title">Install Vimarsh</span>
            <span className="pwa-banner__description">
              Get the full app experience with offline access
            </span>
          </div>
          <button
            onClick={handleInstall}
            disabled={installing}
            className="pwa-banner__button pwa-banner__button--primary"
            aria-label="Install Vimarsh as an app"
          >
            {installing ? 'Installing...' : 'Install'}
          </button>
          <button
            onClick={dismissInstallBanner}
            className="pwa-banner__button pwa-banner__button--dismiss"
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
    <div className={`offline-indicator ${!isOnline ? 'offline-indicator--offline' : 'offline-indicator--online'} ${className}`}>
      <div className="offline-indicator__content">
        {isOnline ? (
          <>
            <Wifi className="offline-indicator__icon" size={16} />
            <span>Back online</span>
          </>
        ) : (
          <>
            <WifiOff className="offline-indicator__icon" size={16} />
            <span>You're offline</span>
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
    <div className={`pwa-status ${className}`}>
      <div className="pwa-status__indicators">
        {isInstalled && (
          <span className="pwa-status__badge pwa-status__badge--installed">
            App Installed
          </span>
        )}
        {canInstall && !isInstalled && (
          <span className="pwa-status__badge pwa-status__badge--installable">
            Installable
          </span>
        )}
        <span className={`pwa-status__badge ${isOnline ? 'pwa-status__badge--online' : 'pwa-status__badge--offline'}`}>
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
    <div className={`pwa-manager ${className}`}>
      {showInstallPrompt && <PWABanner />}
      {showOfflineIndicator && <OfflineIndicator />}
      {showStatus && <PWAStatus />}
    </div>
  );
};

export default PWAManager;
