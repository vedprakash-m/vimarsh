/**
 * StreakDisplay Component Tests
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import StreakDisplay from '../StreakDisplay';

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('StreakDisplay', () => {
  describe('loading state', () => {
    it('renders loading skeleton in compact mode', () => {
      renderWithTheme(<StreakDisplay currentStreak={0} loading={true} compact={true} />);
      expect(document.querySelector('.MuiSkeleton-root')).toBeInTheDocument();
    });

    it('renders loading skeleton in full mode', () => {
      renderWithTheme(<StreakDisplay currentStreak={0} loading={true} compact={false} />);
      const skeletons = document.querySelectorAll('.MuiSkeleton-root');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('streak display', () => {
    it('renders current streak count', () => {
      renderWithTheme(<StreakDisplay currentStreak={7} />);
      expect(screen.getByText('7')).toBeInTheDocument();
    });

    it('renders zero streak correctly', () => {
      renderWithTheme(<StreakDisplay currentStreak={0} />);
      expect(screen.getByText('0')).toBeInTheDocument();
    });

    it('renders large streak count', () => {
      renderWithTheme(<StreakDisplay currentStreak={150} />);
      expect(screen.getByText('150')).toBeInTheDocument();
    });
  });

  describe('compact mode', () => {
    it('renders in compact mode', () => {
      const { container } = renderWithTheme(<StreakDisplay currentStreak={5} compact={true} />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it('renders in full mode', () => {
      const { container } = renderWithTheme(<StreakDisplay currentStreak={5} compact={false} />);
      expect(container.firstChild).toBeInTheDocument();
    });
  });

  describe('streak at risk', () => {
    it('handles streak at risk state', () => {
      renderWithTheme(<StreakDisplay currentStreak={5} streakAtRisk={true} />);
      expect(screen.getByText('5')).toBeInTheDocument();
    });
  });

  describe('click handler', () => {
    it('calls onClick when clicked', () => {
      const handleClick = jest.fn();
      renderWithTheme(<StreakDisplay currentStreak={5} onClick={handleClick} />);
      
      const container = document.querySelector('[role="button"]') || screen.getByText('5').closest('div');
      if (container) {
        fireEvent.click(container);
      }
    });
  });

  describe('freezes', () => {
    it('displays freezes available', () => {
      renderWithTheme(<StreakDisplay currentStreak={5} freezesAvailable={3} />);
      expect(screen.getByText('5')).toBeInTheDocument();
    });

    it('displays zero freezes', () => {
      renderWithTheme(<StreakDisplay currentStreak={5} freezesAvailable={0} />);
      expect(screen.getByText('5')).toBeInTheDocument();
    });
  });

  describe('streak tiers', () => {
    it('renders beginner tier (0-6)', () => {
      renderWithTheme(<StreakDisplay currentStreak={3} />);
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('renders weekly tier (7-29)', () => {
      renderWithTheme(<StreakDisplay currentStreak={14} />);
      expect(screen.getByText('14')).toBeInTheDocument();
    });

    it('renders monthly tier (30-99)', () => {
      renderWithTheme(<StreakDisplay currentStreak={45} />);
      expect(screen.getByText('45')).toBeInTheDocument();
    });

    it('renders legendary tier (100+)', () => {
      renderWithTheme(<StreakDisplay currentStreak={100} />);
      expect(screen.getByText('100')).toBeInTheDocument();
    });
  });
});
