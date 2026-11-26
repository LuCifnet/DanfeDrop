/**
 * API service for YouTube media downloader
 */

export async function fetchSystemConfig() {
  const res = await fetch('/api/config');
  return res.json();
}

export async function analyzeVideoUrl(url) {
  const response = await fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });

  const res = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.detail || 'Could not analyze video.');
  }
  return res.data;
}

export async function initiateDownload(payload) {
  const response = await fetch('/api/download', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const res = await response.json();
  if (!response.ok || !res.success) {
    throw new Error(res.detail || 'Could not start download.');
  }
  return res;
}

export async function cancelDownload(taskId) {
  const response = await fetch(`/api/cancel/${taskId}`, {
    method: 'POST',
  });
  return response.json();
}

export async function fetchTaskStatus(taskId) {
  const res = await fetch(`/api/status/${taskId}`);
  return res.json();
}

export async function fetchTermsOfService() {
  const res = await fetch('/api/terms');
  return res.json();
}


