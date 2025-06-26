import React, { useState, useRef } from 'react';
import { 
  Star, 
  MessageSquare, 
  Mic, 
  MicOff, 
  Send, 
  X, 
  Heart,
  ThumbsUp,
  ThumbsDown,
  Lightbulb,
  AlertTriangle
} from 'lucide-react';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  context?: {
    query?: string;
    response?: string;
    sessionId?: string;
  };
}

type FeedbackType = 'rating' | 'text_feedback' | 'voice_feedback' | 'spiritual_accuracy' | 'user_experience' | 'feature_request' | 'bug_report';

const FeedbackModal: React.FC<FeedbackModalProps> = ({ isOpen, onClose, context }) => {
  const [feedbackType, setFeedbackType] = useState<FeedbackType>('rating');
  const [rating, setRating] = useState<number>(0);
  const [hoverRating, setHoverRating] = useState<number>(0);
  const [textFeedback, setTextFeedback] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const feedbackTypes = [
    { type: 'rating' as FeedbackType, icon: Star, label: 'Rate Experience', color: 'text-yellow-500' },
    { type: 'text_feedback' as FeedbackType, icon: MessageSquare, label: 'Written Feedback', color: 'text-blue-500' },
    { type: 'voice_feedback' as FeedbackType, icon: Mic, label: 'Voice Feedback', color: 'text-green-500' },
    { type: 'spiritual_accuracy' as FeedbackType, icon: Heart, label: 'Spiritual Accuracy', color: 'text-purple-500' },
    { type: 'feature_request' as FeedbackType, icon: Lightbulb, label: 'Feature Request', color: 'text-orange-500' },
    { type: 'bug_report' as FeedbackType, icon: AlertTriangle, label: 'Report Issue', color: 'text-red-500' }
  ];

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const submitFeedback = async () => {
    setIsSubmitting(true);
    
    try {
      const feedbackData = {
        feedback_type: feedbackType,
        rating: rating || undefined,
        text_content: textFeedback || undefined,
        context: context || {},
        timestamp: new Date().toISOString()
      };

      // Create FormData for file upload if voice feedback
      const formData = new FormData();
      formData.append('feedback', JSON.stringify(feedbackData));
      
      if (audioBlob && feedbackType === 'voice_feedback') {
        formData.append('audio', audioBlob, 'feedback.wav');
      }

      const response = await fetch('/api/feedback/collect', {
        method: 'POST',
        body: feedbackType === 'voice_feedback' ? formData : JSON.stringify(feedbackData),
        headers: feedbackType === 'voice_feedback' ? {} : {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setSubmitted(true);
        setTimeout(() => {
          onClose();
          resetForm();
        }, 2000);
      } else {
        throw new Error('Failed to submit feedback');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFeedbackType('rating');
    setRating(0);
    setHoverRating(0);
    setTextFeedback('');
    setAudioBlob(null);
    setSubmitted(false);
  };

  const canSubmit = () => {
    switch (feedbackType) {
      case 'rating':
        return rating > 0;
      case 'text_feedback':
      case 'feature_request':
      case 'bug_report':
      case 'spiritual_accuracy':
      case 'user_experience':
        return textFeedback.trim().length > 0;
      case 'voice_feedback':
        return audioBlob !== null;
      default:
        return false;
    }
  };

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto"
          >
            {/* Header */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">Share Your Feedback</h2>
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X size={24} />
                </button>
              </div>
              <p className="mt-2 text-sm text-gray-600">
                Your feedback helps us improve the spiritual guidance experience
              </p>
            </div>

            {/* Content */}
            <div className="p-6">
              {submitted ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <ThumbsUp className="text-green-500" size={32} />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Thank You!</h3>
                  <p className="text-gray-600">
                    Your feedback has been received and will help us serve you better.
                  </p>
                </div>
              ) : (
                <>
                  {/* Feedback Type Selection */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      What would you like to share?
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {feedbackTypes.map(({ type, icon: Icon, label, color }) => (
                        <button
                          key={type}
                          onClick={() => setFeedbackType(type)}
                          className={`p-3 border rounded-lg text-left transition-colors ${
                            feedbackType === type
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <Icon className={`${color} mb-2`} size={20} />
                          <div className="text-sm font-medium text-gray-900">{label}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Rating Input */}
                  {feedbackType === 'rating' && (
                    <div className="mb-6">
                      <label className="block text-sm font-medium text-gray-700 mb-3">
                        How was your experience?
                      </label>
                      <div className="flex space-x-2">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <button
                            key={star}
                            onClick={() => setRating(star)}
                            onMouseEnter={() => setHoverRating(star)}
                            onMouseLeave={() => setHoverRating(0)}
                            className="p-1 transition-colors"
                          >
                            <Star
                              size={32}
                              className={`${
                                star <= (hoverRating || rating)
                                  ? 'text-yellow-400 fill-current'
                                  : 'text-gray-300'
                              } transition-colors`}
                            />
                          </button>
                        ))}
                      </div>
                      {rating > 0 && (
                        <p className="mt-2 text-sm text-gray-600">
                          {rating === 5 && "Excellent! We're glad we could help."}
                          {rating === 4 && "Great! Thank you for your positive feedback."}
                          {rating === 3 && "Good. We appreciate your feedback."}
                          {rating === 2 && "We'll work to improve your experience."}
                          {rating === 1 && "We're sorry. Please let us know how we can improve."}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Text Input */}
                  {(feedbackType === 'text_feedback' || feedbackType === 'feature_request' || 
                    feedbackType === 'bug_report' || feedbackType === 'spiritual_accuracy' || 
                    feedbackType === 'user_experience') && (
                    <div className="mb-6">
                      <label className="block text-sm font-medium text-gray-700 mb-3">
                        {feedbackType === 'feature_request' && 'What feature would you like to see?'}
                        {feedbackType === 'bug_report' && 'Please describe the issue you encountered'}
                        {feedbackType === 'spiritual_accuracy' && 'How can we improve spiritual accuracy?'}
                        {feedbackType === 'user_experience' && 'How was your overall experience?'}
                        {feedbackType === 'text_feedback' && 'Share your thoughts'}
                      </label>
                      <textarea
                        value={textFeedback}
                        onChange={(e) => setTextFeedback(e.target.value)}
                        placeholder="Your feedback helps us improve..."
                        rows={4}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  )}

                  {/* Voice Recording */}
                  {feedbackType === 'voice_feedback' && (
                    <div className="mb-6">
                      <label className="block text-sm font-medium text-gray-700 mb-3">
                        Record your voice feedback
                      </label>
                      <div className="text-center">
                        {!audioBlob ? (
                          <button
                            onClick={isRecording ? stopRecording : startRecording}
                            className={`w-24 h-24 rounded-full flex items-center justify-center transition-colors ${
                              isRecording
                                ? 'bg-red-500 hover:bg-red-600 text-white'
                                : 'bg-blue-500 hover:bg-blue-600 text-white'
                            }`}
                          >
                            {isRecording ? <MicOff size={32} /> : <Mic size={32} />}
                          </button>
                        ) : (
                          <div className="space-y-3">
                            <div className="text-green-600 text-sm">Recording saved!</div>
                            <button
                              onClick={() => setAudioBlob(null)}
                              className="text-blue-500 hover:text-blue-600 text-sm underline"
                            >
                              Record again
                            </button>
                          </div>
                        )}
                        <p className="mt-2 text-sm text-gray-600">
                          {isRecording ? 'Recording... Click to stop' : 'Click to start recording'}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Submit Button */}
                  <div className="flex space-x-3">
                    <button
                      onClick={onClose}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={submitFeedback}
                      disabled={!canSubmit() || isSubmitting}
                      className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
                    >
                      {isSubmitting ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <>
                          <Send size={16} className="mr-2" />
                          Submit Feedback
                        </>
                      )}
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FeedbackModal;
