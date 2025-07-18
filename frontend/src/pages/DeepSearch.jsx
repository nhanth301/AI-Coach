import React, { useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { OptimizeIcon, RouteIcon, SearchIcon, DbaseIcon, ProcessIcon, SaveIcon, CheckIcon, DefaultIcon } from '../components/Icons';
import ResultCard from '../components/ResultCard';

const MESSAGE_TO_ICON_MAP = {
  "✍️ Optimizing query...": <OptimizeIcon />,
  "🧭 Analyzing and routing for external search...": <RouteIcon />,
  "🔎 Searching internal knowledge base...": <DbaseIcon />,
  "⚖️ Grading document relevance...": <CheckIcon />,
  "🌐 Searching the web...": <SearchIcon />,
  "🔬 Searching ArXiv...": <SearchIcon />,
  "📄 Processing and summarizing web results...": <ProcessIcon />,
  "📚 Processing and summarizing scientific documents...": <ProcessIcon />,
  "💾 Saving new information to database...": <SaveIcon />,
  "✅ Preparing final answer...": <CheckIcon />,
};

export default function DeepSearch() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [statusMessages, setStatusMessages] = useState([]);
  const [passages, setPassages] = useState([]);
  const [selectedPassage, setSelectedPassage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const socketRef = useRef(null);

  const handleSearch = (e) => {
    e.preventDefault();
    if (!query || isLoading) return;

    setIsLoading(true);
    setError('');
    setStatusMessages([]);
    setPassages([]);
    setSelectedPassage(null);

    socketRef.current = new WebSocket('ws://localhost:8000/ws');

    socketRef.current.onopen = () => socketRef.current.send(query);
    socketRef.current.onclose = () => setIsLoading(false);
    socketRef.current.onerror = () => setError("Connection failed. Please ensure the backend is running.");

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'step') {
        setStatusMessages(prev => [...prev, data.message]);
      } else if (data.type === 'result') {
        const resultData = data.data;
        const finalPassages = resultData?.final.final_results || [];
        if (finalPassages.length > 0) {
          setPassages(finalPassages);
        } else {
          setError("The process finished, but no relevant content was found or generated.");
        }
        socketRef.current.close();
      } else if (data.type === 'error') {
        setError(`An error occurred: ${data.message}`);
        socketRef.current.close();
      }
    };
  };
  
  const getIconForStep = (message) => MESSAGE_TO_ICON_MAP[message] || <DefaultIcon />;

  const handleStartPractice = () => {
    if (selectedPassage) {
      navigate('/practice', { state: { passage: selectedPassage } });
    }
  };

  return (
    <div className="container">
      <header>
        <h1>AI-Coach: Sharpen Your Writing with Translation</h1>
        <p className="subtitle">
          What shall we explore and practice together today? 
          {/* <Link to="/practice" style={{color: 'var(--primary-color)', marginLeft: '1rem', fontWeight: 500}}>Go to Translation Practice</Link> */}
        </p>
        <form className="input-group" onSubmit={handleSearch}>
          <input name="query" id="query-input" placeholder="Initiate query..." value={query} onChange={(e) => setQuery(e.target.value)} disabled={isLoading} />
          <button id="search-button" type="submit" disabled={isLoading}>{isLoading ? 'Synthesizing...' : 'Execute'}</button>
        </form>
      </header>
      
      <div className="main-layout">
        <aside className="sidebar">
          <div className="execution-container">
            <h3>Execution Log</h3>
            <ul id="status-list">
              {statusMessages.map((msg, index) => {
                const isCurrent = isLoading && (index === statusMessages.length - 1);
                return (
                  <li key={index} className={isCurrent ? 'active' : 'done'}>
                    <span className="status-icon">{getIconForStep(msg)}</span>
                    <span className="status-text">{msg.substring(msg.indexOf(' ') + 1)}</span>
                    {isCurrent && <div className="pulse-indicator"></div>}
                  </li>
                );
              })}
            </ul>
            {isLoading && statusMessages.length === 0 && (
              <div className="loader-container">
                  <div className="loader"></div>
                  <span>Awaiting response...</span>
              </div>
            )}
          </div>
        </aside>

        <main className="main-content">
          <div className="results-area">
            {error && <p className="error-message">{error}</p>}
            {passages.length > 0 && !isLoading && (
              <>
                <h3>Synthesized Insights</h3>
                <div id="selection-area">
                  {passages.map((text, index) => (
                    <ResultCard
                      key={index}
                      index={index}
                      text={text}
                      isSelected={selectedPassage === text}
                      onClick={() => setSelectedPassage(text)}
                    />
                  ))}
                </div>
              </>
            )}
          </div>
        </main>
      </div>

      {selectedPassage && !isLoading && (
        <div className="practice-controls">
          <button className="start-practice-btn" onClick={handleStartPractice}>
            Start Translation Practice 
          </button>
        </div>
      )}
    </div>
  );
}