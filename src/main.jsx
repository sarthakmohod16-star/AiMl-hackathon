import React from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider, createBrowserRouter } from 'react-router-dom'

import '@/styles/base.css'
import '@/styles/app.css'

import AppLayout from '@/components/layout/AppLayout'
import Dashboard from '@/pages/Dashboard'
import NewAnalysis from '@/pages/NewAnalysis'
import LocationIntelligence from '@/pages/LocationIntelligence'
import FinancialAnalysis from '@/pages/FinancialAnalysis'
import AnalysisHistory from '@/pages/AnalysisHistory'
import Reports from '@/pages/Reports'
import Settings from '@/pages/Settings'

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'new-analysis', element: <NewAnalysis /> },
      { path: 'location-intelligence', element: <LocationIntelligence /> },
      { path: 'financial-analysis', element: <FinancialAnalysis /> },
      { path: 'history', element: <AnalysisHistory /> },
      { path: 'reports', element: <Reports /> },
      { path: 'settings', element: <Settings /> },
    ],
  },
])

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
