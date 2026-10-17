import React from 'react'
import { FieldWrapper, TextInput, SelectInput } from './FormFields'
import { COUNTRIES, RADIUS_OPTIONS } from '@/data/wizardOptions'

/**
 * Step3Location — Country, city, address/area, and search radius.
 */
export default function Step3Location({ fields, errors, touched, setField, blurField }) {
  const f = (name) => ({
    value: fields[name],
    error: touched[name] ? errors[name] : undefined,
    onChange: (v) => setField(name, v),
    onBlur: () => blurField(name),
  })

  const selectedRadius = RADIUS_OPTIONS.find((r) => r.value === fields.radius_meters) || RADIUS_OPTIONS[2]

  return (
    <div className="wizard-step-content">
      <div className="wizard-step-heading">
        <span className="eyebrow" style={{ color: 'var(--copper)' }}>Location Details</span>
        <h2 className="wizard-step-title">Where is your business located?</h2>
        <p className="wizard-step-desc">
          Enter the exact address or target area. BizTwin will use this to map nearby competitors and assess the local market.
        </p>
      </div>

      <div className="wizard-form-grid">
        {/* Country */}
        <FieldWrapper id="country" label="Country" required error={f('country').error}>
          <SelectInput id="country" options={COUNTRIES} {...f('country')} />
        </FieldWrapper>

        {/* City */}
        <FieldWrapper id="city" label="City" required error={f('city').error}>
          <TextInput
            id="city"
            placeholder="e.g. Mumbai, Bengaluru, Delhi"
            maxLength={100}
            {...f('city')}
          />
        </FieldWrapper>

        {/* Address — full width */}
        <div className="wizard-form-full">
          <FieldWrapper
            id="address"
            label="Business Address or Target Area"
            required
            error={f('address').error}
            hint="Street address, locality, landmark, or general area"
          >
            <TextInput
              id="address"
              placeholder="e.g. 14 Turner Road, Bandra West"
              maxLength={200}
              {...f('address')}
            />
          </FieldWrapper>
        </div>

        {/* Radius — full width with visual selector */}
        <div className="wizard-form-full">
          <FieldWrapper
            id="radius_meters"
            label="Competition Search Radius"
            hint="How far around your location to look for nearby businesses"
          >
            <div className="radius-selector" role="group" aria-label="Search radius">
              {RADIUS_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  className={`radius-btn${fields.radius_meters === opt.value ? ' radius-btn--active' : ''}`}
                  onClick={() => setField('radius_meters', opt.value)}
                  aria-pressed={fields.radius_meters === opt.value}
                >
                  {opt.value >= 1000 ? `${opt.value / 1000} km` : `${opt.value} m`}
                </button>
              ))}
            </div>
            <p style={{ fontSize: 12, color: 'var(--muted)', marginTop: 8 }}>
              Selected: <strong>{selectedRadius.label}</strong>
            </p>
          </FieldWrapper>
        </div>
      </div>

      {/* Map placeholder — will be replaced by real map in Phase 3 */}
      <div className="map-placeholder" role="img" aria-label="Map area — interactive map coming in Phase 3">
        <div className="map-placeholder-inner">
          <span style={{ fontSize: 28 }} aria-hidden="true">🗺</span>
          <p>Interactive map coming in Phase 3.</p>
          <p style={{ fontSize: 12, color: 'var(--muted)' }}>
            A live map with your address pin and radius circle will appear here when the location provider is connected.
          </p>
        </div>
      </div>
    </div>
  )
}
