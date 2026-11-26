import React from 'react';
import { User, Eye } from 'lucide-react';

export default function VideoInfoCard({ videoData }) {
  if (!videoData) return null;

  return (
    <div className="video-card">
      <div className="thumbnail-wrapper">
        <img 
          src={videoData.thumbnail} 
          alt={videoData.title} 
          className="video-thumb"
          loading="lazy"
          onError={(e) => {
            e.target.src = `https://i.ytimg.com/vi/${videoData.id}/hqdefault.jpg`;
          }}
        />
        <span className="duration-badge">{videoData.duration_formatted}</span>
      </div>
      <div className="video-details">
        <div>
          <h2 className="video-title" title={videoData.title}>{videoData.title}</h2>
          <div className="video-meta-row">
            <span className="video-meta-item">
              <User size={14} />
              <span>{videoData.uploader}</span>
            </span>
            {videoData.view_count_formatted && (
              <>
                <span className="meta-divider">•</span>
                <span className="video-meta-item">
                  <Eye size={14} />
                  <span>{videoData.view_count_formatted}</span>
                </span>
              </>
            )}
            {videoData.upload_date_formatted && (
              <>
                <span className="meta-divider">•</span>
                <span className="video-meta-item">
                  <span>{videoData.upload_date_formatted}</span>
                </span>
              </>
            )}
          </div>
        </div>

        <div>
          <span className="video-platform-tag">YouTube</span>
        </div>
      </div>
    </div>
  );
}
