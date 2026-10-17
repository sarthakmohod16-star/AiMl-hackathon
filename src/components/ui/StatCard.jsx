import React from 'react'

/**
 * StatCard — reusable dashboard metric tile.
 *
 * Props:
 *  label   — short metric name (string)
 *  value   — formatted display value (string | number)
 *  sub     — optional subtitle / context note (string)
 *  icon    — optional React element (inline SVG)
 *  isDemo  — if true, adds a "(demo)" marker for transparency
 */
export default function StatCard({ label, value, sub, icon, isDemo = false }) {
  return (
    <div className="stat-card" role="region" aria-label={label}>
      {icon && (
        <div className="stat-card-icon" aria-hidden="true">
          {icon}
        </div>
      )}
      <span className="stat-card-label">
        {label}
        {isDemo && (
          <span
            style={{ fontWeight: 400, opacity: 0.6, marginLeft: 5 }}
            aria-label="demo value"
          >
            (demo)
          </span>
        )}
      </span>
      <span className="stat-card-value">{value}</span>
      {sub && <span className="stat-card-sub">{sub}</span>}
    </div>
  )
}
