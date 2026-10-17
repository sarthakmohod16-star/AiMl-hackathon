import React from 'react'
import PlaceholderPage from '@/components/ui/PlaceholderPage'

export default function AnalysisHistory() {
  return (
    <PlaceholderPage
      title="Analysis History"
      description="Browse, search, and revisit all your saved business feasibility analyses. Rerun analyses with updated assumptions or export them as reports."
      phase="Phase 3"
      features={[
        { label: 'Search and filter', desc: 'By name, category, or status' },
        { label: 'Sortable list', desc: 'Date, location, or recommendation' },
        { label: 'Rerun analysis', desc: 'Update inputs and recalculate' },
        { label: 'Delete or archive', desc: 'Manage your saved records' },
        { label: 'Status tracking', desc: 'Completed, processing, failed' },
        { label: 'Export to report', desc: 'One-click PDF generation' },
      ]}
    />
  )
}
