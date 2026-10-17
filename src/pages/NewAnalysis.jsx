import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useWizardForm } from '@/hooks/useWizardForm'
import WizardShell from '@/components/wizard/WizardShell'
import Step1Mode from '@/components/wizard/Step1Mode'
import Step2Profile from '@/components/wizard/Step2Profile'
import Step3Location from '@/components/wizard/Step3Location'
import Step4History from '@/components/wizard/Step4History'
import StepReview from '@/components/wizard/StepReview'

/** Step labels differ by mode (history step only appears for existing businesses) */
function getStepLabels(mode) {
  const base = ['Business Type', 'Business Profile', 'Location']
  if (mode === 'existing') return [...base, 'Historical Data', 'Review']
  return [...base, 'Review']
}

/**
 * NewAnalysis — Business Setup Wizard page.
 * Replaces the Phase 2 placeholder with a fully functional multi-step form.
 */
export default function NewAnalysis() {
  const wizard = useWizardForm()
  const [submitted, setSubmitted] = useState(false)

  const stepLabels = getStepLabels(wizard.fields.mode)

  // Which component to render at each step index
  // new:      0=mode, 1=profile, 2=location, 3=review
  // existing: 0=mode, 1=profile, 2=location, 3=history, 4=review
  function renderStep() {
    const { step, fields, errors, touched, setField, blurField, goToStep } = wizard

    if (step === 0) {
      return <Step1Mode fields={fields} errors={errors} touched={touched} setField={setField} />
    }
    if (step === 1) {
      return (
        <Step2Profile
          fields={fields} errors={errors} touched={touched}
          setField={setField} blurField={blurField}
        />
      )
    }
    if (step === 2) {
      return (
        <Step3Location
          fields={fields} errors={errors} touched={touched}
          setField={setField} blurField={blurField}
        />
      )
    }
    if (step === 3 && fields.mode === 'existing') {
      return (
        <Step4History
          fields={fields} errors={errors} touched={touched}
          setField={setField} blurField={blurField}
        />
      )
    }
    // Final step — review
    return (
      <StepReview
        fields={fields}
        onGoToStep={goToStep}
        onSubmit={() => setSubmitted(true)}
      />
    )
  }

  // Submitted / success state
  if (submitted) {
    return (
      <div className="wizard-submitted">
        <div className="wizard-submitted-icon" aria-hidden="true">✓</div>
        <h2>Business setup complete</h2>
        <p>
          Your business profile, location, and
          {wizard.fields.mode === 'existing' ? ' historical records have' : ' preferences have'}
          {' '}been captured. The next step is to enter your financial assumptions — this will be available once the backend is connected in Phase 3.
        </p>
        <p style={{ fontSize: 13, color: 'var(--muted)' }}>
          <strong>Note:</strong> No data has been sent to a server. Everything is held in your browser session only.
        </p>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 8 }}>
          <button
            type="button"
            className="button button-dark"
            onClick={() => {
              setSubmitted(false)
              wizard.reset()
            }}
          >
            Start another analysis
          </button>
          <Link to="/" className="button button-outline">
            Back to Dashboard
          </Link>
        </div>

        {/* Debug: show collected form data (remove in production) */}
        <details style={{ marginTop: 24, width: '100%' }}>
          <summary style={{ cursor: 'pointer', fontSize: 12.5, color: 'var(--muted)', userSelect: 'none' }}>
            View collected form data (dev only — remove before production)
          </summary>
          <pre style={{
            marginTop: 10,
            padding: 16,
            background: '#f0f0ea',
            borderRadius: 4,
            fontSize: 12,
            overflowX: 'auto',
            lineHeight: 1.7,
            border: '1px solid var(--line)',
          }}>
            {JSON.stringify(wizard.fields, null, 2)}
          </pre>
        </details>
      </div>
    )
  }

  const isFinalStep = wizard.step === wizard.totalSteps - 1

  return (
    <WizardShell
      step={wizard.step}
      totalSteps={wizard.totalSteps}
      stepLabels={stepLabels}
      onBack={wizard.back}
      onNext={isFinalStep ? () => setSubmitted(true) : wizard.next}
      onGoToStep={wizard.goToStep}
      isFinalStep={isFinalStep}
    >
      {renderStep()}
    </WizardShell>
  )
}
