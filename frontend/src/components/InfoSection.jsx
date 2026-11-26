import React from 'react';
import { Zap, Film, Music, ShieldCheck, Check } from 'lucide-react';

export default function InfoSection() {
  return (
    <section className="info-section">
      <div className="section-divider" />

      {/* How it Works */}
      <div className="info-block">
        <h2 className="info-heading">How to Download YouTube Videos & Audio</h2>
        <p className="info-subheading">
          Download any YouTube video or audio in high fidelity in three simple steps.
        </p>

        <div className="steps-grid">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3 className="step-title">Paste Video URL</h3>
            <p className="step-desc">
              Copy the YouTube link and paste it into the search box. The analyzer will automatically scan available streams.
            </p>
          </div>

          <div className="step-card">
            <div className="step-number">2</div>
            <h3 className="step-title">Select Quality & Format</h3>
            <p className="step-desc">
              Choose your preferred format: MP4 video up to 4K / 1080p, or high-bitrate MP3 / M4A audio.
            </p>
          </div>

          <div className="step-card">
            <div className="step-number">3</div>
            <h3 className="step-title">Download & Save</h3>
            <p className="step-desc">
              Click Download. The file converts in real time with live speed and progress, and saves directly to your device.
            </p>
          </div>
        </div>
      </div>

      {/* Features Overview */}
      <div className="info-block" style={{ marginTop: '2.5rem' }}>
        <h2 className="info-heading">Why Use DanfeDrop?</h2>
        <p className="info-subheading">
          A clean, privacy-focused media utility built without intrusive ads or arbitrary limits.
        </p>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <Zap size={20} color="var(--accent-blue)" />
            </div>
            <div>
              <h3 className="feature-title">Instant Auto-Analysis</h3>
              <p className="feature-desc">
                Simply paste your link and analysis starts automatically. No unnecessary delays or multi-step redirects.
              </p>
            </div>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <Film size={20} color="var(--accent-blue)" />
            </div>
            <div>
              <h3 className="feature-title">Full HD & 4K Resolutions</h3>
              <p className="feature-desc">
                Download crisp video in 2160p (4K), 1440p (2K), 1080p Full HD, and 720p HD with crystal clear audio merged seamlessly.
              </p>
            </div>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <Music size={20} color="var(--accent-blue)" />
            </div>
            <div>
              <h3 className="feature-title">Studio 320 kbps MP3</h3>
              <p className="feature-desc">
                Extract soundtrack audio with high-precision FFmpeg audio encoding at 320 kbps, 192 kbps, or original M4A streams.
              </p>
            </div>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <ShieldCheck size={20} color="var(--accent-blue)" />
            </div>
            <div>
              <h3 className="feature-title">Pure & Direct</h3>
              <p className="feature-desc">
                No invasive pop-ups, no registration required, and completely free for personal and educational use.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
