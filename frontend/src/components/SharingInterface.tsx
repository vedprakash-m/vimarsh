import React, { useState, useCallback } from 'react';
import { Share2, Copy, Check, X } from 'lucide-react';
import { getApiBaseUrl } from '../config/environment';

// Platform icons as simple SVG components
const TwitterIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
  </svg>
);

const FacebookIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
  </svg>
);

const LinkedInIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
  </svg>
);

const WhatsAppIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
  </svg>
);

const TelegramIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
  </svg>
);

interface ShareableContent {
  text: string;
  personality: string;
  citation?: string;
  domain: string;
  messageId?: string;
}

interface SharingInterfaceProps {
  content: ShareableContent;
  onShareComplete?: (platform: string) => void;
  onClose?: () => void;
  variant?: 'inline' | 'button';
  size?: 'small' | 'medium';
  autoOpen?: boolean;
  isModal?: boolean;
}

// Domain-specific hashtags
const getDomainHashtags = (domain: string): string[] => {
  const domainTags: Record<string, string[]> = {
    spiritual: ['SpiritualWisdom', 'InnerPeace', 'DivineGuidance'],
    scientific: ['ScienceWisdom', 'Innovation', 'Discovery'],
    philosophical: ['Philosophy', 'DeepThinking', 'Wisdom'],
    historical: ['HistoricalWisdom', 'Leadership', 'Lessons'],
    leadership: ['LeadershipWisdom', 'Success', 'Guidance'],
    literary: ['LiteraryWisdom', 'Poetry', 'Art'],
    psychology: ['MindWisdom', 'SelfGrowth', 'Understanding']
  };
  return domainTags[domain] || ['Wisdom'];
};

