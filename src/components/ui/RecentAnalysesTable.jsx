import React from 'react'
import EmptyState from './EmptyState'

/** Maps status values to pill class and display text. */
const STATUS_MAP = {
  completed:  { cls: 'status-pill--completed',  label: 'Completed' },
  processing: { cls: 'status-pill--processing', label: 'Processing' },
  failed:     { cls: 'status-pill--failed',      label: 'Failed' },
  draft:      { cls: 'status-pill--draft',       label: 'Draft' },
}

/** Maps recommendation labels to display class and text. */
const REC_MAP = {
  proceed: { cls: 'rec-label--proceed', text: '✓ Proceed' },
  caution: { cls: 'rec-label--caution', text: '⚠ Caution' },
  stop:    { cls: 'rec-label--stop',    text: '✗ Stop' },
  pending: { cls: 'rec-label--pending', text: '— Pending' },
}

/** Format an ISO date string to a readable local date. */
function formatDate(iso) {
  try {
    return new Date(iso).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  } catch {
    return iso
  }
}

/**
 * RecentAnalysesTable
 *
 * Props:
 *  analyses — array of analysis objects (see mockData.js for shape)
 */
export default function RecentAnalysesTable({ analyses = [] }) {
  if (analyses.length === 0) {
    return (
      <EmptyState
        title="No analyses yet"
        description="Start a new analysis to evaluate a business location. Your results will appear here."
        actionLabel="Start New Analysis"
        actionTo="/new-analysis"
      />
    )
  }

  return (
    <div className="table-scroll" role="region" aria-label="Recent analyses">
      <table className="data-table" aria-label="Recent analyses list">
        <thead>
          <tr>
            <th scope="col">Business</th>
            <th scope="col">Category</th>
            <th scope="col">Location</th>
            <th scope="col">Mode</th>
            <th scope="col">Status</th>
            <th scope="col">Recommendation</th>
            <th scope="col">Date</th>
          </tr>
        </thead>
        <tbody>
          {analyses.map((row) => {
            const status = STATUS_MAP[row.status] ?? { cls: 'status-pill--draft', label: row.status }
            const rec    = REC_MAP[row.recommendation_label] ?? { cls: 'rec-label--pending', text: row.recommendation_label }

            return (
              <tr key={row.analysis_id}>
                <td>
                  <strong style={{ fontSize: 13.5, fontWeight: 600 }}>
                    {row.business_name}
                  </strong>
                </td>
                <td>{row.category}</td>
                <td style={{ color: 'var(--muted)', maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {row.location_label}
                </td>
                <td>
                  <span style={{
                    fontSize: 11.5,
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                    color: row.mode === 'existing' ? 'var(--processing)' : 'var(--success)',
                    background: row.mode === 'existing' ? 'var(--processing-bg)' : 'var(--success-bg)',
                    borderRadius: 3,
                    padding: '3px 7px',
                  }}>
                    {row.mode === 'existing' ? 'Existing' : 'New'}
                  </span>
                </td>
                <td>
                  <span className={`status-pill ${status.cls}`}>
                    <span className="status-dot" aria-hidden="true" />
                    {status.label}
                  </span>
                </td>
                <td>
                  <span className={`rec-label ${rec.cls}`}>
                    {rec.text}
                  </span>
                </td>
                <td style={{ color: 'var(--muted)', whiteSpace: 'nowrap' }}>
                  {formatDate(row.created_at)}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
