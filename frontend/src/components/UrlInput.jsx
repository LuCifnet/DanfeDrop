import React from 'react';
import { X, ArrowRight } from 'lucide-react';

export default function UrlInput({ 
  url, 
  setUrl, 
  onAnalyze, 
  onAutoAnalyze,
  analyzing, 
  onClear 
}) {
  const handlePasteEvent = (e) => {
    const text = e.clipboardData.getData('text');
    if (text) {
      const trimmed = text.trim();
      setUrl(trimmed);
      if (onAutoAnalyze) {
        onAutoAnalyze(trimmed);
      }
    }
  };

  return (
    <div className="search-card">
      <form className="search-form" onSubmit={onAnalyze}>
        <div className="input-wrapper">
          <input
            type="text"
            className="search-input"
            placeholder="Paste YouTube link here (e.g. https://www.youtube.com/watch?v=...)"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onPaste={handlePasteEvent}
            disabled={analyzing}
            autoFocus
          />
          {url && (
            <button
              type="button"
              className="input-clear-btn"
              onClick={onClear}
              title="Clear URL"
            >
              <X size={16} />
            </button>
          )}
        </div>
        <button
          type="submit"
          className="btn-primary"
          disabled={analyzing || !url.trim()}
          title="Convert video"
        >
          {analyzing ? (
            <>
              <span className="spinner-sm" />
              <span>Converting...</span>
            </>
          ) : (
            <>
              <span>Convert</span>
              <ArrowRight size={16} />
            </>
          )}
        </button>
      </form>
    </div>
  );
}
