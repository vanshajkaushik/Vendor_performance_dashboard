import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { TopNav } from './components/TopNav';
import { FilterBar } from './components/FilterBar';
import { OverviewView } from './views/OverviewView';
import { VendorsView } from './views/VendorsView';
import { ProductsView } from './views/ProductsView';
import { ProcurementView } from './views/ProcurementView';
import { PipelineView } from './views/PipelineView';
import { VendorDetailModal } from './views/VendorDetailModal';
import { EfficiencyScatterPlot } from './components/charts/EfficiencyScatterPlot';
import { PowerBiView } from './components/PowerBiView';
import {
  KpiData,
  MonthlyTrend,
  VendorSummary,
  CategoryData,
  PricingAnomaly,
  InventoryItem,
  AutomatedInsight,
  PipelineStatus,
  FilterState
} from './types';
import {
  fetchKpis,
  fetchTrends,
  fetchVendors,
  fetchCategories,
  fetchPricingAnomalies,
  fetchInventory,
  fetchInsights,
  fetchScatter,
  fetchPipelineStatus
} from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [filters, setFilters] = useState<FilterState>({
    vendor: 'all',
    category: 'all',
    location: 'all',
    startDate: '',
    endDate: ''
  });

  const [kpiData, setKpiData] = useState<KpiData | null>(null);
  const [trends, setTrends] = useState<MonthlyTrend[]>([]);
  const [vendors, setVendors] = useState<VendorSummary[]>([]);
  const [categories, setCategories] = useState<CategoryData[]>([]);
  const [anomalies, setAnomalies] = useState<PricingAnomaly[]>([]);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [insights, setInsights] = useState<AutomatedInsight[]>([]);
  const [scatterData, setScatterData] = useState<any[]>([]);
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(null);

  const [selectedVendorId, setSelectedVendorId] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  const loadAllData = async () => {
    setIsRefreshing(true);
    try {
      const [
        kpisRes,
        trendsRes,
        vendorsRes,
        catRes,
        anomRes,
        invRes,
        insRes,
        scatRes,
        pipeRes
      ] = await Promise.all([
        fetchKpis(filters),
        fetchTrends(filters),
        fetchVendors(filters),
        fetchCategories(),
        fetchPricingAnomalies(),
        fetchInventory(),
        fetchInsights(),
        fetchScatter(),
        fetchPipelineStatus()
      ]);

      setKpiData(kpisRes);
      setTrends(trendsRes);
      setVendors(vendorsRes);
      setCategories(catRes);
      setAnomalies(anomRes);
      setInventory(invRes);
      setInsights(insRes);
      setScatterData(scatRes);
      setPipelineStatus(pipeRes);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setIsRefreshing(false);
      setInitialLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [filters]);

  return (
    <div className="flex h-screen bg-[#0b0f19] text-slate-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Workspace */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopNav onRefresh={loadAllData} isRefreshing={isRefreshing} />

        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Global Slicers */}
            {activeTab !== 'powerbi' && activeTab !== 'pipeline' && (
              <FilterBar filters={filters} setFilters={setFilters} vendors={vendors} />
            )}

            {initialLoading ? (
              <div className="h-96 flex items-center justify-center text-slate-400">
                <div className="flex flex-col items-center gap-3">
                  <div className="w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-xs font-semibold uppercase tracking-wider">
                    Querying Relational Database & Slicers...
                  </span>
                </div>
              </div>
            ) : (
              <>
                {activeTab === 'overview' && (
                  <OverviewView
                    kpiData={kpiData}
                    trends={trends}
                    vendors={vendors}
                    insights={insights}
                    scatterData={scatterData}
                    onSelectVendor={(id) => setSelectedVendorId(id)}
                  />
                )}

                {activeTab === 'vendors' && (
                  <VendorsView
                    vendors={vendors}
                    onSelectVendor={(id) => setSelectedVendorId(id)}
                    onRefresh={loadAllData}
                  />
                )}

                {activeTab === 'products' && (
                  <ProductsView
                    categories={categories}
                    anomalies={anomalies}
                  />
                )}

                {activeTab === 'procurement' && (
                  <ProcurementView
                    inventory={inventory}
                    vendors={vendors}
                  />
                )}

                {activeTab === 'analytics' && (
                  <div className="space-y-6">
                    <EfficiencyScatterPlot
                      data={scatterData}
                      onSelectVendor={(id) => setSelectedVendorId(id)}
                    />
                  </div>
                )}

                {activeTab === 'pipeline' && (
                  <PipelineView status={pipelineStatus} />
                )}

                {activeTab === 'powerbi' && (
                  <PowerBiView />
                )}
              </>
            )}
          </div>
        </main>
      </div>

      {/* Vendor Drill-Down Modal */}
      <VendorDetailModal
        vendorId={selectedVendorId}
        onClose={() => setSelectedVendorId(null)}
      />
    </div>
  );
}
