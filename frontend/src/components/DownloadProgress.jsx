import React from 'react';
import { CheckCircle2, ArrowDownToLine, FolderCheck } from 'lucide-react';

export default function DownloadProgress({ 
  downloadState, 
  onCancel, 
  onDismiss, 
  onSaveFile 
}) {
  if (!downloadState) return null;

  const {
    taskId,
    targetLabel,
    status,
    progress,
    downloaded,
    total,
    speed,
    eta,
    filename,
    savedDir,
    error,
  } = downloadState;

  const isDownloading = ['downloading', 'queued', 'processing'].includes(status);
  const isCompleted = status === 'completed';
  const isCancelled = status === 'cancelled';
  const isError = status === 'error';

  return (
    <div className="download-card">
      <div className="download-header">
        <div className="download-title-area">
          <span className={`download-status-badge ${status}`}>
            {status === 'downloading' ? 'Downloading...' :
             status === 'processing' ? 'Processing...' :
             status === 'completed' ? 'Completed' :
             status === 'cancelled' ? 'Cancelled' : 'Failed'}
          </span>
          <span className="download-target-label">{targetLabel}</span>
        </div>
        <div>
          {isDownloading && (
            <button 
              type="button" 
              className="btn-danger-outline" 
              onClick={onCancel}
            >
              Cancel
            </button>
          )}
          {(isCompleted || isCancelled || isError) && (
            <button 
              type="button" 
              className="btn-secondary" 
              onClick={onDismiss}
            >
              Dismiss
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="progress-container">
        <div 
          className={`progress-fill ${isCompleted ? 'completed' : ''}`}
          style={{ width: `${Math.max(progress || 0, isCompleted ? 100 : 2)}%` }}
        />
      </div>

      {/* Real-time stats */}
      <div className="progress-stats-grid">
        <div className="progress-stat">
          <span>Progress:</span>
          <strong>{Math.round(progress || 0)}%</strong>
          {downloaded && (
            <span>({downloaded} / {total || '—'})</span>
          )}
        </div>
        <div className="progress-stat">
          <span>Speed:</span>
          <strong>{speed || '—'}</strong>
        </div>
        <div className="progress-stat">
          <span>Remaining:</span>
          <strong>{eta || '—'}</strong>
        </div>
      </div>

      {/* Target Directory indicator & Success */}
      {isCompleted && (
        <div className="progress-actions" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#059669', fontSize: '0.875rem' }}>
            <CheckCircle2 size={18} />
            <span>Saved to <strong>{savedDir || 'C:\\Users\\Kapil\\Music\\newmusic'}</strong></span>
          </div>
          <button
            type="button"
            className="btn-primary"
            onClick={onDismiss}
            style={{ padding: '0.45rem 1.25rem' }}
          >
            Done
          </button>
        </div>
      )}


      {/* Error state */}
      {isError && (
        <div style={{ marginTop: '0.875rem', color: '#b91c1c', fontSize: '0.8125rem' }}>
          Download failed: {error || 'An unexpected error occurred.'}
        </div>
      )}
    </div>
  );
}
