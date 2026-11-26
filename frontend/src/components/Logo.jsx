import React from 'react';
import logoLight from '../assets/logo-lightmode.jpg';
import logoDark from '../assets/logo-darkmode.jpg';

export default function Logo({ theme }) {
  const activeTheme =
    theme ||
    (typeof document !== 'undefined'
      ? document.documentElement.getAttribute('data-theme')
      : 'light') ||
    'light';

  const isDark = activeTheme === 'dark';
  const logoSrc = isDark ? logoDark : logoLight;

  return (
    <div className="brand">
      <img
        src={logoSrc}
        alt="DanfeDrop Logo"
        className="brand-logo-img"
      />
      <span>DanfeDrop</span>
    </div>
  );
}
