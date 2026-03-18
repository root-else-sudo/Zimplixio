import { useEffect, useState, useRef } from 'react';
import { createPortal } from 'react-dom';
import type { Stage } from '../data/stages';
import { DualColumn } from './DualColumn';
import { Callout } from './Callout';
import { ComparisonTable } from './ComparisonTable';

interface StageModalProps {
  stage: Stage | null;
  onClose: () => void;
}

const STAGE_BADGE: Record<string, string> = {
  '0': 'Stage 0',
  '1': 'Stage 1',
  '2': 'Stage 2',
  '3': 'Stage 3',
  'P': 'Ongoing',
  'M': 'Ongoing',
};

export function StageModal({ stage, onClose }: StageModalProps) {
  const [mounted, setMounted] = useState(false);
  const [visible, setVisible] = useState(false);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (stage) {
      setMounted(true);
      requestAnimationFrame(() => setVisible(true));
    } else {
      setVisible(false);
      const t = setTimeout(() => setMounted(false), 300);
      return () => clearTimeout(t);
    }
  }, [stage]);

  // Focus close button when modal appears
  useEffect(() => {
    if (visible && closeRef.current) {
      closeRef.current.focus();
    }
  }, [visible]);

  // ESC key closes modal
  useEffect(() => {
    if (!mounted) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [mounted, onClose]);

  if (!mounted || !stage) return null;

  return createPortal(
    <div
      className={`modal-overlay${visible ? '' : ' hidden'}`}
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(17, 24, 39, 0.7)',
        backdropFilter: 'blur(4px)',
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem',
      }}
      onClick={onClose}
    >
      <div
        className={`modal-card${visible ? '' : ' hidden'}`}
        style={{
          maxWidth: '48rem',
          width: '100%',
          maxHeight: '90vh',
          overflowY: 'auto',
          borderRadius: '1.5rem',
          boxShadow: '0 25px 50px rgba(0, 0, 0, 0.3)',
        }}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        {/* Header */}
        <div
          style={{
            background: 'linear-gradient(135deg, #4338CA 0%, #3730A3 100%)',
            padding: '2rem',
            borderRadius: '1.5rem 1.5rem 0 0',
            position: 'relative',
          }}
        >
          <span
            style={{
              display: 'inline-block',
              padding: '0.25rem 0.75rem',
              background: 'rgba(255,255,255,0.2)',
              color: 'white',
              borderRadius: '9999px',
              fontSize: '0.75rem',
              fontWeight: 600,
              marginBottom: '0.75rem',
              fontFamily: 'DM Sans, sans-serif',
            }}
          >
            {STAGE_BADGE[stage.number]}
          </span>
          <h2
            id="modal-title"
            style={{
              fontFamily: 'DM Serif Display, serif',
              fontSize: 'clamp(1.5rem, 3vw, 2rem)',
              fontWeight: 400,
              color: 'white',
              marginBottom: '0.5rem',
              lineHeight: 1.2,
            }}
          >
            {stage.name}
          </h2>
          <p
            style={{
              fontStyle: 'italic',
              color: '#C7D2FE',
              fontSize: '1rem',
              fontFamily: 'DM Sans, sans-serif',
              margin: 0,
            }}
          >
            {stage.keyQuestion}
          </p>
          <button
            ref={closeRef}
            onClick={onClose}
            aria-label="Close"
            style={{
              position: 'absolute',
              top: '1rem',
              right: '1rem',
              width: 36,
              height: 36,
              borderRadius: '50%',
              background: 'rgba(255,255,255,0.15)',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: 18,
              transition: 'background 0.2s',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,0.3)')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,0.15)')}
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div
          className="modal-body"
          style={{
            padding: '2rem',
            borderRadius: '0 0 1.5rem 1.5rem',
          }}
        >
          <p className="modal-body-text" style={{ marginBottom: '1.5rem', lineHeight: 1.7, fontFamily: 'DM Sans, sans-serif' }}>
            {stage.intro}
          </p>
          <DualColumn left={stage.columns.left} right={stage.columns.right} />
          {stage.callouts.map((callout, i) => (
            <Callout key={i} callout={callout} />
          ))}
          {stage.tables?.map((table, i) => (
            <ComparisonTable key={i} table={table} />
          ))}
        </div>
      </div>
    </div>,
    document.body
  );
}
