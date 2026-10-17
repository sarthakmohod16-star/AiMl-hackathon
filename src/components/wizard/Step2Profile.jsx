import React from 'react'
import { FieldWrapper, TextInput, SelectInput, TextareaInput } from './FormFields'
import { BUSINESS_CATEGORIES, BUSINESS_INDUSTRIES } from '@/data/wizardOptions'

/**
 * Step2Profile — Business name, category, industry, description.
 */
export default function Step2Profile({ fields, errors, touched, setField, blurField }) {
  const f = (name) => ({
    value: fields[name],
    error: touched[name] ? errors[name] : undefined,
    onChange: (v) => setField(name, v),
    onBlur: () => blurField(name),
  })

  return (
    <div className="wizard-step-content">
      <div className="wizard-step-heading">
        <span className="eyebrow" style={{ color: 'var(--copper)' }}>Business Profile</span>
        <h2 className="wizard-step-title">Tell us about your business</h2>
        <p className="wizard-step-desc">
          This information helps BizTwin identify comparable businesses and tailor the location analysis to your specific sector.
        </p>
      </div>

      <div className="wizard-form-grid">
        {/* Business name */}
        <div className="wizard-form-full">
          <FieldWrapper id="business_name" label="Business Name" required error={f('business_name').error}>
            <TextInput
              id="business_name"
              autoFocus
              placeholder="e.g. Sunrise Café"
              maxLength={100}
              {...f('business_name')}
            />
          </FieldWrapper>
        </div>

        {/* Category */}
        <FieldWrapper id="category" label="Business Category" required error={f('category').error}>
          <SelectInput id="category" options={BUSINESS_CATEGORIES} {...f('category')} />
        </FieldWrapper>

        {/* Industry */}
        <FieldWrapper id="industry" label="Industry / Domain" required error={f('industry').error}>
          <SelectInput id="industry" options={BUSINESS_INDUSTRIES} {...f('industry')} />
        </FieldWrapper>

        {/* Description — optional */}
        <div className="wizard-form-full">
          <FieldWrapper
            id="description"
            label="Description"
            hint="Optional"
            error={touched.description ? errors.description : undefined}
          >
            <TextareaInput
              id="description"
              placeholder="Briefly describe what your business offers, your target customers, or any distinguishing features…"
              rows={3}
              maxLength={500}
              value={fields.description}
              onChange={(v) => setField('description', v)}
              onBlur={() => blurField('description')}
            />
          </FieldWrapper>
          <p style={{ fontSize: 11.5, color: 'var(--muted)', marginTop: -12, marginBottom: 4 }}>
            {fields.description.length}/500 characters
          </p>
        </div>
      </div>
    </div>
  )
}
