import React from 'react'

const IconCheck = () => (
  <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 8l3.5 3.5L13 5" />
  </svg>
)

/**
 * PlaceholderPage — shown for pages not yet implemented.
 *
 * Props:
 *  title       — page heading (string)
 *  description — what this page will do (string)
 *  phase       — planned phase label, e.g. "Phase 3" (string)
 *  features    — array of { label, desc } objects (upcoming features)
 */
export default function PlaceholderPage({ title, description, phase = 'Phase 3', features = [] }) {
  return (
    <div className="placeholder-page">
      <span className="placeholder-badge">
        <span aria-hidden="true">🚧</span>
        Coming in {phase}
      </span>

      <h1 style={{ fontSize: 'clamp(22px, 3vw, 30px)', fontWeight: 700, letterSpacing: '-0.6px' }}>
        {title}
      </h1>

      {description && (
        <p className="placeholder-desc">{description}</p>
      )}

      {features.length > 0 && (
        <>
          <p style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--muted)', marginTop: 8 }}>
            Planned features
          </p>
          <ul className="placeholder-features">
            {features.map((f, i) => (
              <li key={i} className="placeholder-feature">
                <span aria-hidden="true">
                  <IconCheck />
                </span>
                <span>
                  <span className="placeholder-feature-label">{f.label}</span>
                  {f.desc && <span className="placeholder-feature-desc">{f.desc}</span>}
                </span>
              </li>
            ))}
          </ul>
        </>
      )}

      <p style={{ fontSize: 12.5, color: 'var(--muted)', marginTop: 8 }}>
        This page is reserved and will be implemented in the next development phase.
        Navigate using the sidebar to explore what is already available.
      </p>
    </div>
  )
}
