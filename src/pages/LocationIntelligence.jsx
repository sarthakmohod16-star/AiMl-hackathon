import React, { useState, useMemo, useCallback } from 'react'
import StatCard from '@/components/ui/StatCard'
import EmptyState from '@/components/ui/EmptyState'
import {
  MOCK_SELECTED_LOCATION,
  MOCK_NEARBY_BUSINESSES,
  MOCK_LOCATION_SUMMARY,
  MOCK_SOURCES,
  MOCK_LIMITATIONS,
  COMPETITOR_CATEGORIES,
  DISTANCE_FILTERS,
} from '@/data/locationMockData'

/* ================================================================
   Inline SVG icons — no icon library needed
   ================================================================ */

const IconMapPin = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
    <circle cx="12" cy="10" r="3" />
  </svg>
)

const IconBuilding = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <rect x="4" y="2" width="16" height="20" rx="2" ry="2" />
    <path d="M9 22V12h6v10" />
    <path d="M8 6h.01M16 6h.01M12 6h.01M8 10h.01M16 10h.01M12 10h.01" />
  </svg>
)

const IconTarget = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <circle cx="12" cy="12" r="6" />
    <circle cx="12" cy="12" r="2" />
  </svg>
)

const IconGrid = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7" />
    <rect x="14" y="3" width="7" height="7" />
    <rect x="14" y="14" width="7" height="7" />
    <rect x="3" y="14" width="7" height="7" />
  </svg>
)

const IconList = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <line x1="8" y1="6" x2="21" y2="6" />
    <line x1="8" y1="12" x2="21" y2="12" />
    <line x1="8" y1="18" x2="21" y2="18" />
    <line x1="3" y1="6" x2="3.01" y2="6" />
    <line x1="3" y1="12" x2="3.01" y2="12" />
    <line x1="3" y1="18" x2="3.01" y2="18" />
  </svg>
)

const IconMap = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />
    <line x1="8" y1="2" x2="8" y2="18" />
    <line x1="16" y1="6" x2="16" y2="22" />
  </svg>
)


const IconInfo = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="16" x2="12" y2="12" />
    <line x1="12" y1="8" x2="12.01" y2="8" />
  </svg>
)

const IconWarn = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
    <line x1="12" y1="9" x2="12" y2="13" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
)

const IconLoader = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="2" x2="12" y2="6" />
    <line x1="12" y1="18" x2="12" y2="22" />
    <line x1="4.93" y1="4.93" x2="7.76" y2="7.76" />
    <line x1="16.24" y1="16.24" x2="19.07" y2="19.07" />
    <line x1="2" y1="12" x2="6" y2="12" />
    <line x1="18" y1="12" x2="22" y2="12" />
    <line x1="4.93" y1="19.07" x2="7.76" y2="16.24" />
    <line x1="16.24" y1="7.76" x2="19.07" y2="4.93" />
  </svg>
)

const IconAlertTriangle = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
    <line x1="12" y1="9" x2="12" y2="13" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
)

/* ================================================================
   Helpers
   ================================================================ */

function formatDistance(meters) {
  if (meters >= 1000) return `${(meters / 1000).toFixed(1)} km`
  return `${meters} m`
}

function formatRadius(meters) {
  if (meters >= 1000) return `${(meters / 1000).toFixed(1)} km`
  return `${meters} m`
}

function getCategoryLabel(value) {
  const found = COMPETITOR_CATEGORIES.find((c) => c.value === value)
  return found ? found.label : value
}

/* ================================================================
   Sub-components
   ================================================================ */

/* ---------- Demo banner ---------------------------------------- */
function DemoBanner() {
  return (
    <div className="demo-banner" role="status">
      <IconWarn />
      <span>
        <strong>Demo data</strong> — The competitors and metrics below are
        illustrative only. Connect a backend to display real location intelligence.
      </span>
    </div>
  )
}

