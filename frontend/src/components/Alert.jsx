import React from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

export default function Alert({ type = 'error', message }) {
  if (!message) return null;

  const isError = type === 'error';

  return (
    <div className={`alert-box ${isError ? 'alert-error' : 'alert-success'}`} role="alert">
      {isError ? (
        <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
      ) : (
        <CheckCircle2 size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
      )}
      <div>
        <strong>{isError ? 'Error: ' : 'Success: '}</strong>
        {message}
      </div>
    </div>
  );
}
