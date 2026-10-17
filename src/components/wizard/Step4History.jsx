import React from 'react'
import { FieldWrapper, NumberInput, TextareaInput, SelectInput } from './FormFields'
import { CURRENCY_OPTIONS } from '@/data/wizardOptions'

/** Currency symbol lookup */
const CURRENCY_SYMBOLS = { INR: '₹', USD: '$', GBP: '£', SGD: 'S$', AED: 'د.إ', AUD: 'A$' }

/**
 * Step4History — Historical financial records for existing businesses.
 * This step is only shown when fields.mode === 'existing'.
 */
export default function Step4History({ fields, errors, touched, setField, blurField }) {
  const f = (name) => ({
    value: fields[name],
    error: touched[name] ? errors[name] : undefined,
    onChange: (v) => setField(name, v),
    onBlur: () => blurField(name),
  })

  const symbol = CURRENCY_SYMBOLS[fields.currency] || fields.currency

  return (
    <div className="wizard-step-content">
      <div className="wizard-step-heading">
        <span className="eyebrow" style={{ color: 'var(--copper)' }}>Historical Business Records</span>
        <h2 className="wizard-step-title">Share your business performance data</h2>
        <p className="wizard-step-desc">
          These records allow BizTwin to produce higher-confidence projections by anchoring the analysis to your real operating history.
          Only annual revenue and expenses are required — all other fields are optional.
        </p>
      </div>

      {/* Data transparency notice */}
      <div className="info-notice" role="note">
        <span style={{ fontSize: 18 }} aria-hidden="true">🔒</span>
        <div>
          <strong>Your data stays local</strong>
          <p style={{ fontSize: 13, color: 'var(--muted)', marginTop: 2, lineHeight: 1.6 }}>
            In this phase, data is held in your browser only. No records are sent to a server until the backend is connected in Phase 3.
            Do not enter real confidential figures until that connection is secured.
          </p>
        </div>
      </div>

      <div className="wizard-form-grid">
        {/* Currency */}
        <div className="wizard-form-full">
          <FieldWrapper id="currency" label="Currency">
            <SelectInput id="currency" options={CURRENCY_OPTIONS} {...f('currency')} />
          </FieldWrapper>
        </div>

        {/* Annual revenue — required */}
        <FieldWrapper
          id="annual_revenue"
          label="Annual Revenue (last full year)"
          required
          error={f('annual_revenue').error}
          hint={`Total sales before expenses, in ${fields.currency}`}
        >
          <NumberInput
            id="annual_revenue"
            prefix={symbol}
            placeholder="e.g. 3600000"
            min={0}
            {...f('annual_revenue')}
          />
        </FieldWrapper>

        {/* Annual expenses — required */}
        <FieldWrapper
          id="annual_expenses"
          label="Annual Expenses (last full year)"
          required
          error={f('annual_expenses').error}
          hint={`Total operating costs, in ${fields.currency}`}
        >
          <NumberInput
            id="annual_expenses"
            prefix={symbol}
            placeholder="e.g. 2800000"
            min={0}
            {...f('annual_expenses')}
          />
        </FieldWrapper>

        {/* Average monthly customers — optional */}
        <FieldWrapper
          id="avg_monthly_customers"
          label="Average Monthly Customers"
          hint="Optional — unique paying customers per month"
          error={f('avg_monthly_customers').error}
        >
          <NumberInput
            id="avg_monthly_customers"
            placeholder="e.g. 850"
            min={0}
            {...f('avg_monthly_customers')}
          />
        </FieldWrapper>

        {/* Years in operation — optional */}
        <FieldWrapper
          id="years_in_operation"
          label="Years in Operation"
          hint="Optional"
          error={f('years_in_operation').error}
        >
          <NumberInput
            id="years_in_operation"
            placeholder="e.g. 3"
            min={0}
            {...f('years_in_operation')}
          />
        </FieldWrapper>

        {/* Notes — optional */}
        <div className="wizard-form-full">
          <FieldWrapper
            id="historical_notes"
            label="Additional Notes"
            hint="Optional — seasonal patterns, one-off events, or other context"
          >
            <TextareaInput
              id="historical_notes"
              rows={3}
              placeholder="e.g. Revenue spike in November due to Diwali. One location closed in March."
              maxLength={400}
              value={fields.historical_notes}
              onChange={(v) => setField('historical_notes', v)}
              onBlur={() => blurField('historical_notes')}
            />
          </FieldWrapper>
        </div>
      </div>

      {/* Note: CSV upload deferred to Phase 3 */}
      <div className="info-notice info-notice--muted" role="note" style={{ marginTop: 8 }}>
        <span style={{ fontSize: 18 }} aria-hidden="true">📎</span>
        <div>
          <strong>CSV / XLSX upload</strong>
          <p style={{ fontSize: 13, color: 'var(--muted)', marginTop: 2, lineHeight: 1.6 }}>
            Bulk historical data upload (CSV or XLSX) will be available in Phase 3 once the backend validation
            pipeline is ready. For now, enter key summary figures above.
          </p>
        </div>
      </div>
    </div>
  )
}
