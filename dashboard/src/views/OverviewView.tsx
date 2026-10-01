import React from 'react';
import { DollarSign, ShoppingBag, TrendingUp, Users, Package, Award } from 'lucide-react';
import { KpiData, MonthlyTrend, VendorSummary, AutomatedInsight } from '../types';
import { KpiCard } from '../components/KpiCard';
import { InsightsBanner } from '../components/InsightsBanner';
import { TrendChart } from '../components/charts/TrendChart';
import { VendorRevenueBarChart } from '../components/charts/VendorRevenueBarChart';
import { GrossMarginBarChart } from '../components/charts/GrossMarginBarChart';
import { EfficiencyScatterPlot } from '../components/charts/EfficiencyScatterPlot';

interface OverviewViewProps {
  kpiData: KpiData | null;
  trends: MonthlyTrend[];
  vendors: VendorSummary[];
  insights: AutomatedInsight[];
  scatterData: any[];
  onSelectVendor: (id: string) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  kpiData,
  trends,
  vendors,
  insights,
  scatterData,
  onSelectVendor
}) => {
  const formatMillions = (val?: number) => val !== undefined ? `$${(val / 1_000_000).toFixed(2)}M` : '$0M';

  return (
    <div className="space-y-6">
      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <KpiCard
          title="Total Attributed Sales"
          value={formatMillions(kpiData?.total_sales)}
          subtitle={`${kpiData?.sales_volume.toLocaleString()} units sold`}
          badgeText="+14.2% YoY"
          badgePositive={true}
          icon={DollarSign}
          colorScheme="sky"
        />
        <KpiCard
          title="Procurement Spend"
          value={formatMillions(kpiData?.total_procurement)}
          subtitle={`${kpiData?.purchase_volume.toLocaleString()} units procured`}
          badgeText="Ratio: 0.45"
          badgePositive={true}
          icon={ShoppingBag}
          colorScheme="amber"
        />
        <KpiCard
          title="Gross Profit"
          value={formatMillions(kpiData?.gross_profit)}
          subtitle="Net value capture"
          badgeText="High Capture"
          badgePositive={true}
          icon={TrendingUp}
          colorScheme="emerald"
        />
        <KpiCard
          title="Gross Margin %"
          value={`${kpiData?.gross_margin_pct || 0}%`}
          subtitle="Target threshold: >45%"
          badgeText="Above Target"
          badgePositive={true}
          icon={Award}
          colorScheme="indigo"
        />
        <KpiCard
          title="Active Suppliers"
          value={kpiData?.active_vendors || 0}
          subtitle="Across 8 regions"
          badgeText="100% On Contract"
          badgePositive={true}
          icon={Users}
          colorScheme="purple"
        />
        <KpiCard
          title="Avg Vendor VPS"
          value={`${kpiData?.avg_vendor_performance_score || 0}/100`}
          subtitle="Tier 2 Average"
          badgeText="Healthy Index"
          badgePositive={true}
          icon={Package}
          colorScheme="sky"
        />
      </div>

      {/* Automated NLP Insights */}
      <InsightsBanner insights={insights} />

      {/* Main Visualizations Grid */}
      <div className="grid grid-cols-1 gap-6">
        <TrendChart data={trends} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <VendorRevenueBarChart vendors={vendors} onSelectVendor={onSelectVendor} />
        <GrossMarginBarChart vendors={vendors} onSelectVendor={onSelectVendor} />
      </div>

      <div>
        <EfficiencyScatterPlot data={scatterData} onSelectVendor={onSelectVendor} />
      </div>
    </div>
  );
};