export const SharingInterface: React.FC<SharingInterfaceProps> = ({
  content,
  onShareComplete,
  onClose,
  variant = 'inline',
  size = 'small',
  autoOpen = false,
  isModal = false
}) => {
  const [copied, setCopied] = useState(false);
  const [showPlatforms, setShowPlatforms] = useState(autoOpen || isModal);
  const [isAnimating, setIsAnimating] = useState(false);

  // Handle closing for modal mode
  const handleClose = useCallback(() => {
    setShowPlatforms(false);
    if (isModal && onClose) {
      onClose();
    }
  }, [isModal, onClose]);

  // Generate shareable text with proper formatting
  const generateShareText = useCallback((forPlatform?: string) => {
    // Truncate for Twitter's character limit
    const maxLength = forPlatform === 'twitter' ? 220 : 400;
    const truncatedText = content.text.length > maxLength
      ? content.text.substring(0, maxLength - 3) + '...'
      : content.text;

    const attribution = `— ${content.personality}`;
    const citation = content.citation ? ` (${content.citation})` : '';
    
    // Get domain-specific hashtags
    const hashtags = getDomainHashtags(content.domain);
    const hashtagString = hashtags.slice(0, 2).map(t => `#${t}`).join(' ');

    return `"${truncatedText}"\n\n${attribution}${citation}\n\n${hashtagString} #Vimarsh`;
  }, [content]);

  // Get share URL 
  const getShareUrl = useCallback(() => {
    return `https://vimarsh.vedprakash.net`;
  }, []);

  // Track share event (analytics)
  const trackShare = useCallback(async (platform: string) => {
    try {
      // Send analytics event
      const apiUrl = getApiBaseUrl();
      const response = await fetch(`${apiUrl}/share/track`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform,
          content_type: 'wisdom',
          personality_id: content.personality,
          domain: content.domain
        })
      });
      
      if (!response.ok) {
        console.warn('Share tracking failed');
      }
    } catch (error) {
      // Silent fail for analytics
      console.debug('Share tracking error:', error);
    }
    
    onShareComplete?.(platform);
  }, [content, onShareComplete]);

  // Platform-specific share handlers
  const shareHandlers = {
    twitter: () => {
      const text = generateShareText('twitter');
      const shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(getShareUrl())}`;
      window.open(shareUrl, '_blank', 'width=550,height=420,noopener,noreferrer');
      trackShare('twitter');
      handleClose();
    },
    facebook: () => {
      const shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(getShareUrl())}&quote=${encodeURIComponent(generateShareText('facebook'))}`;
      window.open(shareUrl, '_blank', 'width=550,height=420,noopener,noreferrer');
      trackShare('facebook');
      handleClose();
    },
    linkedin: () => {
      const shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(getShareUrl())}`;
      window.open(shareUrl, '_blank', 'width=550,height=500,noopener,noreferrer');
      trackShare('linkedin');
      handleClose();
    },
    whatsapp: () => {
      const text = generateShareText('whatsapp');
      const shareUrl = `https://wa.me/?text=${encodeURIComponent(text + '\n\n' + getShareUrl())}`;
      window.open(shareUrl, '_blank', 'noopener,noreferrer');
      trackShare('whatsapp');
      handleClose();
    },
    telegram: () => {
      const text = generateShareText('telegram');
      const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(getShareUrl())}&text=${encodeURIComponent(text)}`;
      window.open(shareUrl, '_blank', 'noopener,noreferrer');
      trackShare('telegram');
      handleClose();
    },
    copy: async () => {
      try {
        const textToCopy = generateShareText() + '\n\n' + getShareUrl();
        await navigator.clipboard.writeText(textToCopy);
        setCopied(true);
        setIsAnimating(true);
        trackShare('copy');
        
        setTimeout(() => {
          setCopied(false);
          setIsAnimating(false);
        }, 2000);
      } catch (error) {
        console.error('Copy failed:', error);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = generateShareText() + '\n\n' + getShareUrl();
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    },
    native: async () => {
      if (navigator.share) {
        try {
          await navigator.share({
            title: `Wisdom from ${content.personality}`,
            text: generateShareText('native'),
            url: getShareUrl()
          });
          trackShare('native');
        } catch (error) {
          if ((error as Error).name !== 'AbortError') {
            console.error('Native share failed:', error);
          }
        }
      }
      handleClose();
    }
  };

  const buttonSize = size === 'small' ? '1.75rem' : '2.25rem';
  const iconSize = size === 'small' ? 14 : 18;
  const fontSize = size === 'small' ? '0.75rem' : '0.85rem';

  // Get domain color for styling
  const getDomainColor = (domain: string) => {
    const colors: Record<string, string> = {
      spiritual: '#ea580c',
      scientific: '#2563eb',
      historical: '#16a34a',
      philosophical: '#9333ea',
      literary: '#059669',
      leadership: '#dc2626',
      psychology: '#8b5cf6'
    };
    return colors[domain] || '#6b7280';
  };

  const domainColor = getDomainColor(content.domain);

  // Render sharing options panel (used in both modal and dropdown)
  const renderSharingOptions = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
      <PlatformButton 
        icon={<TwitterIcon />} 
        label="X (Twitter)" 
        onClick={shareHandlers.twitter}
        hoverColor="#1DA1F2"
      />
      <PlatformButton 
        icon={<FacebookIcon />} 
        label="Facebook" 
        onClick={shareHandlers.facebook}
        hoverColor="#1877F2"
      />
      <PlatformButton 
        icon={<LinkedInIcon />} 
        label="LinkedIn" 
        onClick={shareHandlers.linkedin}
        hoverColor="#0A66C2"
      />
      <PlatformButton 
        icon={<WhatsAppIcon />} 
        label="WhatsApp" 
        onClick={shareHandlers.whatsapp}
        hoverColor="#25D366"
      />
      <PlatformButton 
        icon={<TelegramIcon />} 
        label="Telegram" 
        onClick={shareHandlers.telegram}
        hoverColor="#0088cc"
      />
      
      <div style={{ 
        height: '1px', 
        background: '#e2e8f0', 
        margin: '0.35rem 0' 
      }} />
      
      <PlatformButton 
        icon={copied ? <Check size={16} /> : <Copy size={16} />} 
        label={copied ? "Copied!" : "Copy Link"}
        onClick={shareHandlers.copy}
        hoverColor="#10b981"
        isActive={copied}
      />
      
      {/* Native share for mobile */}
      {'share' in navigator && (
        <PlatformButton 
          icon={<Share2 size={16} />} 
          label="More options..." 
          onClick={shareHandlers.native}
          hoverColor="#6366f1"
        />
      )}
    </div>
  );

  // Modal mode - full screen overlay
  if (isModal) {
    return (
      <>
        {/* Full screen backdrop */}
        <div
          onClick={handleClose}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            zIndex: 9998,
            animation: 'fadeIn 0.2s ease-out'
          }}
        />
        
        {/* Modal content */}
        <div
          style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            background: '#ffffff',
            borderRadius: '1rem',
            padding: '1.5rem',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
            zIndex: 9999,
            minWidth: '280px',
            maxWidth: '90vw',
            animation: 'scaleIn 0.2s ease-out'
          }}
        >
          {/* Close button */}
          <button
            onClick={handleClose}
            style={{
              position: 'absolute',
              top: '0.75rem',
              right: '0.75rem',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '0.5rem',
              borderRadius: '0.5rem',
              color: '#94a3b8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#f1f5f9';
              e.currentTarget.style.color = '#64748b';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'none';
              e.currentTarget.style.color = '#94a3b8';
            }}
            aria-label="Close share modal"
          >
            <X size={20} />
          </button>

          {/* Modal header */}
          <div style={{ marginBottom: '1rem', paddingRight: '2rem' }}>
            <h3 style={{
              fontSize: '1.1rem',
              fontWeight: '600',
              color: '#1e293b',
              margin: '0 0 0.5rem 0',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <Share2 size={18} style={{ color: domainColor }} />
              Share this wisdom
            </h3>
            <p style={{
              fontSize: '0.85rem',
              color: '#64748b',
              margin: 0,
              lineHeight: '1.4'
            }}>
              "{content.text.length > 80 ? content.text.substring(0, 80) + '...' : content.text}"
            </p>
            <p style={{
              fontSize: '0.75rem',
              color: '#94a3b8',
              margin: '0.25rem 0 0 0',
              fontStyle: 'italic'
            }}>
              — {content.personality}
            </p>
          </div>

          <div style={{ 
            fontSize: '0.7rem', 
            color: '#94a3b8', 
            marginBottom: '0.5rem',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Share to
          </div>

          {renderSharingOptions()}
        </div>

        <style>{`
          @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
          }
          @keyframes scaleIn {
            from {
              opacity: 0;
              transform: translate(-50%, -50%) scale(0.9);
            }
            to {
              opacity: 1;
              transform: translate(-50%, -50%) scale(1);
            }
          }
        `}</style>
      </>
    );
  }

  // Inline mode - button with dropdown
  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      {/* Share Trigger Button */}
      <button
        onClick={() => setShowPlatforms(!showPlatforms)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.35rem',
          padding: size === 'small' ? '0.35rem 0.65rem' : '0.5rem 0.85rem',
          background: showPlatforms ? `${domainColor}15` : 'transparent',
          border: `1px solid ${showPlatforms ? domainColor : '#e2e8f0'}`,
          borderRadius: '0.5rem',
          color: showPlatforms ? domainColor : '#64748b',
          fontSize,
          fontWeight: '500',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          outline: 'none'
        }}
        onMouseEnter={(e) => {
          if (!showPlatforms) {
            e.currentTarget.style.borderColor = domainColor;
            e.currentTarget.style.color = domainColor;
            e.currentTarget.style.background = `${domainColor}10`;
          }
        }}
        onMouseLeave={(e) => {
          if (!showPlatforms) {
            e.currentTarget.style.borderColor = '#e2e8f0';
            e.currentTarget.style.color = '#64748b';
            e.currentTarget.style.background = 'transparent';
          }
        }}
        aria-label="Share this wisdom"
        aria-expanded={showPlatforms}
      >
        <Share2 size={iconSize} />
        <span>Share</span>
      </button>

      {/* Platform Dropdown */}
      {showPlatforms && (
        <>
          {/* Backdrop to close dropdown */}
          <div
            onClick={handleClose}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 998
            }}
          />
          
          <div
            style={{
              position: 'absolute',
              bottom: '100%',
              left: '50%',
              transform: 'translateX(-50%)',
              marginBottom: '0.5rem',
              background: '#ffffff',
              borderRadius: '0.75rem',
              padding: '0.5rem',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
              border: '1px solid #e2e8f0',
              zIndex: 999,
              minWidth: '180px',
              animation: 'fadeInUp 0.2s ease-out'
            }}
          >
            {/* Close button */}
            <button
              onClick={handleClose}
              style={{
                position: 'absolute',
                top: '0.35rem',
                right: '0.35rem',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '0.25rem',
                borderRadius: '0.25rem',
                color: '#94a3b8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              aria-label="Close share menu"
            >
              <X size={14} />
            </button>

            <div style={{ 
              fontSize: '0.7rem', 
              color: '#94a3b8', 
              marginBottom: '0.5rem',
              paddingLeft: '0.5rem',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              Share to
            </div>

            {renderSharingOptions()}
          </div>
        </>
      )}

      {/* Animation keyframes */}
      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateX(-50%) translateY(8px);
          }
          to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

// Helper component for platform buttons
interface PlatformButtonProps {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  hoverColor: string;
  isActive?: boolean;
}

const PlatformButton: React.FC<PlatformButtonProps> = ({ 
  icon, 
  label, 
  onClick, 
  hoverColor,
  isActive = false
}) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.65rem',
        padding: '0.5rem 0.65rem',
        background: isHovered || isActive ? `${hoverColor}15` : 'transparent',
        border: 'none',
        borderRadius: '0.5rem',
        color: isHovered || isActive ? hoverColor : '#475569',
        fontSize: '0.85rem',
        fontWeight: '500',
        cursor: 'pointer',
        transition: 'all 0.15s ease',
        width: '100%',
        textAlign: 'left'
      }}
    >
      <span style={{ 
        display: 'flex', 
        alignItems: 'center',
        color: isHovered || isActive ? hoverColor : '#64748b'
      }}>
        {icon}
      </span>
      {label}
    </button>
  );
};

export default SharingInterface;
