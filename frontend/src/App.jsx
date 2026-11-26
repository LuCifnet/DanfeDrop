import React, { useState, useEffect, useCallback } from 'react';

// Components
import Header from './components/Header';
import UrlInput from './components/UrlInput';
import VideoInfoCard from './components/VideoInfoCard';
import FormatTabs from './components/FormatTabs';
import DownloadProgress from './components/DownloadProgress';
import AnalyzingSkeleton from './components/AnalyzingSkeleton';
import InfoSection from './components/InfoSection';
import TermsModal from './components/TermsModal';
import Alert from './components/Alert';
import Footer from './components/Footer';

// Services & Hooks
import { analyzeVideoUrl } from './services/api';
import { useDownloadProgress } from './hooks/useDownloadProgress';

export default function App() {
  const [url, setUrl] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [videoData, setVideoData] = useState(null);
  const [error, setError] = useState(null);
  const [isTermsOpen, setIsTermsOpen] = useState(false);

  // Theme Management - Default to LIGHT mode
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark' || saved === 'light') return saved;
    return 'light'; // Default to light mode
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleDownloadComplete = useCallback(() => {
    setUrl('');
    setVideoData(null);
    setError(null);
  }, []);

  const {
    downloadState,
    startDownload,
    cancelActiveDownload,
    dismissDownload,
    clearFinishedDownload,
    isDownloading,
  } = useDownloadProgress({ onComplete: handleDownloadComplete });


  const validateUrl = (testUrl) => {
    if (!testUrl || !testUrl.trim()) return false;
    const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|shorts\/|embed\/|v\/|live\/)|youtu\.be\/|music\.youtube\.com\/watch\?v=)[\w-]{11}/i;
    return pattern.test(testUrl.trim());
  };

  // Common analysis runner
  const triggerAnalysis = useCallback(async (targetUrl) => {
    const trimmed = (targetUrl || url).trim();
    if (!trimmed) {
      setError('Please paste a YouTube video URL.');
      return;
    }

    if (!validateUrl(trimmed)) {
      setError('Invalid YouTube link. Please check the URL and try again (e.g. https://www.youtube.com/watch?v=...)');
      return;
    }

    clearFinishedDownload();
    setError(null);
    setAnalyzing(true);
    setVideoData(null);

    try {
      const data = await analyzeVideoUrl(trimmed);
      setVideoData(data);
    } catch (err) {
      setError(err.message || 'Failed to analyze this video.');
    } finally {
      setAnalyzing(false);
    }
  }, [url, clearFinishedDownload]);

  // Form submit handler
  const handleAnalyzeSubmit = (e) => {
    if (e) e.preventDefault();
    triggerAnalysis(url);
  };

  // Instant auto-analyze on paste event
  const handleAutoAnalyze = (pastedUrl) => {
    if (validateUrl(pastedUrl)) {
      triggerAnalysis(pastedUrl);
    }
  };

  const handleClear = () => {
    setUrl('');
    setVideoData(null);
    setError(null);
  };

  const handleStartDownload = (item, type) => {
    startDownload(item, type, videoData, url);
    // Clear URL input and video info after initiating download
    setUrl('');
    setVideoData(null);
    setError(null);
  };

  return (
    <div>
      <Header 
        theme={theme} 
        onToggleTheme={toggleTheme} 
        onOpenTerms={() => setIsTermsOpen(true)} 
      />

      <main className="main-container">
        <section className="hero-section">
          <h1 className="hero-title">Download videos and audio from YouTube</h1>
          <p className="hero-subtitle">
            Paste a YouTube URL to automatically convert and download in your desired video or audio quality.
          </p>
        </section>

        <UrlInput
          url={url}
          setUrl={(val) => {
            setUrl(val);
            if (val.trim()) clearFinishedDownload();
            if (error) setError(null);
          }}
          onAnalyze={handleAnalyzeSubmit}
          onAutoAnalyze={handleAutoAnalyze}
          analyzing={analyzing}
          onClear={handleClear}
        />

        <Alert type="error" message={error} />

        {analyzing && <AnalyzingSkeleton />}

        <DownloadProgress
          downloadState={downloadState}
          onCancel={cancelActiveDownload}
          onDismiss={dismissDownload}
        />


        {videoData && (
          <div className="results-container">
            <VideoInfoCard videoData={videoData} />
            <FormatTabs
              key={videoData.id}
              videoFormats={videoData.video_formats}
              audioFormats={videoData.audio_formats}
              onDownload={handleStartDownload}
              isDownloading={isDownloading}
            />

          </div>
        )}

        {/* Informative Body Content (Y2Mate Style) */}
        <InfoSection />
      </main>

      <Footer onOpenTerms={() => setIsTermsOpen(true)} />

      <TermsModal 
        isOpen={isTermsOpen} 
        onClose={() => setIsTermsOpen(false)} 
      />
    </div>
  );
}
