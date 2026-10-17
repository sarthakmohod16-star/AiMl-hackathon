import React from 'react'
import { Link } from 'react-router-dom'

/** Lookup helpers */
const MODE_LABELS = { existing: 'Existing Business', new: 'New Business' }
const CURRENCY_SYMBOLS = { INR: '₹', USD: '$', GBP: '£', SGD: 'S$', AED: 'د.إ', AUD: 'A$' }

function fmt(val, symbol) {
  const n = Number(val)
  if (!val || isNaN(n)) return '—'
  return `${symbol}${n.toLocaleString('en-IN')}`
}

function ReviewRow({ label, value }) {
  return (
    <div className="review-row">
      <span className="review-label">{label}</span>
      <span className="review-value">{value || <em style={{ color: 'var(--muted)' }}>Not provided</em>}</span>
    </div>
  )
}

function ReviewSection({ title, onEdit: _onEdit, stepIdx, onGoToStep, children }) {
  return (
    <div className="review-section">
      <div className="review-section-header">
        <h3 className="review-section-title">{title}</h3>
        <button
          type="button"
          className="button button-outline button-small"
          onClick={() => onGoToStep(stepIdx)}
          aria-label={`Edit ${title}`}
        >
          Edit
        </button>
      </div>
      <div className="review-rows">{children}</div>
    </div>
  )
}

/**
 * StepReview — Final review step.
 * Shows all collected information with edit-back links and a submit CTA.
 *
 * Props:
 *  fields     — full form state
 *  onGoToStep — callback to navigate back to a specific step
 *  onSubmit   — called when the user confirms the review
 */
export default function StepReview({ fields, onGoToStep, onSubmit }) {
  const isExisting = fields.mode === 'existing'
  const symbol = CURRENCY_SYMBOLS[fields.currency] || fields.currency

  // Category label lookup
  const catLabel = fields.category
    ? fields.category.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    : ''
  const indLabel = fields.industry
    ? fields.industry.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    : ''

  return (
    <div className="wizard-step-content">
      <div className="wizard-step-heading">
        <span className="eyebrow" style={{ color: 'var(--copper)' }}>Review your details</span>
        <h2 className="wizard-step-title">Everything look right?</h2>
        <p className="wizard-step-desc">
          Check your inputs below. Click <strong>Edit</strong> on any section to go back and make changes.
          When you're ready, click <strong>Finish &amp; Review</strong>.
        </p>
      </div>

      {/* Mode */}
      <ReviewSection title="Business Type" onGoToStep={onGoToStep} stepIdx={0}>
        <ReviewRow label="Mode" value={MODE_LABELS[fields.mode]} />
      </ReviewSection>

      {/* Profile */}
      <ReviewSection title="Business Profile" onGoToStep={onGoToStep} stepIdx={1}>
        <ReviewRow label="Business Name" value={fields.business_name} />
        <ReviewRow label="Category" value={catLabel} />
        <ReviewRow label="Industry" value={indLabel} />
        {fields.description && (
          <ReviewRow label="Description" value={fields.description} />
        )}
      </ReviewSection>

      {/* Location */}
      <ReviewSection title="Location" onGoToStep={onGoToStep} stepIdx={2}>
        <ReviewRow label="Country" value={fields.country} />
        <ReviewRow label="City" value={fields.city} />
        <ReviewRow label="Address / Area" value={fields.address} />
        <ReviewRow label="Search Radius" value={`${fields.radius_meters >= 1000 ? `${fields.radius_meters / 1000} km` : `${fields.radius_meters} m`}`} />
      </ReviewSection>

      {/* Historical data — existing mode only */}
      {isExisting && (
        <ReviewSection title="Historical Records" onGoToStep={onGoToStep} stepIdx={3}>
          <ReviewRow label="Currency" value={`${fields.currency} (${symbol})`} />
          <ReviewRow label="Annual Revenue" value={fmt(fields.annual_revenue, symbol)} />
          <ReviewRow label="Annual Expenses" value={fmt(fields.annual_expenses, symbol)} />
          {fields.avg_monthly_customers && (
            <ReviewRow label="Avg Monthly Customers" value={Number(fields.avg_monthly_customers).toLocaleString('en-IN')} />
          )}
          {fields.years_in_operation && (
            <ReviewRow label="Years in Operation" value={fields.years_in_operation} />
          )}
          {fields.historical_notes && (
            <ReviewRow label="Notes" value={fields.historical_notes} />
          )}
        </ReviewSection>
      )}

      {/* New business assumption notice */}
      {!isExisting && (
        <div className="info-notice" role="note" style={{ marginBottom: 20 }}>
          <span style={{ fontSize: 18 }} aria-hidden="true">📊</span>
          <div>
            <strong>Analysis approach for new businesses</strong>
            <p style={{ fontSize: 13, color: 'var(--muted)', marginTop: 2, lineHeight: 1.6 }}>
              Since no historical records are available, BizTwin will use your financial assumptions (collected in the next phase)
              alongside comparable business benchmarks and local market demand estimates. Results will be clearly
              labelled as estimates, not actuals.
            </p>
          </div>
        </div>
      )}

      {/* What happens next */}
      <div className="info-notice info-notice--success" role="note">
        <span style={{ fontSize: 18 }} aria-hidden="true">🚀</span>
        <div>
          <strong>What happens next?</strong>
          <p style={{ fontSize: 13, color: 'var(--muted)', marginTop: 2, lineHeight: 1.6 }}>
            After you confirm, BizTwin will proceed to collect financial assumptions and projection settings.
            The full AI analysis — including competitor mapping, demand estimation, and financial forecasts —
            will run once the backend is connected in Phase 3.
          </p>
        </div>
      </div>

      {/* Confirm CTA — also triggered by the WizardShell footer button */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 8 }}>
        <button
          type="button"
          className="button button-dark"
          onClick={onSubmit}
        >
          Confirm & Continue to Financial Setup →
        </button>
        <Link to="/" className="button button-outline">
          Save and exit
        </Link>
      </div>
    </div>
  )
}
