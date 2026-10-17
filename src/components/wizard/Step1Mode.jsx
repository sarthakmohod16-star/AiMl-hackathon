import React from 'react'

const IconBuilding = () => (
  <svg viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <rect x="4" y="8" width="24" height="20" rx="2" />
    <path d="M4 12h24M12 8V4M20 8V4M10 16h3M19 16h3M10 21h3M19 21h3" />
  </svg>
)

const IconSeedling = () => (
  <svg viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M16 28V14" />
    <path d="M16 14C16 14 8 12 6 6c6 0 10 4 10 8z" />
    <path d="M16 18c0 0 8-2 10-8-6 0-10 4-10 8z" />
  </svg>
)

/**
 * Step1Mode — Business type selection card.
 * Users choose between "Existing Business" and "New Business".
 */
export default function Step1Mode({ fields, errors, touched, setField }) {
  const err = touched.mode && errors.mode

  return (
    <div className="wizard-step-content">
      <div className="wizard-step-heading">
        <span className="eyebrow" style={{ color: 'var(--copper)' }}>Step 1 of your analysis</span>
        <h2 className="wizard-step-title">What type of business are you assessing?</h2>
        <p className="wizard-step-desc">
          Choose whether you're evaluating an existing business you already run, or planning a brand-new venture.
        </p>
      </div>

      <div className="mode-cards" role="radiogroup" aria-label="Business type" aria-required="true">
        {/* Existing Business */}
        <button
          type="button"
          role="radio"
          aria-checked={fields.mode === 'existing'}
          className={`mode-card${fields.mode === 'existing' ? ' mode-card--selected' : ''}`}
          onClick={() => setField('mode', 'existing')}
        >
          <span className="mode-card-icon" aria-hidden="true">
            <IconBuilding />
          </span>
          <span className="mode-card-title">Existing Business</span>
          <span className="mode-card-desc">
            You already operate this business and have historical data — revenue, expenses, and customer records — to inform the analysis.
          </span>
          <ul className="mode-card-bullets">
            <li>Uses your real financial records</li>
            <li>Higher-confidence projections</li>
            <li>Identifies expansion opportunities</li>
          </ul>
          <span className="mode-card-check" aria-hidden="true">
            {fields.mode === 'existing' ? '✓' : ''}
          </span>
        </button>

        {/* New Business */}
        <button
          type="button"
          role="radio"
          aria-checked={fields.mode === 'new'}
          className={`mode-card${fields.mode === 'new' ? ' mode-card--selected' : ''}`}
          onClick={() => setField('mode', 'new')}
        >
          <span className="mode-card-icon" aria-hidden="true">
            <IconSeedling />
          </span>
          <span className="mode-card-title">New Business</span>
          <span className="mode-card-desc">
            You're starting a new venture and don't have historical data. The analysis will use your assumptions and comparable market data.
          </span>
          <ul className="mode-card-bullets">
            <li>Based on your financial assumptions</li>
            <li>Comparable business benchmarks</li>
            <li>Location demand estimates</li>
          </ul>
          <span className="mode-card-check" aria-hidden="true">
            {fields.mode === 'new' ? '✓' : ''}
          </span>
        </button>
      </div>

      {err && (
        <p className="field-error-msg" role="alert" style={{ marginTop: 12 }}>{err}</p>
      )}
    </div>
  )
}
