import {
  KpiData,
  MonthlyTrend,
  VendorSummary,
  VendorDetailResponse,
  CategoryData,
  PricingAnomaly,
  InventoryItem,
  AutomatedInsight,
  PipelineStatus,
  FilterState
} from '../types';

const API_BASE = '/api';

export async function fetchKpis(filters: FilterState): Promise<KpiData> {
  const params = new URLSearchParams();
  if (filters.vendor && filters.vendor !== 'all') params.append('vendor', filters.vendor);
  if (filters.category && filters.category !== 'all') params.append('category', filters.category);
  if (filters.location && filters.location !== 'all') params.append('location', filters.location);
  if (filters.startDate) params.append('start_date', filters.startDate);
  if (filters.endDate) params.append('end_date', filters.endDate);

  const res = await fetch(`${API_BASE}/kpis?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch KPIs');
  return res.json();
}

export async function fetchTrends(filters: FilterState): Promise<MonthlyTrend[]> {
  const params = new URLSearchParams();
  if (filters.vendor && filters.vendor !== 'all') params.append('vendor', filters.vendor);
  if (filters.category && filters.category !== 'all') params.append('category', filters.category);
  if (filters.startDate) params.append('start_date', filters.startDate);
  if (filters.endDate) params.append('end_date', filters.endDate);

  const res = await fetch(`${API_BASE}/trends?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch trends');
  return res.json();
}

export async function fetchVendors(filters: FilterState): Promise<VendorSummary[]> {
  const params = new URLSearchParams();
  if (filters.category && filters.category !== 'all') params.append('category', filters.category);
  if (filters.location && filters.location !== 'all') params.append('location', filters.location);

  const res = await fetch(`${API_BASE}/vendors?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch vendors');
  return res.json();
}

export async function fetchVendorDetails(vendorId: string): Promise<VendorDetailResponse> {
  const res = await fetch(`${API_BASE}/vendors/${vendorId}`);
  if (!res.ok) throw new Error('Failed to fetch vendor details');
  return res.json();
}

export async function fetchCategories(): Promise<CategoryData[]> {
  const res = await fetch(`${API_BASE}/categories`);
  if (!res.ok) throw new Error('Failed to fetch categories');
  return res.json();
}

export async function fetchScatter(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/scatter`);
  if (!res.ok) throw new Error('Failed to fetch scatter data');
  return res.json();
}

export async function fetchPricingAnomalies(): Promise<PricingAnomaly[]> {
  const res = await fetch(`${API_BASE}/pricing-anomalies`);
  if (!res.ok) throw new Error('Failed to fetch pricing anomalies');
  return res.json();
}

export async function fetchInventory(): Promise<InventoryItem[]> {
  const res = await fetch(`${API_BASE}/inventory`);
  if (!res.ok) throw new Error('Failed to fetch inventory');
  return res.json();
}

export async function fetchInsights(): Promise<AutomatedInsight[]> {
  const res = await fetch(`${API_BASE}/insights`);
  if (!res.ok) throw new Error('Failed to fetch automated insights');
  return res.json();
}

export async function fetchPipelineStatus(): Promise<PipelineStatus> {
  const res = await fetch(`${API_BASE}/pipeline-status`);
  if (!res.ok) throw new Error('Failed to fetch pipeline status');
  return res.json();
}

export interface VendorCreateData {
  vendor_code: string;
  vendor_name: string;
  category_id?: number;
  contact_name?: string;
  email: string;
  phone?: string;
  city?: string;
  country?: string;
  payment_terms?: string;
  lead_time_days?: number;
  status?: string;
  contract_start_date?: string;
}

export interface ImportPreviewResponse {
  total_rows: number;
  valid_rows: number;
  duplicate_rows: number;
  invalid_rows: number;
  error_details: Array<{ row: number; vendor_code?: string; vendor_name?: string; reason: string }>;
  valid_records: any[];
}

export async function createVendor(data: VendorCreateData): Promise<any> {
  const res = await fetch(`${API_BASE}/vendors/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to register vendor');
  }
  return res.json();
}

export async function previewVendorCsv(file: File): Promise<ImportPreviewResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/vendors/import/preview`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'CSV preview failed');
  }
  return res.json();
}

export async function confirmVendorCsvImport(records: any[]): Promise<any> {
  const res = await fetch(`${API_BASE}/vendors/import/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(records)
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to confirm CSV import');
  }
  return res.json();
}