/* ---------- Selected location card ----------------------------- */
function LocationCard({ location }) {
  return (
    <div className="card loc-location-card">
      <div className="card-header">
        <span style={{ fontWeight: 700, fontSize: 14.5 }}>Selected Location</span>
        <span
          className="status-pill status-pill--completed"
          style={{ fontSize: 11 }}
        >
          <span className="status-dot" />
          Active
        </span>
      </div>
      <div className="card-body loc-location-details">
        <div className="loc-location-row">
          <div className="loc-location-icon" aria-hidden="true">
            <IconMapPin />
          </div>
          <div>
            <span className="loc-location-label">Address</span>
            <span className="loc-location-value">{location.label}</span>
          </div>
        </div>
        <div className="loc-location-meta">
          <div className="loc-meta-item">
            <span className="loc-meta-label">Search Radius</span>
            <span className="loc-meta-value">
              {formatRadius(location.radius_meters)}
            </span>
          </div>
          <div className="loc-meta-item">
            <span className="loc-meta-label">Business</span>
            <span className="loc-meta-value">{location.business_name}</span>
          </div>
          <div className="loc-meta-item">
            <span className="loc-meta-label">Category</span>
            <span className="loc-meta-value">
              {getCategoryLabel(location.business_category)}
            </span>
          </div>
          <div className="loc-meta-item">
            <span className="loc-meta-label">Coordinates</span>
            <span className="loc-meta-value" style={{ fontFamily: 'monospace', fontSize: 12 }}>
              {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ---------- Filter controls ------------------------------------ */
function FilterBar({
  categoryFilter,
  setCategoryFilter,
  distanceFilter,
  setDistanceFilter,
  viewMode,
  setViewMode,
  resultCount,
}) {
  return (
    <div className="loc-filter-bar">
      <div className="loc-filter-controls">
        <div className="field" style={{ marginBottom: 0, minWidth: 180 }}>
          <label htmlFor="loc-cat-filter">Category</label>
          <select
            id="loc-cat-filter"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            {COMPETITOR_CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </div>
        <div className="field" style={{ marginBottom: 0, minWidth: 160 }}>
          <label htmlFor="loc-dist-filter">Max Distance</label>
          <select
            id="loc-dist-filter"
            value={distanceFilter}
            onChange={(e) => setDistanceFilter(Number(e.target.value))}
          >
            {DISTANCE_FILTERS.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
        </div>
        <div className="loc-filter-count">
          <span className="loc-filter-count-value">{resultCount}</span>{' '}
          competitor{resultCount !== 1 ? 's' : ''} found
        </div>
      </div>
      <div className="loc-view-toggle" role="tablist" aria-label="View mode">
        <button
          role="tab"
          aria-selected={viewMode === 'list'}
          className={`loc-view-btn${viewMode === 'list' ? ' loc-view-btn--active' : ''}`}
          onClick={() => setViewMode('list')}
          title="List view"
        >
          <IconList />
        </button>
        <button
          role="tab"
          aria-selected={viewMode === 'map'}
          className={`loc-view-btn${viewMode === 'map' ? ' loc-view-btn--active' : ''}`}
          onClick={() => setViewMode('map')}
          title="Map view"
        >
          <IconMap />
        </button>
      </div>
    </div>
  )
}

/* ---------- Competitor list (table) ----------------------------- */
function CompetitorTable({ businesses }) {
  if (businesses.length === 0) {
    return (
      <EmptyState
        title="No competitors found"
        description="Try adjusting your filters to see more results."
        icon={
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
        }
      />
    )
  }

  return (
    <div className="table-scroll">
      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Category</th>
            <th>Type</th>
            <th>Distance</th>
            <th>Address</th>
          </tr>
        </thead>
        <tbody>
          {businesses.map((biz) => (
            <tr key={biz.id}>
              <td style={{ fontWeight: 600 }}>{biz.name}</td>
              <td>{getCategoryLabel(biz.category)}</td>
              <td>
                <span
                  className={`status-pill ${
                    biz.competitor_type === 'direct'
                      ? 'status-pill--failed'
                      : 'status-pill--processing'
                  }`}
                >
                  <span className="status-dot" />
                  {biz.competitor_type === 'direct' ? 'Direct' : 'Indirect'}
                </span>
              </td>
              <td style={{ whiteSpace: 'nowrap' }}>
                {formatDistance(biz.distance_meters)}
              </td>
              <td style={{ color: 'var(--muted)', fontSize: 13 }}>
                {biz.address || '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/* ---------- Map placeholder ------------------------------------ */
function MapPlaceholder({ businesses, location }) {
  if (businesses.length === 0) {
    return (
      <EmptyState
        title="No competitors to map"
        description="Try adjusting your filters to see more results."
        icon={<IconMap />}
      />
    )
  }

  /* Simple CSS-based dot map — no map library required */
  const MAP_SIZE = 320
  const PADDING = 32

  /* Calculate relative positions based on lat/lng offsets */
  const allLats = [location.latitude, ...businesses.map((b) => b.latitude)]
  const allLngs = [location.longitude, ...businesses.map((b) => b.longitude)]
  const minLat = Math.min(...allLats)
  const maxLat = Math.max(...allLats)
  const minLng = Math.min(...allLngs)
  const maxLng = Math.max(...allLngs)
  const latRange = maxLat - minLat || 0.005
  const lngRange = maxLng - minLng || 0.005

  function toPixel(lat, lng) {
    const x = PADDING + ((lng - minLng) / lngRange) * (MAP_SIZE - 2 * PADDING)
    const y =
      MAP_SIZE -
      PADDING -
      ((lat - minLat) / latRange) * (MAP_SIZE - 2 * PADDING)
    return { x, y }
  }

  const centerPx = toPixel(location.latitude, location.longitude)

  return (
    <div className="loc-map-container">
      <div className="loc-map-visual" style={{ height: MAP_SIZE }}>
        <svg
          viewBox={`0 0 ${MAP_SIZE} ${MAP_SIZE}`}
          width="100%"
          height="100%"
          style={{ display: 'block' }}
          role="img"
          aria-label={`Map showing ${businesses.length} competitors around ${location.label}`}
        >
          {/* Radius ring */}
          <circle
            cx={centerPx.x}
            cy={centerPx.y}
            r={(MAP_SIZE - 2 * PADDING) / 2.2}
            fill="#bc8b6710"
            stroke="#bc8b67"
            strokeWidth="1.5"
            strokeDasharray="6 4"
          />

          {/* Competitor dots */}
          {businesses.map((biz) => {
            const pos = toPixel(biz.latitude, biz.longitude)
            const isDirect = biz.competitor_type === 'direct'
            return (
              <g key={biz.id}>
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="6"
                  fill={isDirect ? '#c45c5c' : '#3a5f8c'}
                  stroke="#fff"
                  strokeWidth="2"
                />
                <title>
                  {biz.name} ({isDirect ? 'Direct' : 'Indirect'}) —{' '}
                  {formatDistance(biz.distance_meters)}
                </title>
              </g>
            )
          })}

          {/* Center marker (user's location) */}
          <circle
            cx={centerPx.x}
            cy={centerPx.y}
            r="8"
            fill="#bc8b67"
            stroke="#fff"
            strokeWidth="2.5"
          />
          <circle
            cx={centerPx.x}
            cy={centerPx.y}
            r="3"
            fill="#fff"
          />
        </svg>
      </div>
      <div className="loc-map-legend">
        <span className="loc-legend-item">
          <span className="loc-legend-dot" style={{ background: '#bc8b67' }} />
          Your location
        </span>
        <span className="loc-legend-item">
          <span className="loc-legend-dot" style={{ background: '#c45c5c' }} />
          Direct competitor
        </span>
        <span className="loc-legend-item">
          <span className="loc-legend-dot" style={{ background: '#3a5f8c' }} />
          Indirect competitor
        </span>
      </div>
      <div className="info-notice info-notice--muted" style={{ marginTop: 12 }}>
        <IconInfo />
        <span style={{ fontSize: 12.5 }}>
          This is a simplified schematic view. Connect a map provider (e.g.
          Leaflet, Mapbox) for interactive mapping with real tile layers.
        </span>
      </div>
    </div>
  )
}

/* ---------- Market overview section ---------------------------- */
function MarketOverview({ summary }) {
  return (
    <div className="loc-market-overview">
      <h2 style={{ fontSize: 17, fontWeight: 700, letterSpacing: '-0.3px', marginBottom: 16 }}>
        Market Overview
      </h2>
      <div className="stat-grid loc-stat-grid">
        <StatCard
          label="Nearby Businesses"
          value={summary.nearby_business_count}
          sub="Within search radius"
          icon={<IconBuilding />}
          isDemo
        />
        <StatCard
          label="Direct Competitors"
          value={summary.direct_competitor_count}
          sub="Same category"
          icon={<IconTarget />}
          isDemo
        />
        <StatCard
          label="Indirect Competitors"
          value={summary.indirect_competitor_count}
          sub="Related categories"
          icon={<IconGrid />}
          isDemo
        />
        <StatCard
          label="Density"
          value={
            summary.density_per_square_km != null
              ? summary.density_per_square_km.toFixed(1)
              : '—'
          }
          sub="Businesses per km²"
          icon={<IconMapPin />}
          isDemo
        />
      </div>
    </div>
  )
}

/* ---------- Data source footer --------------------------------- */
function DataSourceFooter({ sources, limitations }) {
  return (
    <div className="loc-data-source">
      {sources.map((src, i) => (
        <div key={i} className="loc-source-row">
          <span className="loc-source-label">Source:</span>
          <span className="loc-source-value">{src.name}</span>
          <span className="loc-source-label" style={{ marginLeft: 16 }}>Retrieved:</span>
          <span className="loc-source-value">
            {new Date(src.retrieved_at).toLocaleString()}
          </span>
        </div>
      ))}
      {limitations.length > 0 && (
        <div className="info-notice" style={{ marginTop: 12 }}>
          <IconInfo />
          <div>
            <strong style={{ fontSize: 12 }}>Limitations</strong>
            <ul style={{ marginTop: 4, paddingLeft: 16, listStyle: 'disc' }}>
              {limitations.map((lim, i) => (
                <li key={i} style={{ fontSize: 12.5, color: 'var(--muted)', marginBottom: 2 }}>
                  {lim}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

/* ---------- Loading skeleton ----------------------------------- */
function LoadingSkeleton() {
  return (
    <div className="loc-loading" role="status" aria-label="Loading location intelligence">
      <div className="loc-loading-icon">
        <IconLoader />
      </div>
      <h3 style={{ fontSize: 17, fontWeight: 700 }}>Analyzing location…</h3>
      <p style={{ fontSize: 14, color: 'var(--muted)' }}>
        Scanning for nearby businesses and calculating market metrics.
      </p>
      {/* Skeleton cards */}
      <div className="stat-grid" style={{ width: '100%', marginTop: 20 }}>
        {[1, 2, 3, 4].map((n) => (
          <div key={n} className="stat-card" style={{ minHeight: 100 }}>
            <div className="loc-skeleton loc-skeleton--sm" />
            <div className="loc-skeleton loc-skeleton--lg" />
            <div className="loc-skeleton loc-skeleton--sm" />
          </div>
        ))}
      </div>
    </div>
  )
}

/* ---------- Error state ---------------------------------------- */
function ErrorState({ onRetry }) {
  return (
    <div className="empty-state" role="alert">
      <div className="empty-state-icon" style={{ background: 'var(--error-bg)' }}>
        <IconAlertTriangle />
      </div>
      <h3>Unable to load location data</h3>
      <p>
        The location intelligence service is currently unavailable. This may be
        because no backend is connected yet.
      </p>
      <button
        className="button button-outline"
        style={{ marginTop: 8 }}
        onClick={onRetry}
      >
        Try again
      </button>
    </div>
  )
}

/* ================================================================
   Main page component
   ================================================================ */

export default function LocationIntelligence() {
  /* --- View state ------------------------------------------------ */
  const [viewState, setViewState] = useState('loaded') // 'loading' | 'loaded' | 'error'
  const [categoryFilter, setCategoryFilter] = useState('')
  const [distanceFilter, setDistanceFilter] = useState(0)
  const [viewMode, setViewMode] = useState('list')

  /* --- Simulated state toggles for demo -------------------------- */
  const cycleState = useCallback(() => {
    setViewState((prev) => {
      if (prev === 'loaded') return 'loading'
      if (prev === 'loading') return 'error'
      return 'loaded'
    })
  }, [])

  /* --- Filtered businesses --------------------------------------- */
  const filtered = useMemo(() => {
    return MOCK_NEARBY_BUSINESSES.filter((biz) => {
      if (categoryFilter && biz.category !== categoryFilter) return false
      if (distanceFilter > 0 && biz.distance_meters >= distanceFilter) return false
      return true
    })
  }, [categoryFilter, distanceFilter])

  /* --- Render ---------------------------------------------------- */
  if (viewState === 'loading') {
    return (
      <div className="page-content">
        <div className="dashboard-welcome">
          <h1>Location Intelligence</h1>
          <p>Explore the competitive landscape around your selected location.</p>
        </div>
        <LoadingSkeleton />
      </div>
    )
  }

  if (viewState === 'error') {
    return (
      <div className="page-content">
        <div className="dashboard-welcome">
          <h1>Location Intelligence</h1>
          <p>Explore the competitive landscape around your selected location.</p>
        </div>
        <ErrorState onRetry={() => setViewState('loaded')} />
      </div>
    )
  }

  return (
    <div className="page-content">
      {/* --- Page heading ---------------------------------------- */}
      <div className="dashboard-welcome">
        <h1>Location Intelligence</h1>
        <p>
          Explore the competitive landscape around your selected location.
          Discover nearby businesses, classify competitors, and review market
          density metrics.
        </p>
      </div>

      <DemoBanner />

      {/* --- Selected location ----------------------------------- */}
      <LocationCard location={MOCK_SELECTED_LOCATION} />

      {/* --- Market overview stats ------------------------------- */}
      <MarketOverview summary={MOCK_LOCATION_SUMMARY} />

      {/* --- Competitor section ---------------------------------- */}
      <div className="loc-competitors-section">
        <h2 style={{ fontSize: 17, fontWeight: 700, letterSpacing: '-0.3px', marginBottom: 4 }}>
          Nearby Competitors
        </h2>
        <p style={{ fontSize: 13.5, color: 'var(--muted)', marginBottom: 16 }}>
          Businesses within {formatRadius(MOCK_SELECTED_LOCATION.radius_meters)} of
          your location, sorted by distance.
        </p>

        <FilterBar
          categoryFilter={categoryFilter}
          setCategoryFilter={setCategoryFilter}
          distanceFilter={distanceFilter}
          setDistanceFilter={setDistanceFilter}
          viewMode={viewMode}
          setViewMode={setViewMode}
          resultCount={filtered.length}
        />

        <div className="card" style={{ marginTop: 16 }}>
          <div className="card-body" style={{ padding: viewMode === 'map' ? 0 : undefined }}>
            {viewMode === 'list' ? (
              <CompetitorTable businesses={filtered} />
            ) : (
              <MapPlaceholder businesses={filtered} location={MOCK_SELECTED_LOCATION} />
            )}
          </div>
        </div>
      </div>

      {/* --- Data source ----------------------------------------- */}
      <DataSourceFooter sources={MOCK_SOURCES} limitations={MOCK_LIMITATIONS} />

      {/* --- Dev utility: state toggler -------------------------- */}
      <div style={{ marginTop: 32, paddingTop: 20, borderTop: '1px dashed var(--line)' }}>
        <button
          className="button button-small button-outline"
          onClick={cycleState}
          style={{ fontSize: 12 }}
        >
          Toggle state (loaded → loading → error) — dev only
        </button>
      </div>
    </div>
  )
}
