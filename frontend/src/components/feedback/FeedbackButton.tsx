import React, { useState } from 'react';
import { MessageCircle } from 'lucide-react';
import FeedbackModal from './FeedbackModal';

interface FeedbackButtonProps {
  context?: {
    query?: string;
    response?: string;
    sessionId?: string;
  };
  className?: string;
  variant?: 'floating' | 'inline' | 'compact';
}

const FeedbackButton: React.FC<FeedbackButtonProps> = ({ 
  context, 
  className = '', 
  variant = 'inline' 
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const getButtonStyles = () => {
    switch (variant) {
      case 'floating':
        return 'fixed bottom-6 right-6 w-14 h-14 bg-blue-500 hover:bg-blue-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center z-40';
      case 'compact':
        return 'px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors flex items-center space-x-2';
      default:
        return 'px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors flex items-center space-x-2';
    }
  };

  const getIconSize = () => {
    switch (variant) {
      case 'floating':
        return 24;
      case 'compact':
        return 16;
      default:
        return 20;
    }
  };

  return (
    <>
      <button
        onClick={() => setIsModalOpen(true)}
        className={`${getButtonStyles()} ${className}`}
        title="Share feedback about your experience"
      >
        <MessageCircle size={getIconSize()} />
        {variant !== 'floating' && (
          <span className="font-medium">
            {variant === 'compact' ? 'Feedback' : 'Share Feedback'}
          </span>
        )}
      </button>

      <FeedbackModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        context={context}
      />
    </>
  );
};

export default FeedbackButton;
