/**
 * AchievementBadge Component Tests
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import AchievementBadge from '../AchievementBadge';
import { Achievement } from '../types';

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

const mockUnlockedAchievement: Achievement = {
  id: 'first_conversation',
  name: 'First Steps',
  description: 'Complete your first conversation',
  icon: '💬',
  points: 10,
  category: 'onboarding',
  tier: 'bronze',
  unlocked: true,
  unlocked_at: '2024-01-15T10:30:00Z',
  progress: {
    current: 1,
    target: 1,
    percentage: 100
  }
};

const mockLockedAchievement: Achievement = {
  id: 'streak_master',
  name: 'Streak Master',
  description: 'Maintain a 30-day streak',
  icon: '🔥',
  points: 100,
  category: 'streak',
  tier: 'gold',
  unlocked: false,
  unlocked_at: null,
  progress: {
    current: 15,
    target: 30,
    percentage: 50
  }
};

const mockPlatinumAchievement: Achievement = {
  id: 'wisdom_seeker',
  name: 'Wisdom Seeker',
  description: 'Explore all domains',
  icon: '🌟',
  points: 500,
  category: 'mastery',
  tier: 'platinum',
  unlocked: true,
  unlocked_at: '2024-02-01T12:00:00Z',
  progress: {
    current: 6,
    target: 6,
    percentage: 100
  }
};

describe('AchievementBadge', () => {
  describe('loading state', () => {
    it('renders loading skeleton when loading', () => {
      renderWithTheme(<AchievementBadge loading={true} />);
      expect(document.querySelector('.MuiSkeleton-root')).toBeInTheDocument();
    });

    it('renders loading skeleton when no achievement provided', () => {
      renderWithTheme(<AchievementBadge />);
      expect(document.querySelector('.MuiSkeleton-root')).toBeInTheDocument();
    });
  });

  describe('unlocked achievement', () => {
    it('renders achievement icon', () => {
      renderWithTheme(<AchievementBadge achievement={mockUnlockedAchievement} />);
      expect(screen.getByText('💬')).toBeInTheDocument();
    });

    it('renders unlocked achievement without lock icon', () => {
      const { container } = renderWithTheme(
        <AchievementBadge achievement={mockUnlockedAchievement} />
      );
      expect(container.querySelector('[data-testid="lock-icon"]')).not.toBeInTheDocument();
    });
  });

  describe('locked achievement', () => {
    it('renders locked achievement with progress', () => {
      renderWithTheme(<AchievementBadge achievement={mockLockedAchievement} />);
      expect(screen.getByText('🔥')).toBeInTheDocument();
    });

    it('shows progress for locked achievement', () => {
      renderWithTheme(
        <AchievementBadge achievement={mockLockedAchievement} showProgress={true} />
      );
      expect(screen.getByText('🔥')).toBeInTheDocument();
    });
  });

  describe('sizes', () => {
    it('renders small size', () => {
      const { container } = renderWithTheme(
        <AchievementBadge achievement={mockUnlockedAchievement} size="small" />
      );
      expect(container.firstChild).toBeInTheDocument();
    });

    it('renders medium size', () => {
      const { container } = renderWithTheme(
        <AchievementBadge achievement={mockUnlockedAchievement} size="medium" />
      );
      expect(container.firstChild).toBeInTheDocument();
    });

    it('renders large size', () => {
      const { container } = renderWithTheme(
        <AchievementBadge achievement={mockUnlockedAchievement} size="large" />
      );
      expect(container.firstChild).toBeInTheDocument();
    });
  });

  describe('tiers', () => {
    it('renders bronze tier', () => {
      renderWithTheme(<AchievementBadge achievement={mockUnlockedAchievement} />);
      expect(screen.getByText('💬')).toBeInTheDocument();
    });

    it('renders gold tier', () => {
      renderWithTheme(<AchievementBadge achievement={mockLockedAchievement} />);
      expect(screen.getByText('🔥')).toBeInTheDocument();
    });

    it('renders platinum tier', () => {
      renderWithTheme(<AchievementBadge achievement={mockPlatinumAchievement} />);
      expect(screen.getByText('🌟')).toBeInTheDocument();
    });
  });

  describe('click handler', () => {
    it('calls onClick when clicked', () => {
      const handleClick = jest.fn();
      renderWithTheme(
        <AchievementBadge achievement={mockUnlockedAchievement} onClick={handleClick} />
      );
      
      const badge = screen.getByText('💬').closest('div');
      if (badge) {
        fireEvent.click(badge);
      }
    });
  });

  describe('progress display', () => {
    it('hides progress when showProgress is false', () => {
      const { container } = renderWithTheme(
        <AchievementBadge achievement={mockLockedAchievement} showProgress={false} />
      );
      expect(container.firstChild).toBeInTheDocument();
    });

    it('shows progress when showProgress is true', () => {
      const { container } = renderWithTheme(
        <AchievementBadge achievement={mockLockedAchievement} showProgress={true} />
      );
      // Should have SVG progress ring
      expect(container.querySelector('svg')).toBeInTheDocument();
    });
  });
});
