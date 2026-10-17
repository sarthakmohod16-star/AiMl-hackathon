/**
 * BizTwin — Mock Data
 *
 * ⚠️  DEMO DATA — Not real business intelligence.
 * All figures, names, and locations are illustrative only.
 * Replace this file with real API responses when the backend is ready.
 */

export const MOCK_SUMMARY = {
  total_analyses: 5,
  completed_analyses: 3,
  processing_analyses: 1,
  failed_analyses: 1,
  saved_reports: 2,
};

export const MOCK_RECENT_ANALYSES = [
  {
    analysis_id: 'analysis_001',
    business_name: 'Sunrise Café',
    mode: 'new',
    category: 'Café',
    location_label: 'Bandra West, Mumbai',
    status: 'completed',
    recommendation_label: 'proceed',
    created_at: '2026-10-14T09:15:00Z',
  },
  {
    analysis_id: 'analysis_002',
    business_name: 'GreenLeaf Organic Store',
    mode: 'new',
    category: 'Retail',
    location_label: 'Koramangala, Bengaluru',
    status: 'completed',
    recommendation_label: 'caution',
    created_at: '2026-10-12T14:30:00Z',
  },
  {
    analysis_id: 'analysis_003',
    business_name: 'City Fitness Hub',
    mode: 'existing',
    category: 'Fitness',
    location_label: 'Andheri East, Mumbai',
    status: 'processing',
    recommendation_label: 'pending',
    created_at: '2026-10-16T11:00:00Z',
  },
  {
    analysis_id: 'analysis_004',
    business_name: 'The Book Nook',
    mode: 'new',
    category: 'Retail',
    location_label: 'Indiranagar, Bengaluru',
    status: 'completed',
    recommendation_label: 'stop',
    created_at: '2026-10-10T08:45:00Z',
  },
  {
    analysis_id: 'analysis_005',
    business_name: 'Quick Bites QSR',
    mode: 'new',
    category: 'Restaurant',
    location_label: 'Powai, Mumbai',
    status: 'failed',
    recommendation_label: 'pending',
    created_at: '2026-10-08T16:20:00Z',
  },
];

export const MOCK_EMPTY_ANALYSES = [];
