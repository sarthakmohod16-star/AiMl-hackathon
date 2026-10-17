import React from 'react'
import PlaceholderPage from '@/components/ui/PlaceholderPage'

export default function Settings() {
  return (
    <PlaceholderPage
      title="Settings"
      description="Manage your account preferences, default currency, notification settings, and API configuration for the BizTwin platform."
      phase="Phase 3"
      features={[
        { label: 'Currency preference', desc: 'INR / USD and display format' },
        { label: 'Default radius', desc: 'Set your preferred search radius' },
        { label: 'Notifications', desc: 'Analysis completion alerts' },
        { label: 'Account details', desc: 'Name, email, and password' },
        { label: 'API configuration', desc: 'Backend endpoint and keys' },
        { label: 'Data privacy', desc: 'Export or delete your data' },
      ]}
    />
  )
}
