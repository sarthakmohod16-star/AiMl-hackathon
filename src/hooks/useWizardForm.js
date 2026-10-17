import { useState, useCallback } from 'react'

/** Initial form field values — defined at module scope so it's referentially stable */
const INITIAL_FIELDS = {
  // Step 1 — Mode
  mode: '', // 'new' | 'existing'

  // Step 2 — Business profile
  business_name: '',
  category: '',
  industry: '',
  description: '',

  // Step 3 — Location
  country: '',
  city: '',
  address: '',
  radius_meters: 1500,

  // Step 4 — Historical data (existing mode only)
  currency: 'INR',
  annual_revenue: '',
  annual_expenses: '',
  avg_monthly_customers: '',
  years_in_operation: '',
  historical_notes: '',
}

/** Validate a single field — returns an error string or empty string */
function validateField(name, value, allFields) {
  switch (name) {
    case 'mode':
      return value ? '' : 'Please select a business type to continue.'

    case 'business_name':
      if (!value.trim()) return 'Business name is required.'
      if (value.trim().length < 2) return 'Name must be at least 2 characters.'
      if (value.trim().length > 100) return 'Name must be 100 characters or fewer.'
      return ''

    case 'category':
      return value ? '' : 'Please select a business category.'

    case 'industry':
      return value ? '' : 'Please select an industry / domain.'

    case 'country':
      return value ? '' : 'Please select a country.'

    case 'city':
      if (!value.trim()) return 'City is required.'
      if (value.trim().length < 2) return 'Enter a valid city name.'
      return ''

    case 'address':
      if (!value.trim()) return 'Address or target area is required.'
      if (value.trim().length < 5) return 'Please enter a more specific address.'
      return ''

    // Historical fields — only required when mode is 'existing'
    case 'annual_revenue':
      if (allFields.mode !== 'existing') return ''
      if (!value.toString().trim()) return 'Annual revenue is required for existing businesses.'
      if (isNaN(Number(value)) || Number(value) < 0) return 'Enter a valid non-negative number.'
      return ''

    case 'annual_expenses':
      if (allFields.mode !== 'existing') return ''
      if (!value.toString().trim()) return 'Annual expenses are required for existing businesses.'
      if (isNaN(Number(value)) || Number(value) < 0) return 'Enter a valid non-negative number.'
      return ''

    default:
      return ''
  }
}

/** Returns the list of field names that belong to a given step */
function getStepFields(stepIndex, mode) {
  // Steps: 0=mode, 1=profile, 2=location, 3=history(existing)/review(new), 4=review(existing)
  if (stepIndex === 0) return ['mode']
  if (stepIndex === 1) return ['business_name', 'category', 'industry']
  if (stepIndex === 2) return ['country', 'city', 'address']
  if (stepIndex === 3 && mode === 'existing') return ['annual_revenue', 'annual_expenses']
  return [] // review step — no new fields
}

/** Validate all fields for a given step. Returns { isValid, errors } */
function validateStep(stepIndex, allFields) {
  const stepFields = getStepFields(stepIndex, allFields.mode)
  const newErrors = {}

  for (const fieldName of stepFields) {
    const err = validateField(fieldName, allFields[fieldName], allFields)
    if (err) newErrors[fieldName] = err
  }

  return { isValid: Object.keys(newErrors).length === 0, errors: newErrors }
}

/**
 * useWizardForm
 *
 * Manages all state, validation, and step navigation for the
 * Business Setup Wizard. Completely decoupled from UI components.
 */
export function useWizardForm() {
  const [step, setStep] = useState(0)
  const [fields, setFields] = useState(INITIAL_FIELDS)
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})

  // Determine total steps based on mode
  // Mode = 'existing' → 5 steps (mode, profile, location, history, review)
  // Mode = 'new'      → 4 steps (mode, profile, location, review — no history)
  const totalSteps = fields.mode === 'existing' ? 5 : 4

  const setField = useCallback((name, value) => {
    setFields((prev) => ({ ...prev, [name]: value }))
    // Clear error as user types
    setErrors((prev) => {
      if (!prev[name]) return prev
      const next = { ...prev }
      delete next[name]
      return next
    })
  }, [])

  const blurField = useCallback((name) => {
    setTouched((prev) => ({ ...prev, [name]: true }))
    setFields((cur) => {
      const err = validateField(name, cur[name], cur)
      setErrors((prev) => ({
        ...prev,
        ...(err ? { [name]: err } : (() => { const n = { ...prev }; delete n[name]; return n })()),
      }))
      return cur
    })
  }, [])

  /** Advance to the next step. Returns true if valid, false if blocked. */
  const next = useCallback(() => {
    setFields((cur) => {
      const { isValid, errors: stepErrors } = validateStep(step, cur)
      // Mark all step fields as touched so errors appear
      const stepFields = getStepFields(step, cur.mode)
      setTouched((prev) => {
        const next = { ...prev }
        stepFields.forEach((f) => { next[f] = true })
        return next
      })
      if (!isValid) {
        setErrors((prev) => ({ ...prev, ...stepErrors }))
        return cur
      }
      setStep((s) => Math.min(s + 1, totalSteps - 1))
      return cur
    })
  }, [step, totalSteps])

  const back = useCallback(() => {
    setStep((s) => Math.max(s - 1, 0))
  }, [])

  const goToStep = useCallback((target) => {
    if (target < step) setStep(target)
  }, [step])

  const isStepValid = useCallback((stepIndex) => {
    const { isValid } = validateStep(stepIndex, fields)
    return isValid
  }, [fields])

  const reset = useCallback(() => {
    setStep(0)
    setFields(INITIAL_FIELDS)
    setErrors({})
    setTouched({})
  }, [])

  return {
    step,
    totalSteps,
    fields,
    errors,
    touched,
    setField,
    blurField,
    next,
    back,
    goToStep,
    isStepValid,
    reset,
  }
}
