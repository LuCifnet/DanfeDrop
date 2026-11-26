import React from 'react';
import { Download } from 'lucide-react';

export default function FormatTable({ 
  type, 
  items, 
  onDownload, 
  isDownloading 
}) {
  if (!items || items.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--text-secondary)' }}>
        No {type} streams available for this URL.
      </div>
    );
  }

  const isVideo = type === 'video';

  return (
    <div className="format-table-wrapper">
      <table className="format-table">
        <thead>
          <tr>
            <th>Quality</th>
            <th>Format</th>
            <th>{isVideo ? 'Audio' : 'Bitrate'}</th>
            <th>Est. Size</th>
            <th style={{ textAlign: 'right' }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>
                <div className="quality-cell">
                  <span>{item.quality}</span>
                  {isVideo && item.height >= 720 && (
                    <span className="quality-badge badge-hd">HD</span>
                  )}
                </div>
              </td>
              <td>
                <span className="format-tag">{item.format}</span>
              </td>
              <td>
                {isVideo ? (
                  <span className="audio-tag audio-included">
                    {item.audio_note || 'Included'}
                  </span>
                ) : (
                  <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>
                    {item.bitrate}
                  </span>
                )}
              </td>
              <td>
                <span style={{ color: 'var(--text-secondary)' }}>
                  {item.filesize_formatted}
                </span>
              </td>
              <td className="table-action-cell">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => onDownload(item, type)}
                  disabled={isDownloading}
                  title={`Download ${item.quality} (${item.format})`}
                >
                  <Download size={14} />
                  <span>Download</span>
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
