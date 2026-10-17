import React from 'react'

/**
 * FieldWrapper — consistent label + input + error layout.
 *
 * Props:
 *  id       — links label to input (required)
 *  label    — display label string
 *  required — show required asterisk
 *  error    — error string; if present, renders error text
 *  hint     — optional helper text below the label
 *  children — the actual input / select / textarea element
 */
export function FieldWrapper({ id, label, required = false, error, hint, children }) {
  return (
    <div className={`field${error ? ' field-error' : ''}`}>
      <label htmlFor={id}>
        {label}
        {required && <span style={{ color: '#b85c38', marginLeft: 3 }} aria-hidden="true">*</span>}
        {hint && (
          <span style={{ fontWeight: 400, fontSize: 11, color: 'var(--muted)', marginLeft: 8, textTransform: 'none', letterSpacing: 0 }}>
            {hint}
          </span>
        )}
      </label>
      {children}
      {error && <p className="field-error-msg" role="alert" id={`${id}-error`}>{error}</p>}
    </div>
  )
}

/**
 * TextInput — standard single-line text input.
 */
export function TextInput({ id, value, onChange, onBlur, placeholder, maxLength, autoFocus, error, type = 'text' }) {
  return (
    <input
      id={id}
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onBlur={onBlur}
      placeholder={placeholder}
      maxLength={maxLength}
      autoFocus={autoFocus}
      aria-invalid={!!error}
      aria-describedby={error ? `${id}-error` : undefined}
      autoComplete="off"
    />
  )
}

/**
 * SelectInput — styled native <select>.
 */
export function SelectInput({ id, value, onChange, onBlur, options, error }) {
  return (
    <select
      id={id}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onBlur={onBlur}
      aria-invalid={!!error}
      aria-describedby={error ? `${id}-error` : undefined}
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value} disabled={opt.value === ''}>
          {opt.label}
        </option>
      ))}
    </select>
  )
}

/**
 * TextareaInput — multi-line textarea.
 */
export function TextareaInput({ id, value, onChange, onBlur, placeholder, rows = 3, maxLength, error }) {
  return (
    <textarea
      id={id}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onBlur={onBlur}
      placeholder={placeholder}
      rows={rows}
      maxLength={maxLength}
      aria-invalid={!!error}
      aria-describedby={error ? `${id}-error` : undefined}
    />
  )
}

/**
 * NumberInput — numeric input with optional prefix (currency symbol).
 */
export function NumberInput({ id, value, onChange, onBlur, placeholder, prefix, min = 0, error }) {
  return (
    <div className="input-with-prefix">
      {prefix && <span className="input-prefix" aria-hidden="true">{prefix}</span>}
      <input
        id={id}
        type="number"
        min={min}
        step="any"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
        placeholder={placeholder}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        style={prefix ? { borderTopLeftRadius: 0, borderBottomLeftRadius: 0 } : {}}
      />
    </div>
  )
}
