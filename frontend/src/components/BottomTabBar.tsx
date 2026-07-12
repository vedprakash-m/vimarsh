import React, { useEffect, useState } from 'react';
import { MessageSquare, Users, TrendingUp, User } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function BottomTabBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Only show on mobile
    const checkVisibility = () => {
      setIsVisible(window.innerWidth <= 768);
    };
    
    checkVisibility();
    window.addEventListener('resize', checkVisibility);
    return () => window.removeEventListener('resize', checkVisibility);
  }, []);

  if (!isVisible) return null;

  const tabs = [
    { id: 'chat', path: '/guidance', icon: MessageSquare, label: 'Chat' },
    { id: 'minds', path: '/wisdom/archive', icon: Users, label: 'Minds' },
    { id: 'progress', path: '/progress', icon: TrendingUp, label: 'Progress' },
    { id: 'profile', path: '/settings', icon: User, label: 'Profile' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 pb-safe bg-gradient-to-t from-canvas via-canvas to-transparent md:hidden pointer-events-none">
      <nav className="flex items-center justify-around bg-surface/90 backdrop-blur-xl border border-border-subtle rounded-full p-2 shadow-lg pointer-events-auto w-full max-w-sm mx-auto">
        {tabs.map((tab) => {
          const isActive = location.pathname.startsWith(tab.path);
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => navigate(tab.path)}
              className={`flex flex-col items-center justify-center w-14 h-12 rounded-full transition-all duration-300 ${
                isActive ? 'text-accent' : 'text-tertiary hover:text-secondary'
              }`}
            >
              <Icon size={20} strokeWidth={isActive ? 2.5 : 2} className={isActive ? 'drop-shadow-[0_0_8px_var(--domain-glow)]' : ''} />
              <span className="text-[10px] font-medium mt-1">{tab.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}
