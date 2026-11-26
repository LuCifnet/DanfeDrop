import React from 'react';

export default function AnalyzingSkeleton() {
  return (
    <div className="analyzing-box">
      <div className="spinner" />
      <h3 className="analyzing-title">Analyzing video and checking available formats...</h3>
      <p className="analyzing-desc">Querying stream manifests, available resolutions, and audio codecs.</p>
    </div>
  );
}
