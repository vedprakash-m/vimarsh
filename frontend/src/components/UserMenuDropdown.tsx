import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Settings, LogOut, BarChart3, Brain, Shield, ChevronDown } from 'lucide-react';
import { useAuth } from '../auth/AuthProvider';
import { useAdmin } from '../contexts/AdminProviderContext';

interface UserMenuDropdownProps {
  compact?: boolean;
}

const UserMenuDropdown: React.FC<UserMenuDropdownProps> = ({ compact = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { account, logout } = useAuth();
  const { user: adminUser } = useAdmin();

  const showAdminButton = adminUser?.isAdmin;
  const userName = account?.name || account?.username?.split('@')[0] || 'User';
  const userEmail = account?.username || '';
  const userInitial = userName.charAt(0).toUpperCase();

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close on Escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    if (isOpen) {
      window.addEventListener('keydown', handleEscape);
      return () => window.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen]);

  const handleLogout = async () => {
    setIsOpen(false);
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const menuItems = [
    {
      icon: <BarChart3 size={16} />,
      label: 'Progress Dashboard',
      onClick: () => { setIsOpen(false); navigate('/progress'); },
    },
    {
      icon: <Brain size={16} />,
      label: 'Memory Dashboard',
      onClick: () => { setIsOpen(false); navigate('/memory'); },
    },
    {
      icon: <Settings size={16} />,
      label: 'Settings',
      onClick: () => { setIsOpen(false); navigate('/settings'); },
    },
    ...(showAdminButton ? [{
      icon: <Shield size={16} />,
      label: 'Admin Panel',
      onClick: () => { setIsOpen(false); navigate('/admin'); },
      accent: true,
    }] : []),
  ];

  return (
    <div ref={menuRef} style={{ position: 'relative' }}>
      {/* Avatar Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          background: isOpen ? '#f1f5f9' : 'transparent',
          border: '1px solid transparent',
          borderRadius: '2rem',
          padding: compact ? '0.25rem 0.5rem 0.25rem 0.25rem' : '0.375rem 0.75rem 0.375rem 0.375rem',
          cursor: 'pointer',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
        }}
        onMouseEnter={(e) => {
          if (!isOpen) e.currentTarget.style.background = '#f8fafc';
          e.currentTarget.style.borderColor = '#e2e8f0';
        }}
        onMouseLeave={(e) => {
          if (!isOpen) e.currentTarget.style.background = 'transparent';
          e.currentTarget.style.borderColor = 'transparent';
        }}
        aria-label="User menu"
        aria-expanded={isOpen}
        aria-haspopup="menu"
      >
        {/* Avatar circle */}
        <div style={{
          width: compact ? '28px' : '32px',
          height: compact ? '28px' : '32px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #f97316, #f59e0b)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: compact ? '0.75rem' : '0.8rem',
          fontWeight: '600',
          flexShrink: 0,
        }}>
          {userInitial}
        </div>
        {!compact && (
          <ChevronDown 
            size={14} 
            style={{ 
              color: '#64748b',
              transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 0.2s ease'
            }} 
          />
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          role="menu"
          style={{
            position: 'absolute',
            right: 0,
            top: 'calc(100% + 8px)',
            width: '260px',
            background: '#ffffff',
            borderRadius: '0.75rem',
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08)',
            border: '1px solid #e2e8f0',
            overflow: 'hidden',
            zIndex: 1000,
            animation: 'menuFadeIn 0.15s ease-out',
            fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
          }}
        >
          {/* User Info Header */}
          <div style={{
            padding: '1rem 1rem 0.75rem',
            borderBottom: '1px solid #f1f5f9',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
            }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #f97316, #f59e0b)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '1rem',
                fontWeight: '600',
                flexShrink: 0,
              }}>
                {userInitial}
              </div>
              <div style={{ minWidth: 0 }}>
                <div style={{
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  color: '#1e293b',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}>
                  {userName}
                </div>
                <div style={{
                  fontSize: '0.75rem',
                  color: '#94a3b8',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}>
                  {userEmail}
                </div>
              </div>
            </div>
          </div>

          {/* Menu Items */}
          <div style={{ padding: '0.375rem 0' }}>
            {menuItems.map((item, index) => (
              <button
                key={index}
                role="menuitem"
                onClick={item.onClick}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  width: '100%',
                  padding: '0.625rem 1rem',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '0.8125rem',
                  fontWeight: '500',
                  color: (item as any).accent ? '#f59e0b' : '#475569',
                  transition: 'all 0.15s ease',
                  textAlign: 'left',
                  fontFamily: 'inherit',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#f8fafc';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent';
                }}
              >
                <span style={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  opacity: 0.7 
                }}>
                  {item.icon}
                </span>
                {item.label}
              </button>
            ))}
          </div>

          {/* Divider + Sign Out */}
          <div style={{ borderTop: '1px solid #f1f5f9', padding: '0.375rem 0' }}>
            <button
              role="menuitem"
              onClick={handleLogout}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                width: '100%',
                padding: '0.625rem 1rem',
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                fontSize: '0.8125rem',
                fontWeight: '500',
                color: '#dc2626',
                transition: 'all 0.15s ease',
                textAlign: 'left',
                fontFamily: 'inherit',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#fef2f2';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent';
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', opacity: 0.7 }}>
                <LogOut size={16} />
              </span>
              Sign Out
            </button>
          </div>
        </div>
      )}

      {/* Animation keyframes */}
      <style>{`
        @keyframes menuFadeIn {
          from { opacity: 0; transform: translateY(-4px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default UserMenuDropdown;
