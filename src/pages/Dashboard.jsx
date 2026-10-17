import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import StatCard from '@/components/ui/StatCard'
import RecentAnalysesTable from '@/components/ui/RecentAnalysesTable'
import { MOCK_SUMMARY, MOCK_RECENT_ANALYSES, MOCK_EMPTY_ANALYSES } from '@/data/mockData'

/* ── Icons ─────────────────────────────────────────────────── */
const IconAnalysis = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="3" width="16" height="14" rx="2" />
    <path d="M6 10l3 3 5-6" />
  </svg>
)

const IconCompleted = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="10" cy="10" r="8" />
    <path d="M6.5 10.5l2.5 2.5 5-5" />
  </svg>
)

const IconReport = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 2h7l4 4v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1z" />
    <path d="M12 2v5h5M7 10h6M7 13h4" />
  </svg>
)

const IconArrow = () => (
  <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 8h10M9 4l4 4-4 4" />
  </svg>
)

const IconInfo = () => (
  <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="8" cy="8" r="6.5" />
    <path d="M8 7v4M8 5.5v.5" />
  </svg>
)

/* ── Dashboard ─────────────────────────────────────────────── */
export default function Dashboard() {
  // Toggle between populated demo data and empty state for testing
  const [showEmpty, setShowEmpty] = useState(false)
  const analyses = showEmpty ? MOCK_EMPTY_ANALYSES : MOCK_RECENT_ANALYSES
  const summary  = showEmpty
    ? { total_analyses: 0, completed_analyses: 0, processing_analyses: 0, failed_analyses: 0, saved_reports: 0 }
    : MOCK_SUMMARY

  return (
    <>
      {/* Welcome */}
      <div className="dashboard-welcome">
        <h1>
          Good morning, <span className="serif-accent">welcome back.</span>
        </h1>
        <p>
          Review your recent analyses or start a new business feasibility assessment.
        </p>
      </div>

      {/* Demo data notice */}
      <div className="demo-banner" role="note">
        <IconInfo />
        <span>
          <strong>Demo data</strong> — The figures below are illustrative only and do not represent
          real business intelligence. Connect the backend in Phase 3 to see live data.
        </span>
      </div>

      {/* Stat cards */}
      <div className="stat-grid" aria-label="Summary statistics">
        <StatCard
          label="Total Analyses"
          value={summary.total_analyses}
          sub="All time"
          icon={<IconAnalysis />}
          isDemo
        />
        <StatCard
          label="Completed"
          value={summary.completed_analyses}
          sub="Results ready"
          icon={<IconCompleted />}
          isDemo
        />
        <StatCard
          label="In Progress"
          value={summary.processing_analyses}
          sub="Running now"
          icon={<IconAnalysis />}
          isDemo
        />
        <StatCard
          label="Saved Reports"
          value={summary.saved_reports}
          sub="Exportable"
          icon={<IconReport />}
          isDemo
        />
      </div>

      {/* Primary CTA row */}
      <div className="dashboard-cta-row">
        <h2>Recent Analyses</h2>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Empty-state toggle — dev convenience, remove in production */}
          <button
            type="button"
            className="button button-outline button-small"
            onClick={() => setShowEmpty((v) => !v)}
            title="Toggle empty state for testing"
            aria-label={showEmpty ? 'Show demo analyses' : 'Show empty state'}
            style={{ fontSize: 12 }}
          >
            {showEmpty ? 'Show demo data' : 'Test empty state'}
          </button>
          <Link to="/history" className="button button-outline button-small">
            View all
            <span aria-hidden="true" style={{ marginLeft: 6 }}><IconArrow /></span>
          </Link>
          <Link to="/new-analysis" className="button button-dark">
            Start New Analysis
            <span aria-hidden="true" style={{ marginLeft: 8 }}><IconArrow /></span>
          </Link>
        </div>
      </div>

      {/* Recent analyses table */}
      <div className="analyses-card">
        <div className="analyses-card-header">
          <span className="analyses-card-title">
            {showEmpty ? 'No analyses found' : `${analyses.length} most recent`}
          </span>
          {!showEmpty && (
            <span style={{ fontSize: 12, color: 'var(--muted)' }}>
              Demo data — not real results
            </span>
          )}
        </div>
        <RecentAnalysesTable analyses={analyses} />
      </div>

      {/* Quick-action shortcuts */}
      <div style={{ marginTop: 8 }}>
        <p style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--muted)', marginBottom: 14 }}>
          Quick access
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 12 }}>
          {[
            { to: '/location-intelligence', label: 'Location Intelligence', desc: 'Explore nearby competitors' },
            { to: '/financial-analysis',    label: 'Financial Analysis',    desc: 'Run projections & Monte Carlo' },
            { to: '/history',               label: 'Analysis History',       desc: 'Browse saved analyses' },
            { to: '/reports',               label: 'Reports',               desc: 'Export and download reports' },
          ].map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className="card"
              style={{
                display: 'block',
                padding: '16px 18px',
                textDecoration: 'none',
                transition: 'border-color 0.2s, transform 0.15s',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--copper)' }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = '' }}
            >
              <span style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--ink)', display: 'block', marginBottom: 4 }}>
                {item.label}
              </span>
              <span style={{ fontSize: 12, color: 'var(--muted)', lineHeight: 1.5 }}>
                {item.desc}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </>
  )
}
