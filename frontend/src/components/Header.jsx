import React from 'react';
import { Sun, Moon } from 'lucide-react';
import Logo from './Logo';

export default function Header({ theme, onToggleTheme, onOpenTerms }) {
  return (
    <header className="app-header">
      <div className="header-container">
        <Logo theme={theme} />

        <div className="header-actions">
          <button
            type="button"
            className="header-nav-link"
            onClick={onOpenTerms}
          >
            Terms of Use
          </button>

          <button
            type="button"
            className="theme-toggle-btn"
            onClick={onToggleTheme}
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
          </button>
        </div>
      </div>
    </header>
  );
}
