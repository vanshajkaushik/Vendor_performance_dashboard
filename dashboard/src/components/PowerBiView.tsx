import React from 'react';
import { Layers, FileText, Database, RefreshCw, BarChart2, CheckCircle2, ShieldCheck, Zap } from 'lucide-react';

export const PowerBiView: React.FC = () => {
  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-amber-500/10 via-amber-600/10 to-transparent border border-amber-500/20 rounded-2xl p-6 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-amber-400 font-semibold text-xs tracking-wider uppercase mb-1">
              <BarChart2 className="w-4 h-4" />
              <span>Enterprise Power BI Integration</span>
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Power BI Deliverables & Star Schema Model</h2>
            <p className="text-slate-400 text-sm mt-1 max-w-2xl">
              Production-ready Power BI template (<code className="text-amber-300 font-mono text-xs">.pbit</code> / <code className="text-amber-300 font-mono text-xs">.pbix</code>) engineered on Kimberly-Clark & Microsoft best-practice Star Schema, featuring 14 dynamic DAX measures and 5 interactive report pages.
            </p>
          </div>
          <div className="flex items-center space-x-3 shrink-0">
            <div className="px-4 py-2 bg-amber-500/20 border border-amber-500/40 rounded-xl text-amber-300 font-mono text-xs flex items-center space-x-2">
              <Database className="w-4 h-4" />
              <span>Model: Star Schema (7 Tables)</span>
            </div>
          </div>
        </div>
      </div>

      {/* 5 Report Pages Overview */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
          <Layers className="w-5 h-5 text-blue-400" />
          <span>Interactive Power BI Report Suite (5 Pages)</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400">Page 1</span>
              <span className="text-xs text-slate-500 font-mono">Executive</span>
            </div>
            <h4 className="text-base font-bold text-white">Executive Spend & Vendor Overview</h4>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Total procurement spend cards, month-over-month variance, active vendor count, spend by category donut, and top 10 vendor bar chart with Pareto cumulative curve.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400">Page 2</span>
              <span className="text-xs text-slate-500 font-mono">Operations</span>
            </div>
            <h4 className="text-base font-bold text-white">Delivery Performance & Reliability</h4>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              On-Time In-Full (OTIF %) gauge, lead time variance scatter plot (quoted vs actual days), quality defect rate by category, and bottom 10 at-risk delivery vendors.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-400">Page 3</span>
              <span className="text-xs text-slate-500 font-mono">Intelligence</span>
            </div>
            <h4 className="text-base font-bold text-white">Pricing Intelligence & Cost Variance</h4>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Purchase price vs catalog benchmark variance (PPV), unit cost drift heatmap across procurement quarters, gross margin contribution, and outlier flags.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-400">Page 4</span>
              <span className="text-xs text-slate-500 font-mono">Governance</span>
            </div>
            <h4 className="text-base font-bold text-white">Vendor Risk & Concentration Matrix</h4>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Herfindahl-Hirschman Index (HHI) gauge, single-source dependency alert table (&gt;35% category spend), vendor tier distribution, and at-risk contract matrix.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-400">Page 5</span>
              <span className="text-xs text-slate-500 font-mono">Drill-Through</span>
            </div>
            <h4 className="text-base font-bold text-white">Vendor 360° Scorecard (Drill-Through)</h4>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Target destination for any vendor drill-through. Complete historical PO log, 12-month delivery trend line, product catalog breakdown, and composite VPS radar breakdown.
            </p>
          </div>
        </div>
      </div>

      {/* DAX Measures Reference & Architecture */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center space-x-2 text-white font-semibold">
            <FileText className="w-5 h-5 text-amber-400" />
            <span>Key DAX Measures Reference</span>
          </div>
          <p className="text-xs text-slate-400">
            Exported to <code className="text-amber-300 font-mono">powerbi/dax/measures.dax</code> for automated Power BI / Tabular Editor import:
          </p>
          <div className="space-y-3 font-mono text-xs">
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-blue-400 font-semibold">[Total Spend]</span> = SUM(FactPurchases[Total_Amount])
            </div>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-blue-400 font-semibold">[OTIF %]</span> = DIVIDE(CALCULATE(COUNTROWS(FactPurchases), FactPurchases[Delivery_Status] = "ON_TIME" && FactPurchases[Defect_Rate] &lt;= 0.01), COUNTROWS(FactPurchases), 0)
            </div>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-blue-400 font-semibold">[Vendor Performance Score]</span> = [OTIF %]*30 + (1 - [Defect Rate %])*25 + (1 - ABS([Price Variance %]))*20 + (1 - [Lead Time Variance %])*15 + (1 - [Spend Concentration %])*10
            </div>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-blue-400 font-semibold">[Vendor Tier]</span> = SWITCH(TRUE(), [Vendor Performance Score] &gt;= 85, "Strategic Partner", [Vendor Performance Score] &gt;= 70, "Preferred", [Vendor Performance Score] &gt;= 50, "Standard", "At-Risk")
            </div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center space-x-2 text-white font-semibold">
            <Zap className="w-5 h-5 text-emerald-400" />
            <span>Star Schema & Refresh Procedure</span>
          </div>
          <div className="space-y-3 text-xs text-slate-300">
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <p className="font-semibold text-white mb-1">1. Model Structure (1-to-Many Relationships):</p>
              <ul className="list-disc list-inside text-slate-400 space-y-1">
                <li><code className="text-blue-300">DimVendor[Vendor_ID]</code> 1:* <code className="text-blue-300">FactPurchases[Vendor_ID]</code></li>
                <li><code className="text-blue-300">DimProduct[Product_ID]</code> 1:* <code className="text-blue-300">FactPurchases[Product_ID]</code> & <code className="text-blue-300">FactSales</code></li>
                <li><code className="text-blue-300">DimDate[Date]</code> 1:* <code className="text-blue-300">FactPurchases[PO_Date]</code> & <code className="text-blue-300">FactSales[Sales_Date]</code></li>
                <li><code className="text-blue-300">DimCategory[Category_ID]</code> 1:* <code className="text-blue-300">DimProduct[Category_ID]</code></li>
              </ul>
            </div>

            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <p className="font-semibold text-white mb-1">2. How to Open & Refresh:</p>
              <ol className="list-decimal list-inside text-slate-400 space-y-1">
                <li>Open <code className="text-amber-300">powerbi/Vendor_Performance_Dashboard.pbit</code> in Microsoft Power BI Desktop.</li>
                <li>When prompted for parameter <code className="text-amber-300">DataFolderPath</code>, enter project root or <code className="text-amber-300">.../data/processed</code>.</li>
                <li>Power Query M script will automatically parse the 7 clean Star Schema CSV tables and build the data model.</li>
                <li>Click <strong>Refresh</strong> whenever the Python ETL pipeline completes.</li>
              </ol>
            </div>

            <div className="p-3 bg-emerald-950/20 border border-emerald-500/20 rounded-xl flex items-center space-x-2 text-emerald-300">
              <ShieldCheck className="w-5 h-5 shrink-0" />
              <span>All 7 CSV datasets, M queries, and DAX measures match 100% with the SQLite & FastAPI production layer.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
