import React from 'react';

export default function Footer({ onOpenTerms }) {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-inner">
        <div>
          <div className="footer-brand">
            <span>DanfeDrop</span>
          </div>
          <p className="footer-copy" style={{ marginTop: '0.25rem' }}>
            High-fidelity video and audio converter powered by FFmpeg.
          </p>
        </div>

        <div className="footer-nav">
          <button type="button" className="footer-btn" onClick={onOpenTerms}>
            Terms of Use
          </button>
          <span className="footer-copy">© {currentYear} DanfeDrop. All rights reserved.</span>
        </div>
      </div>
    </footer>
  );
}
