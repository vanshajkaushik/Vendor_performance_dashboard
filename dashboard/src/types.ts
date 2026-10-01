export interface KpiData {
  total_sales: number;
  total_procurement: number;
  gross_profit: number;
  gross_margin_pct: number;
  purchase_volume: number;
  sales_volume: number;
  active_vendors: number;
  total_products: number;
  avg_vendor_performance_score: number;
  purchase_to_sales_ratio: number;
}

export interface MonthlyTrend {
  month: string;
  sales_revenue: number;
  procurement_spend: number;
  gross_profit: number;
  gross_margin_pct: number;
}

export interface VendorSummary {
  vendor_id: string;
  vendor_name: string;
  vendor_category: string;
  location: string;
  rating: number;
  total_procurement_cost: number;
  total_revenue: number;
  gross_profit: number;
  gross_margin_pct: number;
  purchase_to_sales_ratio: number;
  price_variance_pct: number;
  inventory_turnover: number;
  spend_share_pct: number;
  revenue_share_pct: number;
  vendor_performance_score: number;
  performance_tier: string;
  recommendation: string;
  score_revenue?: number;
  score_margin?: number;
  score_efficiency?: number;
  score_pricing?: number;
  score_ops?: number;
  contact_name?: string;
  contact_email?: string;
  phone?: string;
  contract_start_date?: string;
}

export interface VendorDetailResponse {
  profile: VendorSummary;
  monthly_trend: Array<{ month: string; spend: number; units: number }>;
  products: Array<{
    product_id: string;
    product_name: string;
    category: string;
    subcategory: string;
    unit_cost: number;
    avg_price_paid: number;
    price_variance_pct: number;
    orders_count: number;
    units_purchased: number;
    total_spend: number;
  }>;
}

export interface CategoryData {
  category: string;
  sales_revenue: number;
  procurement_spend: number;
  gross_profit: number;
  gross_margin_pct: number;
  product_count: number;
}

export interface PricingAnomaly {
  vendor_id: string;
  vendor_name: string;
  product_id: string;
  product_name: string;
  category: string;
  unit_cost: number;
  avg_purchase_price: number;
  price_variance_pct: number;
  order_count: number;
  total_qty: number;
}

export interface InventoryItem {
  product_id: string;
  product_name: string;
  category: string;
  vendor_id: string;
  vendor_name: string;
  stock_quantity: number;
  reorder_level: number;
  safety_stock: number;
  inventory_value: number;
  reorder_deficit: number;
  status: string;
}

export interface AutomatedInsight {
  type: string;
  severity: 'positive' | 'warning' | 'danger' | 'info';
  title: string;
  message: string;
}

export interface PipelineStatus {
  pipeline_health: string;
  last_sync: string;
  data_quality: {
    status: string;
    total_checks: number;
    passed_checks: number;
    failed_checks: number;
    checks: Array<{ check_name: string; passed: boolean; details: string }>;
  };
  table_counts: Record<string, { clean_rows: number; raw_rows: number }>;
}

export interface FilterState {
  vendor: string;
  category: string;
  location: string;
  startDate: string;
  endDate: string;
}
