/**
 * BizTwin — Wizard / Form Reference Data
 *
 * Lightweight reference lists used by the Business Setup Wizard.
 * No backend call needed for these static options.
 * ⚠️  Add or remove entries to match agreed taxonomy before Phase 3.
 */

export const BUSINESS_CATEGORIES = [
  { value: '', label: 'Select a category…' },
  { value: 'cafe', label: 'Café / Coffee Shop' },
  { value: 'restaurant', label: 'Restaurant' },
  { value: 'qsr', label: 'Quick Service Restaurant (QSR)' },
  { value: 'bakery', label: 'Bakery / Patisserie' },
  { value: 'retail_grocery', label: 'Retail — Grocery / Supermarket' },
  { value: 'retail_fashion', label: 'Retail — Fashion / Apparel' },
  { value: 'retail_electronics', label: 'Retail — Electronics' },
  { value: 'retail_general', label: 'Retail — General' },
  { value: 'salon', label: 'Salon / Barbershop' },
  { value: 'spa_wellness', label: 'Spa & Wellness' },
  { value: 'fitness', label: 'Gym / Fitness Studio' },
  { value: 'pharmacy', label: 'Pharmacy' },
  { value: 'clinic', label: 'Clinic / Healthcare' },
  { value: 'education', label: 'Education / Coaching Centre' },
  { value: 'coworking', label: 'Co-working Space' },
  { value: 'logistics', label: 'Logistics / Courier' },
  { value: 'other', label: 'Other / Custom' },
]

export const BUSINESS_INDUSTRIES = [
  { value: '', label: 'Select an industry…' },
  { value: 'food_beverage', label: 'Food & Beverage' },
  { value: 'retail', label: 'Retail & Commerce' },
  { value: 'health_wellness', label: 'Health & Wellness' },
  { value: 'education', label: 'Education & Training' },
  { value: 'professional_services', label: 'Professional Services' },
  { value: 'hospitality', label: 'Hospitality & Tourism' },
  { value: 'technology', label: 'Technology & Software' },
  { value: 'logistics', label: 'Logistics & Supply Chain' },
  { value: 'real_estate', label: 'Real Estate' },
  { value: 'other', label: 'Other' },
]

export const COUNTRIES = [
  { value: '', label: 'Select a country…' },
  { value: 'IN', label: 'India' },
  { value: 'US', label: 'United States' },
  { value: 'GB', label: 'United Kingdom' },
  { value: 'SG', label: 'Singapore' },
  { value: 'AE', label: 'United Arab Emirates' },
  { value: 'AU', label: 'Australia' },
  { value: 'CA', label: 'Canada' },
  { value: 'DE', label: 'Germany' },
  { value: 'FR', label: 'France' },
  { value: 'other', label: 'Other' },
]

export const RADIUS_OPTIONS = [
  { value: 500,  label: '500 m — Immediate vicinity' },
  { value: 1000, label: '1 km — Neighbourhood' },
  { value: 1500, label: '1.5 km' },
  { value: 2000, label: '2 km — Local area' },
  { value: 3000, label: '3 km' },
  { value: 5000, label: '5 km — District / Zone' },
]

export const CURRENCY_OPTIONS = [
  { value: 'INR', label: '₹ INR — Indian Rupee' },
  { value: 'USD', label: '$ USD — US Dollar' },
  { value: 'GBP', label: '£ GBP — British Pound' },
  { value: 'SGD', label: 'S$ SGD — Singapore Dollar' },
  { value: 'AED', label: 'AED — UAE Dirham' },
  { value: 'AUD', label: 'A$ AUD — Australian Dollar' },
]
