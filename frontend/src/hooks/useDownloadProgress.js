import { useState, useRef, useEffect, useCallback } from 'react';
import { initiateDownload, cancelDownload, fetchTaskStatus } from '../services/api';

export function useDownloadProgress({ onComplete } = {}) {
  const [downloadState, setDownloadState] = useState(null);
  const eventSourceRef = useRef(null);
  const autoDismissTimerRef = useRef(null);

  // Close active SSE and timers on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (autoDismissTimerRef.current) {
        clearTimeout(autoDismissTimerRef.current);
      }
    };
  }, []);



  const startDownload = useCallback(async (item, type, videoData, rawUrl) => {
    if (downloadState && ['downloading', 'queued', 'processing'].includes(downloadState.status)) {
      alert('A download is already in progress. Please wait or cancel the current task.');
      return;
    }

    const targetLabel = type === 'video'
      ? `${item.quality} • ${item.format}`
      : `${item.quality} (${item.bitrate}) • ${item.format}`;

    setDownloadState({
      taskId: null,
      targetLabel,
      type,
      status: 'queued',
      progress: 0,
      downloaded: '0 B',
      total: item.filesize_formatted !== '—' ? item.filesize_formatted : 'Calculating...',
      speed: 'Connecting...',
      eta: 'Preparing...',
      filename: null,
      savedDir: '',
      error: null,
    });

    try {
      const payload = {
        url: videoData.webpage_url || rawUrl,
        type,
        format_id: item.format_id || null,
        height: item.height || null,
        ext: item.ext || (type === 'video' ? 'mp4' : 'mp3'),
        bitrate: item.bitrate_val || null,
        title: videoData.title || 'media',
        quality: item.quality,
      };

      const res = await initiateDownload(payload);
      const taskId = res.task_id;
      const savedDir = res.saved_dir || '';

      setDownloadState(prev => ({ ...prev, taskId, savedDir, status: 'downloading' }));

      // Setup Server-Sent Events
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      const es = new EventSource(`/api/progress/${taskId}`);
      eventSourceRef.current = es;

      es.onmessage = (event) => {
        try {
          const update = JSON.parse(event.data);
          if (update.error && update.status !== 'cancelled') {
            setDownloadState(prev => ({
              ...prev,
              status: 'error',
              error: update.error,
            }));
            es.close();
            return;
          }

          setDownloadState(prev => ({
            ...prev,
            status: update.status,
            progress: update.progress,
            downloaded: update.downloaded_formatted,
            total: update.total_formatted,
            speed: update.speed_formatted,
            eta: update.eta_formatted,
            filename: update.filename,
            savedDir: update.saved_dir || prev.savedDir,
            error: update.error,
          }));

          if (update.status === 'completed') {
            es.close();
            // Show 100% completed status briefly, then automatically dismiss and clear all
            if (autoDismissTimerRef.current) clearTimeout(autoDismissTimerRef.current);
            autoDismissTimerRef.current = setTimeout(() => {
              setDownloadState(null);
              onComplete?.();
              autoDismissTimerRef.current = null;
            }, 1500);
          } else if (['error', 'cancelled'].includes(update.status)) {
            es.close();
          }

        } catch {
          // ignore parsing error
        }
      };

      es.onerror = async () => {
        es.close();
        try {
          const res = await fetchTaskStatus(taskId);
          if (res.success && res.data) {
            const t = res.data;
            setDownloadState(prev => ({
              ...prev,
              status: t.status,
              progress: t.progress,
              downloaded: t.downloaded_formatted,
              total: t.total_formatted,
              speed: t.speed_formatted,
              eta: t.eta_formatted,
              filename: t.filename,
              savedDir: t.saved_dir,
              error: t.error,
            }));

            if (t.status === 'completed') {
              if (autoDismissTimerRef.current) clearTimeout(autoDismissTimerRef.current);
              autoDismissTimerRef.current = setTimeout(() => {
                setDownloadState(null);
                onComplete?.();
                autoDismissTimerRef.current = null;
              }, 1500);
            }
          }
        } catch {
          // ignore
        }
      };

    } catch (err) {
      setDownloadState(prev => ({
        ...prev,
        status: 'error',
        error: err.message || 'Could not start download.',
      }));
    }
  }, [downloadState, onComplete]);

  const cancelActiveDownload = useCallback(async () => {
    if (autoDismissTimerRef.current) {
      clearTimeout(autoDismissTimerRef.current);
      autoDismissTimerRef.current = null;
    }
    if (!downloadState || !downloadState.taskId) return;
    try {
      await cancelDownload(downloadState.taskId);
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      setDownloadState(prev => ({
        ...prev,
        status: 'cancelled',
        error: 'Download cancelled by user.',
      }));
    } catch {
      // ignore
    }
  }, [downloadState]);

  const dismissDownload = useCallback(() => {
    if (autoDismissTimerRef.current) {
      clearTimeout(autoDismissTimerRef.current);
      autoDismissTimerRef.current = null;
    }
    setDownloadState(null);
    onComplete?.();
  }, [onComplete]);

  const isDownloading = downloadState && ['downloading', 'queued', 'processing'].includes(downloadState.status);

  return {
    downloadState,
    startDownload,
    cancelActiveDownload,
    dismissDownload,
    isDownloading,
  };
}


