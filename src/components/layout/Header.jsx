import React from 'react'

const IconMenu = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round">
    <path d="M3 5h14M3 10h14M3 15h14" />
  </svg>
)

const IconBell = () => (
  <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10 2a6 6 0 0 1 6 6c0 3.5 1.5 5 1.5 5h-15S4 11.5 4 8a6 6 0 0 1 6-6z" />
    <path d="M8.5 17a1.5 1.5 0 0 0 3 0" />
  </svg>
)

const IconChevronRight = () => (
  <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 4l4 4-4 4" />
  </svg>
)

/**
 * App header.
 * Shows the current page title (and optional breadcrumb trail),
 * a sidebar toggle for mobile, a notifications button, and a user pill.
 */
export default function Header({ title, breadcrumb = [], onToggleSidebar }) {
  return (
    <header className="app-header" role="banner">
      <div className="header-left">
        {/* Mobile hamburger */}
        <button
          className="sidebar-toggle"
          onClick={onToggleSidebar}
          aria-label="Open navigation menu"
          aria-controls="main-sidebar"
          aria-expanded="false"
          type="button"
        >
          <IconMenu />
        </button>

        {/* Breadcrumb / page title */}
        {breadcrumb.length > 0 ? (
          <nav aria-label="Breadcrumb" className="breadcrumb">
            {breadcrumb.map((crumb, idx) => (
              <React.Fragment key={idx}>
                <span>{crumb}</span>
                <span className="breadcrumb-sep" aria-hidden="true">
                  <IconChevronRight />
                </span>
              </React.Fragment>
            ))}
            <span className="breadcrumb-current" aria-current="page">
              {title}
            </span>
          </nav>
        ) : (
          <span className="page-title">{title}</span>
        )}
      </div>

      <div className="header-right">
        {/* Notifications */}
        <button
          className="header-action-btn"
          aria-label="Notifications"
          type="button"
        >
          <IconBell />
        </button>

        {/* User pill */}
        <button
          className="header-user"
          aria-label="Account menu"
          type="button"
        >
          <span className="header-avatar" aria-hidden="true">A</span>
          <span className="header-user-label">Account</span>
        </button>
      </div>
    </header>
  )
}
