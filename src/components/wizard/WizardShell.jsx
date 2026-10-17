import React from 'react'

/**
 * WizardShell — top-level layout for the multi-step wizard.
 *
 * Props:
 *  step        — current 0-based step index
 *  totalSteps  — total number of steps
 *  stepLabels  — array of step label strings
 *  onBack      — callback to go to previous step
 *  onNext      — callback to advance to next step
 *  onGoToStep  — callback(index) to jump backwards to a completed step
 *  isFinalStep — if true, the forward button says "Finish" or "Submit"
 *  isLoading   — disables navigation while async work runs
 *  children    — current step content
 */
export default function WizardShell({
  step,
  totalSteps,
  stepLabels,
  onBack,
  onNext,
  onGoToStep,
  isFinalStep = false,
  isLoading = false,
  children,
}) {
  const pct = Math.round(((step + 1) / totalSteps) * 100)

  return (
    <div className="wizard-shell">
      {/* Progress header */}
      <div className="wizard-header">
        <div className="wizard-steps" role="list" aria-label="Wizard steps">
          {stepLabels.map((label, idx) => {
            const done = idx < step
            const active = idx === step
            const clickable = idx < step

            return (
              <div
                key={idx}
                className={`wizard-step-item${done ? ' done' : ''}${active ? ' active' : ''}`}
                role="listitem"
                aria-current={active ? 'step' : undefined}
              >
                <button
                  type="button"
                  className="wizard-step-btn"
                  onClick={() => clickable && onGoToStep(idx)}
                  disabled={!clickable}
                  aria-label={`Step ${idx + 1}: ${label}${done ? ' (completed)' : active ? ' (current)' : ''}`}
                >
                  <span className="wizard-step-circle" aria-hidden="true">
                    {done ? '✓' : idx + 1}
                  </span>
                  <span className="wizard-step-label">{label}</span>
                </button>
                {idx < stepLabels.length - 1 && (
                  <span className={`wizard-step-connector${done ? ' done' : ''}`} aria-hidden="true" />
                )}
              </div>
            )
          })}
        </div>

        {/* Compact progress bar for mobile */}
        <div className="wizard-progress-bar" aria-hidden="true">
          <div className="wizard-progress-fill" style={{ width: `${pct}%` }} />
        </div>
        <p className="wizard-progress-label" aria-live="polite">
          Step {step + 1} of {totalSteps}
        </p>
      </div>

      {/* Step content area */}
      <div className="wizard-body">
        {children}
      </div>

      {/* Navigation footer */}
      <div className="wizard-footer">
        <div className="wizard-footer-left">
          {step > 0 && (
            <button
              type="button"
              className="button button-outline"
              onClick={onBack}
              disabled={isLoading}
            >
              ← Back
            </button>
          )}
        </div>
        <div className="wizard-footer-right">
          <button
            type="button"
            className="button button-dark"
            onClick={onNext}
            disabled={isLoading}
          >
            {isFinalStep ? 'Finish & Review' : 'Continue →'}
          </button>
        </div>
      </div>
    </div>
  )
}
