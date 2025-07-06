import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';

export default function TranslationPractice() {
  const location = useLocation();
  
  // Get the passage from the router state, with a fallback message
  const [passage, setPassage] = useState(
    location.state?.passage || "No passage selected. Please go back to the search page to select one."
  );
  
  const [sentences, setSentences] = useState([]);
  const [currentSentenceIndex, setCurrentSentenceIndex] = useState(0);
  const [userTranslation, setUserTranslation] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sentenceScores, setSentenceScores] = useState({});

  // Split the passage into sentences when the component loads
  useEffect(() => {
    const splitSentences = passage.match(/[^.!?]+[.!?]+/g) || [];
    setSentences(splitSentences);
    setCurrentSentenceIndex(0);
    setUserTranslation('');
    setFeedback(null);
    setSentenceScores({});
  }, [passage]);

  // Send the translation to the API to be graded
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userTranslation || isLoading) return;
    
    setIsLoading(true);
    setFeedback(null);
    
    const payload = {
      original_passage: passage,
      current_sentence: sentences[currentSentenceIndex],
      user_translation: userTranslation,
    };

    try {
      const response = await fetch('http://localhost:8000/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error('Network response was not ok');
      const result = await response.json();
      
      setFeedback(result.feedback_data);
      // Save the score for the current sentence
      setSentenceScores(prevScores => ({
        ...prevScores,
        [currentSentenceIndex]: result.feedback_data.score
      }));

    } catch (error) {
      console.error('Failed to fetch feedback:', error);
      alert('Error getting feedback from the server.');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Navigate between sentences
  const handleNavigation = (direction) => {
    const newIndex = currentSentenceIndex + direction;
    if (newIndex >= 0 && newIndex < sentences.length) {
      setCurrentSentenceIndex(newIndex);
      setUserTranslation('');
      setFeedback(null);
    }
  };

  // Get the CSS class based on the score
  const getScoreClass = (score) => {
    if (score === undefined) return '';
    if (score >= 85) return 'score-good';
    if (score >= 50) return 'score-ok';
    return 'score-bad';
  };

  return (
    <div className="container">
      <header>
        <h1>AI Writing Coach</h1>
        <p className="subtitle">
            Practice translating from Vietnamese to English. 
            {/* <Link to="/">Back to Deep Search</Link> */}
        </p>
      </header>
      
      <div className="practice-view-container">
        <main className="left-pane">
          <h3>Original Passage</h3>
          <div className="vietnamese-passage-box">
            <p className="passage-content">
              {sentences.map((sentence, index) => {
                const isCurrent = index === currentSentenceIndex;
                const scoreClass = getScoreClass(sentenceScores[index]);
                
                return (
                  <span 
                    key={index} 
                    className={`sentence ${isCurrent ? 'current-sentence-highlight' : ''} ${scoreClass}`}
                  >
                    {sentence}
                  </span>
                );
              })}
            </p>
          </div>
          <hr/>
          
          {sentences[currentSentenceIndex] && (
            <form onSubmit={handleSubmit}>
              <label htmlFor="translation-input" className="current-sentence-label">
                <span className="sentence-counter">Translate Sentence {currentSentenceIndex + 1}/{sentences.length}</span>
                <span className="sentence-text">"{sentences[currentSentenceIndex]}"</span>
              </label>
              <textarea
                id="translation-input"
                className="translation-input"
                value={userTranslation}
                onChange={(e) => setUserTranslation(e.target.value)}
                placeholder="Type your English translation here..."
              />
              <div className="action-buttons">
                <div className="nav-buttons">
                    <button type="button" className="btn btn-secondary" onClick={() => handleNavigation(-1)} disabled={currentSentenceIndex === 0}>Previous</button>
                    <button type="button" className="btn btn-secondary" onClick={() => handleNavigation(1)} disabled={currentSentenceIndex === sentences.length - 1}>Next</button>
                </div>
                <button type="submit" className="btn btn-primary" disabled={isLoading || !userTranslation}>
                  {isLoading ? 'Checking...' : 'Check'}
                </button>
              </div>
            </form>
          )}
        </main>

        <aside className="right-pane">
          <h3>AI Feedback</h3>
          <div className="ai-feedback-card">
            <div className="feedback-content">
              {isLoading && <div className="loader-container" style={{justifyContent: 'center'}}><div className="loader"></div><span>AI Coach is analyzing...</span></div>}
              {feedback ? (
                <>
                  <div className="score-display">
                    <div className="score-circle" style={{'--score': feedback.score}}><div className="score-text">{feedback.score}</div></div>
                    <strong>Overall Score: {feedback.score}/100</strong>
                  </div>
                  <dl className="feedback-list">
                    <div className="feedback-item"><dt>Grammar:</dt><dd>{feedback.categorized_feedback.grammar}</dd></div>
                    <div className="feedback-item"><dt>Vocabulary:</dt><dd>{feedback.categorized_feedback.vocabulary}</dd></div>
                    <div className="feedback-item"><dt>Nuance & Style:</dt><dd>{feedback.categorized_feedback.nuance}</dd></div>
                    <div className="feedback-item suggestion"><dt>Suggestions:</dt><dd>
                      {feedback.suggestions.map((s, i) => <p key={i}>{s}</p>)}
                    </dd></div>
                  </dl>
                </>
              ) : (
                !isLoading && <p style={{textAlign: 'center', color: 'var(--text-tertiary)'}}>Submit your translation to get AI feedback.</p>
              )}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}