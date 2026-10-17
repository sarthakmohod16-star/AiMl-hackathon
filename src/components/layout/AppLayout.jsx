import React, { useState, useCallback } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

/** Maps route paths to human-readable page titles and breadcrumb trails. */
const PAGE_META = {
  '/': { title: 'Dashboard', breadcrumb: [] },
  '/new-analysis': { title: 'New Analysis', breadcrumb: ['Dashboard'] },
  '/location-intelligence': { title: 'Location Intelligence', breadcrumb: ['Dashboard'] },
  '/financial-analysis': { title: 'Financial Analysis', breadcrumb: ['Dashboard'] },
  '/history': { title: 'Analysis History', breadcrumb: ['Dashboard'] },
  '/reports': { title: 'Reports', breadcrumb: ['Dashboard'] },
  '/settings': { title: 'Settings', breadcrumb: ['Dashboard'] },
}

export default function AppLayout() {
  const { pathname } = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const meta = PAGE_META[pathname] ?? { title: 'BizTwin', breadcrumb: [] }

  const openSidebar = useCallback(() => setSidebarOpen(true), [])
  const closeSidebar = useCallback(() => setSidebarOpen(false), [])

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Skip to content</a>

      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          role="presentation"
          onClick={closeSidebar}
          aria-hidden="true"
        />
      )}

      {/* Right column: header + content */}
      <div className="app-main">
        <Header
          title={meta.title}
          breadcrumb={meta.breadcrumb}
          onToggleSidebar={openSidebar}
        />

        <main id="main-content" className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
