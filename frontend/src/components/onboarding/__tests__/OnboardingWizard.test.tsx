import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import OnboardingWizard from '../OnboardingWizard';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock PersonalityContext to avoid API calls in tests
jest.mock('../../../contexts/PersonalityContext', () => {
  const actual = jest.requireActual('../../../contexts/PersonalityContext');
  return {
    ...actual,
    usePersonality: () => ({
      availablePersonalities: [
        { id: '1', name: 'Krishna', domain: 'spiritual' },
        { id: '2', name: 'Aurelius', domain: 'philosophical' }
      ],
      personalityLoading: false,
      setSelectedPersonality: jest.fn()
    })
  };
});

describe('OnboardingWizard Component', () => {
  const mockOnClose = jest.fn();
  const mockOnSelectPersonality = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  const TestWrapper = ({ children }: { children: React.ReactNode }) => (
    <BrowserRouter>
      {children}
    </BrowserRouter>
  );

  it('renders exactly 6 static domain cards for immediate matching', () => {
    render(
      <TestWrapper>
        <OnboardingWizard
          open={true}
          onClose={mockOnClose}
          onSelectPersonality={mockOnSelectPersonality}
        />
      </TestWrapper>
    );

    // Verify header exists
    expect(screen.getByText(/Choose your path/i)).toBeInTheDocument();

    // Verify 6 hardcoded domains exist
    expect(screen.getByText('Spiritual')).toBeInTheDocument();
    expect(screen.getByText('Philosophical')).toBeInTheDocument();
    expect(screen.getByText('Leadership')).toBeInTheDocument();
    expect(screen.getByText('Scientific')).toBeInTheDocument();
    expect(screen.getByText('Literary')).toBeInTheDocument();
    expect(screen.getByText('Psychology')).toBeInTheDocument();
  });

  it('navigates immediately to guidance view upon domain selection bypassing legacy arrays', () => {
    render(
      <TestWrapper>
        <OnboardingWizard
          open={true}
          onClose={mockOnClose}
          onSelectPersonality={mockOnSelectPersonality}
        />
      </TestWrapper>
    );

    // Click the spiritual domain
    const spiritualCard = screen.getByText('Spiritual');
    fireEvent.click(spiritualCard);

    // Verify it closed that screen and routed properly passing ID
    expect(mockOnClose).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/guidance');
    expect(mockOnSelectPersonality).toHaveBeenCalledWith('1'); // ID is '1' logic
  });
});
