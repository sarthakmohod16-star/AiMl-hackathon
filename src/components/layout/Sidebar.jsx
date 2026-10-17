import React, { useEffect } from 'react'
import { NavLink, useLocation } from 'react-router-dom'

/* ── Icons (inline SVG, no icon library dependency) ───────── */
const IconDashboard = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="2" width="7" height="7" rx="1" />
    <rect x="11" y="2" width="7" height="7" rx="1" />
    <rect x="2" y="11" width="7" height="7" rx="1" />
    <rect x="11" y="11" width="7" height="7" rx="1" />
  </svg>
)

const IconPlus = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
    <circle cx="10" cy="10" r="8" />
    <path d="M10 6v8M6 10h8" />
  </svg>
)

const IconMap = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 5l6-2 4 2 6-2v12l-6 2-4-2-6 2V5z" />
    <path d="M8 3v12M12 5v12" />
  </svg>
)

const IconChart = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 15l4-5 4 3 5-7" />
    <path d="M2 17h16" />
  </svg>
)

const IconHistory = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16z" />
    <path d="M10 6v4l3 2" />
  </svg>
)

const IconReport = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 2h7l4 4v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1z" />
    <path d="M12 2v5h5M7 10h6M7 13h4" />
  </svg>
)

const IconSettings = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="10" cy="10" r="2.5" />
    <path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.22 4.22l1.42 1.42M14.36 14.36l1.42 1.42M4.22 15.78l1.42-1.42M14.36 5.64l1.42-1.42" />
  </svg>
)

const BizTwinLogo = () => (
  <svg viewBox="0 0 32 36" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <path
      d="M4 34V16a12 12 0 0 1 24 0v18h-7V16a5 5 0 0 0-10 0v18Z"
      fill="#bc8b67"
    />
  </svg>
)

/* ── Nav items config ─────────────────────────────────────── */
const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: IconDashboard, end: true },
  { to: '/new-analysis', label: 'New Analysis', icon: IconPlus },
]

const ANALYSIS_ITEMS = [
  { to: '/location-intelligence', label: 'Location Intelligence', icon: IconMap },
  { to: '/financial-analysis', label: 'Financial Analysis', icon: IconChart },
]

const RECORDS_ITEMS = [
  { to: '/history', label: 'Analysis History', icon: IconHistory },
  { to: '/reports', label: 'Reports', icon: IconReport },
]

const SYSTEM_ITEMS = [
  { to: '/settings', label: 'Settings', icon: IconSettings },
]

function NavItem({ to, label, icon: Icon, end }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
      aria-current={undefined} /* NavLink handles via className */
    >
      <span className="nav-link-icon" aria-hidden="true">
        <Icon />
      </span>
      {label}
    </NavLink>
  )
}

/* ── Sidebar ─────────────────────────────────────────────── */
export default function Sidebar({ isOpen, onClose }) {
  const location = useLocation()

  // Close sidebar on navigation (mobile)
  useEffect(() => {
    onClose()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname])

  // Close sidebar on Escape
  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === 'Escape' && isOpen) onClose()
    }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [isOpen, onClose])

  return (
    <aside
      className={`sidebar${isOpen ? ' sidebar--open' : ''}`}
      aria-label="Main navigation"
      id="main-sidebar"
    >
      {/* Brand */}
      <NavLink to="/" className="sidebar-brand" aria-label="BizTwin home">
        <span className="sidebar-brand-icon">
          <BizTwinLogo />
        </span>
        <span>
          <span className="sidebar-brand-name">BizTwin</span>
          <span className="sidebar-brand-tagline">Location Intelligence</span>
        </span>
      </NavLink>

      {/* Navigation */}
      <nav className="sidebar-nav" aria-label="Primary navigation">

        <span className="sidebar-section-label">Main</span>
        {NAV_ITEMS.map((item) => (
          <NavItem key={item.to} {...item} />
        ))}

        <span className="sidebar-section-label">Analysis</span>
        {ANALYSIS_ITEMS.map((item) => (
          <NavItem key={item.to} {...item} />
        ))}

        <span className="sidebar-section-label">Records</span>
        {RECORDS_ITEMS.map((item) => (
          <NavItem key={item.to} {...item} />
        ))}

        <span className="sidebar-section-label">System</span>
        {SYSTEM_ITEMS.map((item) => (
          <NavItem key={item.to} {...item} />
        ))}
      </nav>

      {/* Footer: user area */}
      <div className="sidebar-footer">
        <div className="sidebar-footer-user">
          <div className="sidebar-avatar" aria-hidden="true">A</div>
          <div className="sidebar-user-info">
            <span className="sidebar-user-name">Account</span>
            <span className="sidebar-user-role">Business Owner</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
