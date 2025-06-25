import React, { useState } from 'react';
import { useABTesting, ABTest, ABTestResults } from '../contexts/ABTestingContext';
import './ABTestManager.css';

/**
 * A/B Test Management Component
 * For administrators to monitor and manage A/B tests
 * Provides insights into test performance and user experience optimization
 */

interface ABTestManagerProps {
  isAdmin?: boolean;
}

const ABTestManager: React.FC<ABTestManagerProps> = ({ isAdmin = false }) => {
  const { 
    activeTests, 
    userAssignments, 
    isOptedOut, 
    setOptOut, 
    getTestResults 
  } = useABTesting();
  
  const [selectedTest, setSelectedTest] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  if (!isAdmin) {
    // User view - simple opt-out control
    return (
      <div className="ab-test-user-controls">
        <h3>Interface Optimization</h3>
        <p>
          Vimarsh uses respectful A/B testing to improve your spiritual guidance experience.
          Your privacy is fully protected, and you can opt out at any time.
        </p>
        
        <div className="opt-out-control">
          <label className="opt-out-label">
            <input
              type="checkbox"
              checked={isOptedOut}
              onChange={(e) => setOptOut(e.target.checked)}
              className="opt-out-checkbox"
            />
            Opt out of interface optimization tests
          </label>
        </div>

        {!isOptedOut && (
          <div className="active-tests-info">
            <h4>Current Optimizations</h4>
            <p>
              You are participating in {Object.keys(userAssignments).length} interface 
              optimization experiments to enhance your spiritual journey.
            </p>
            
            {Object.values(userAssignments).map(assignment => {
              const test = activeTests.find(t => t.id === assignment.testId);
              return test ? (
                <div key={assignment.testId} className="test-participation">
                  <strong>{test.name}</strong>
                  <span className="variant-badge">
                    Variant: {assignment.variantId}
                  </span>
                </div>
              ) : null;
            })}
          </div>
        )}
      </div>
    );
  }

  // Admin view - full test management
  return (
    <div className="ab-test-manager">
      <div className="manager-header">
        <h2>A/B Test Management</h2>
        <p>Monitor and optimize the spiritual guidance interface</p>
      </div>

      <div className="test-overview">
        <div className="overview-stats">
          <div className="stat-card">
            <h3>{activeTests.length}</h3>
            <p>Active Tests</p>
          </div>
          <div className="stat-card">
            <h3>{activeTests.filter(t => t.isActive).length}</h3>
            <p>Running Tests</p>
          </div>
          <div className="stat-card">
            <h3>{Object.keys(userAssignments).length}</h3>
            <p>User Assignments</p>
          </div>
        </div>
      </div>

      <div className="test-list">
        <h3>Test Management</h3>
        {activeTests.map(test => (
          <TestCard 
            key={test.id}
            test={test}
            isSelected={selectedTest === test.id}
            onSelect={() => setSelectedTest(test.id)}
            onViewDetails={() => {
              setSelectedTest(test.id);
              setShowDetails(true);
            }}
            results={getTestResults(test.id)}
          />
        ))}
      </div>

      {showDetails && selectedTest && (
        <TestDetailsModal
          testId={selectedTest}
          onClose={() => {
            setShowDetails(false);
            setSelectedTest(null);
          }}
        />
      )}
    </div>
  );
};

interface TestCardProps {
  test: ABTest;
  isSelected: boolean;
  onSelect: () => void;
  onViewDetails: () => void;
  results: ABTestResults | null;
}

const TestCard: React.FC<TestCardProps> = ({ 
  test, 
  isSelected, 
  onSelect, 
  onViewDetails, 
  results 
}) => {
  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(date);
  };

  return (
    <div 
      className={`test-card ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
    >
      <div className="test-header">
        <h4>{test.name}</h4>
        <div className="test-status">
          <span className={`status-badge ${test.isActive ? 'active' : 'inactive'}`}>
            {test.isActive ? 'Active' : 'Inactive'}
          </span>
          <span className="target-percentage">
            {test.targetPercentage}% of users
          </span>
        </div>
      </div>

      <p className="test-description">{test.description}</p>

      <div className="test-variants">
        {test.variants.map(variant => (
          <div key={variant.id} className="variant-summary">
            <span className="variant-name">{variant.name}</span>
            <span className="variant-weight">{(variant.weight * 100).toFixed(0)}%</span>
          </div>
        ))}
      </div>

      <div className="test-timeline">
        <span>Started: {formatDate(test.startDate)}</span>
        {test.endDate && (
          <span>Ends: {formatDate(test.endDate)}</span>
        )}
      </div>

      {results && (
        <div className="test-results-preview">
          <span className={`significance ${results.isSignificant ? 'significant' : 'not-significant'}`}>
            {results.isSignificant ? '✓ Significant' : '○ Not Significant'}
          </span>
          {results.recommendedVariant && (
            <span className="recommended">
              Recommended: {results.recommendedVariant}
            </span>
          )}
        </div>
      )}

      <button 
        className="view-details-btn"
        onClick={(e) => {
          e.stopPropagation();
          onViewDetails();
        }}
      >
        View Details
      </button>
    </div>
  );
};

interface TestDetailsModalProps {
  testId: string;
  onClose: () => void;
}

const TestDetailsModal: React.FC<TestDetailsModalProps> = ({ testId, onClose }) => {
  const { activeTests, getTestResults } = useABTesting();
  
  const test = activeTests.find(t => t.id === testId);
  const results = getTestResults(testId);

  if (!test) {
    return null;
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{test.name}</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <div className="test-details">
            <h3>Test Configuration</h3>
            <div className="detail-grid">
              <div className="detail-item">
                <strong>Description:</strong>
                <span>{test.description}</span>
              </div>
              <div className="detail-item">
                <strong>Target Percentage:</strong>
                <span>{test.targetPercentage}%</span>
              </div>
              <div className="detail-item">
                <strong>Status:</strong>
                <span className={test.isActive ? 'active' : 'inactive'}>
                  {test.isActive ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="detail-item">
                <strong>Category:</strong>
                <span>{test.metadata?.category || 'General'}</span>
              </div>
            </div>
          </div>

          <div className="variant-details">
            <h3>Variants</h3>
            {test.variants.map(variant => (
              <div key={variant.id} className="variant-detail">
                <h4>{variant.name}</h4>
                <p>{variant.description}</p>
                <div className="variant-config">
                  <strong>Weight:</strong> {(variant.weight * 100).toFixed(0)}%
                </div>
                <div className="variant-config">
                  <strong>Configuration:</strong>
                  <pre>{JSON.stringify(variant.config, null, 2)}</pre>
                </div>
              </div>
            ))}
          </div>

          {results && (
            <div className="test-results">
              <h3>Results</h3>
              <div className="results-summary">
                <div className={`significance ${results.isSignificant ? 'significant' : 'not-significant'}`}>
                  Statistical Significance: {results.isSignificant ? 'Yes' : 'No'}
                </div>
                {results.recommendedVariant && (
                  <div className="recommended-variant">
                    Recommended Variant: {results.recommendedVariant}
                  </div>
                )}
              </div>

              <div className="variant-results">
                {results.variants.map(variantResult => (
                  <div key={variantResult.variantId} className="variant-result">
                    <h4>{variantResult.variantId}</h4>
                    <div className="result-metrics">
                      <span>Participants: {variantResult.participants}</span>
                      <span>Conversions: {variantResult.conversions}</span>
                      <span>Conversion Rate: {(variantResult.conversionRate * 100).toFixed(2)}%</span>
                      <span>Significance: {variantResult.significance.toFixed(3)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ABTestManager;
