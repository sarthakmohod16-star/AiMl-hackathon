/**
 * BizTwin — Location Intelligence Mock Data
 *
 * ⚠️  DEMO DATA — Not real businesses or market intelligence.
 * All names, addresses, coordinates, and distances are illustrative only.
 * Replace this file with real API responses when the backend is ready.
 *
 * Shape follows the BizTwin spec:
 *   POST /api/locations/analyze → response.businesses[]
 */

/* ---------- Selected location (simulates wizard output) ---------- */
export const MOCK_SELECTED_LOCATION = {
  label: 'Bandra West, Mumbai, Maharashtra',
  latitude: 19.0607,
  longitude: 72.8362,
  radius_meters: 1500,
  business_category: 'cafe',
  business_name: 'Sunrise Café',
};

/* ---------- Nearby businesses ------------------------------------ */
export const MOCK_NEARBY_BUSINESSES = [
  {
    id: 'mock_biz_001',
    name: 'Chai Point',
    category: 'cafe',
    latitude: 19.0612,
    longitude: 72.837,
    distance_meters: 180,
    competitor_type: 'direct',
    address: '12 Hill Road, Bandra West',
    public_attributes: {},
    source: 'demo_provider',
  },
  {
    id: 'mock_biz_002',
    name: 'The Rolling Pin Bakery',
    category: 'bakery',
    latitude: 19.062,
    longitude: 72.835,
    distance_meters: 310,
    competitor_type: 'indirect',
    address: '5A Carter Road, Bandra West',
    public_attributes: {},
    source: 'demo_provider',
  },
  {
    id: 'mock_biz_003',
    name: 'Blue Tokai Coffee',
    category: 'cafe',
    latitude: 19.059,
    longitude: 72.834,
    distance_meters: 420,
    competitor_type: 'direct',
    address: '28 Pali Naka, Bandra West',
    public_attributes: {},
    source: 'demo_provider',
  },
  {
    id: 'mock_biz_004',
    name: 'McDonald\'s',
    category: 'qsr',
    latitude: 19.063,
    longitude: 72.839,
    distance_meters: 580,
    competitor_type: 'indirect',
    address: 'Turner Road, Bandra West',
    public_attributes: {},
    source: 'demo_provider',
  },
  {
    id: 'mock_biz_005',
    name: 'Third Wave Coffee',
    category: 'cafe',
    latitude: 19.058,
    longitude: 72.838,
    distance_meters: 640,
    competitor_type: 'direct',
    address: '17 Linking Road, Bandra West',
    public_attributes: {},
    source: 'demo_provider',
  },
  {
    id: 'mock_biz_006',
    name: 'Nutcracker',
    category: 'restaurant',
    latitude: 19.064,
    longitude: 72.832,
    distance_meters: 750,
    competitor_type: 'indirect',
    address: '3 Pali Hill, Bandra West',
    public_attributes: {},
    source: 'demo_provider',
  },
  {
    id: 'mock_biz_007',
    name: 'Starbucks',
    category: 'cafe',
    latitude: 19.055,
    longitude: 72.837,
    distance_meters: 920,
    competitor_type: 'direct',
    address: 'Linking Road, Bandra West',
    public_attributes: {},
    source: 'demo_provider',
  },
  {
    id: 'mock_biz_008',
    name: 'Yoga House Café',
    category: 'cafe',
    latitude: 19.065,
    longitude: 72.834,
    distance_meters: 1050,
    competitor_type: 'direct',
    address: 'Chapel Road, Bandra West',
    public_attributes: {},
    source: 'demo_provider',
  },
  {
    id: 'mock_biz_009',
    name: 'Green Leaf Juicery',
    category: 'cafe',
    latitude: 19.057,
    longitude: 72.832,
    distance_meters: 1180,
    competitor_type: 'indirect',
    address: '9B Hill Road, Bandra West',
    public_attributes: {},
    source: 'demo_provider',
  },
  {
    id: 'mock_biz_010',
    name: 'Domino\'s Pizza',
    category: 'qsr',
    latitude: 19.053,
    longitude: 72.836,
    distance_meters: 1350,
    competitor_type: 'indirect',
    address: 'S.V. Road, Bandra West',
    public_attributes: {},
    source: 'demo_provider',
  },
];

/* ---------- Summary stats ---------------------------------------- */
export const MOCK_LOCATION_SUMMARY = {
  nearby_business_count: MOCK_NEARBY_BUSINESSES.length,
  direct_competitor_count: MOCK_NEARBY_BUSINESSES.filter(
    (b) => b.competitor_type === 'direct'
  ).length,
  indirect_competitor_count: MOCK_NEARBY_BUSINESSES.filter(
    (b) => b.competitor_type === 'indirect'
  ).length,
  density_per_square_km: 1.41, // illustrative
};

/* ---------- Data sources ----------------------------------------- */
export const MOCK_SOURCES = [
  {
    name: 'demo_provider',
    data_type: 'nearby_businesses',
    retrieved_at: '2026-10-17T10:30:00Z',
  },
];

/* ---------- Warnings / limitations ------------------------------- */
export const MOCK_WARNINGS = [];
export const MOCK_LIMITATIONS = [
  'Demo data — does not represent real businesses or locations.',
  'Distance values are approximate and illustrative only.',
];

/* ---------- Filter options --------------------------------------- */
export const COMPETITOR_CATEGORIES = [
  { value: '', label: 'All categories' },
  { value: 'cafe', label: 'Café / Coffee Shop' },
  { value: 'bakery', label: 'Bakery' },
  { value: 'restaurant', label: 'Restaurant' },
  { value: 'qsr', label: 'Quick Service (QSR)' },
];

export const DISTANCE_FILTERS = [
  { value: 0, label: 'All distances' },
  { value: 500, label: '< 500 m' },
  { value: 1000, label: '< 1 km' },
  { value: 1500, label: '< 1.5 km' },
];
