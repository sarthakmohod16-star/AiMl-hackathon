import React from 'react'
import { Link } from 'react-router-dom'

const IconInbox = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 12h-6l-2 3H10L8 12H2" />
    <path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 17.5 4h-11a2 2 0 0 0-1.89 1.11z" />
  </svg>
)

/**
 * EmptyState — displayed when a list or section has no data.
 *
 * Props:
 *  title       — primary heading (string)
 *  description — supporting text (string)
 *  actionLabel — optional CTA button label (string)
 *  actionTo    — React Router path for the CTA (string)
 *  icon        — optional custom icon element
 */
export default function EmptyState({ title, description, actionLabel, actionTo, icon }) {
  return (
    <div className="empty-state" role="status">
      <div className="empty-state-icon" aria-hidden="true">
        {icon ?? <IconInbox />}
      </div>
      <h3>{title}</h3>
      {description && <p>{description}</p>}
      {actionLabel && actionTo && (
        <Link to={actionTo} className="button button-dark" style={{ marginTop: 8 }}>
          {actionLabel}
        </Link>
      )}
    </div>
  )
}
