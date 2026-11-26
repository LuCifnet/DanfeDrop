import React, { useState } from 'react';
import { Film, Music } from 'lucide-react';
import FormatTable from './FormatTable';

export default function FormatTabs({ 
  videoFormats, 
  audioFormats, 
  onDownload, 
  isDownloading 
}) {
  const [activeTab, setActiveTab] = useState('audio');

  return (
    <div className="formats-card">
      <div className="tabs-header">
        <button
          type="button"
          className={`tab-btn ${activeTab === 'audio' ? 'active' : ''}`}
          onClick={() => setActiveTab('audio')}
        >
          <Music size={16} />
          <span>Audio</span>
          <span className="tab-badge">{audioFormats?.length || 0}</span>
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === 'video' ? 'active' : ''}`}
          onClick={() => setActiveTab('video')}
        >
          <Film size={16} />
          <span>Video</span>
          <span className="tab-badge">{videoFormats?.length || 0}</span>
        </button>
      </div>

      {activeTab === 'audio' ? (
        <FormatTable 
          type="audio" 
          items={audioFormats} 
          onDownload={onDownload} 
          isDownloading={isDownloading} 
        />
      ) : (
        <FormatTable 
          type="video" 
          items={videoFormats} 
          onDownload={onDownload} 
          isDownloading={isDownloading} 
        />
      )}
    </div>
  );
}

