import React from 'react'
import PlaceholderPage from '@/components/ui/PlaceholderPage'

export default function Reports() {
  return (
    <PlaceholderPage
      title="Reports"
      description="Generate, preview, and download structured PDF reports summarising your business feasibility analyses, location intelligence findings, and financial forecasts."
      phase="Phase 3"
      features={[
        { label: 'PDF export', desc: 'Branded, shareable report document' },
        { label: 'Report sections', desc: 'Summary, location, financials, risks' },
        { label: 'Custom branding', desc: 'Add your business name or logo' },
        { label: 'Saved reports', desc: 'Access previously generated PDFs' },
        { label: 'Share link', desc: 'Generate a read-only share URL' },
        { label: 'Data disclaimer', desc: 'Limitations clearly disclosed' },
      ]}
    />
  )
}
