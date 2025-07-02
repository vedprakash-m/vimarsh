import React, { useState } from 'react';
import { ArrowRight } from 'lucide-react';
import ConversationInterface from './ConversationInterface';

const LandingPage: React.FC = () => {
  const [showInterface, setShowInterface] = useState(false);

  if (showInterface) {
    return <ConversationInterface onBack={() => setShowInterface(false)} />;
  }

  return (
    <div className="landing-page">
      {/* Minimal Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          {/* Sacred Symbol */}
          <div className="sacred-symbol">
            🕉
          </div>
          
          {/* Main Title */}
          <h1 className="main-title">
            Vimarsh
          </h1>
          
          {/* Subtitle */}
          <p className="subtitle">
            Seek wisdom from Lord Krishna's eternal teachings
          </p>
          
          {/* Sacred Quote */}
          <div className="sacred-quote">
            <p className="sanskrit">
              "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत"
            </p>
            <p className="translation">
              Whenever dharma declines, O Bharata...
            </p>
          </div>
          
          {/* Single Clear CTA */}
          <button 
            className="primary-cta"
            onClick={() => setShowInterface(true)}
          >
            Begin Your Spiritual Journey
            <ArrowRight size={20} />
          </button>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
