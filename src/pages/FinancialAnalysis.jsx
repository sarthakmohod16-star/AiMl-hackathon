import React from 'react'
import PlaceholderPage from '@/components/ui/PlaceholderPage'

export default function FinancialAnalysis() {
  return (
    <PlaceholderPage
      title="Financial Analysis"
      description="Review AI-powered financial forecasts, scenario comparisons, and Monte Carlo simulation results for your selected business and location."
      phase="Phase 3"
      features={[
        { label: 'Revenue projections', desc: '12 / 24 / 36-month forecasts' },
        { label: 'Monte Carlo chart', desc: 'Probability distribution of outcomes' },
        { label: 'Best / Base / Worst scenarios', desc: 'Side-by-side comparison' },
        { label: 'Break-even analysis', desc: 'Months to profitability' },
        { label: 'Risk factors', desc: 'Key drivers and sensitivities' },
        { label: 'Assumptions summary', desc: 'Full audit trail of inputs used' },
      ]}
    />
  )
}
