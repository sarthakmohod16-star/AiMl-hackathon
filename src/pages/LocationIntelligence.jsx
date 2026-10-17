import React from 'react'
import PlaceholderPage from '@/components/ui/PlaceholderPage'

export default function LocationIntelligence() {
  return (
    <PlaceholderPage
      title="Location Intelligence"
      description="Explore the competitive landscape around any location. Discover nearby businesses, classify direct and indirect competitors, and view density and market metrics."
      phase="Phase 3"
      features={[
        { label: 'Interactive map', desc: 'Pin and radius visualisation' },
        { label: 'Nearby businesses', desc: 'Competitor listing with distance' },
        { label: 'Competitor classification', desc: 'Direct vs indirect competitors' },
        { label: 'Density metrics', desc: 'Businesses per km² in radius' },
        { label: 'Category filters', desc: 'Filter by business type' },
        { label: 'Data source attribution', desc: 'Provider name and retrieval time' },
      ]}
    />
  )
}
