import React, { useEffect, useState } from 'react';
import { X, ShieldCheck } from 'lucide-react';
import { fetchTermsOfService } from '../services/api';

export default function TermsModal({ isOpen, onClose }) {
  const [termsData, setTermsData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && !termsData) {
      setLoading(true);
      fetchTermsOfService()
        .then((res) => {
          if (res && res.success && res.data) {
            setTermsData(res.data);
          }
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [isOpen, termsData]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldCheck size={20} color="var(--accent-blue)" />
            <h2 className="modal-title">{termsData?.title || 'Terms of Use'}</h2>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            title="Close"
          >
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <div className="spinner-sm" />
              <p style={{ marginTop: '0.5rem' }}>Loading Terms of Use...</p>
            </div>
          ) : termsData ? (
            <div>
              <p style={{ marginBottom: '1.25rem', fontStyle: 'italic' }}>
                {termsData.summary}
              </p>
              {termsData.sections?.map((sec) => (
                <div key={sec.id} className="terms-section">
                  <h3 className="terms-section-title">{sec.title}</h3>
                  <p>{sec.content}</p>
                </div>
              ))}
            </div>
          ) : (
            <p>Unable to load terms at this moment.</p>
          )}
        </div>

        <div className="modal-footer">
          <button type="button" className="btn-primary" onClick={onClose}>
            Got it
          </button>
        </div>
      </div>
    </div>
  );
}
