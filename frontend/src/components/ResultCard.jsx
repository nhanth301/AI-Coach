import React from 'react';

function ResultCard({ text, index, isSelected, onClick }) {
  return (
    <div
      className={`result-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="card-header">
        <h3>Paragraph #{index + 1}</h3>
      </div>
      <div className="card-body">
        <p>{text}</p>
      </div>
    </div>
  );
}

export default ResultCard;