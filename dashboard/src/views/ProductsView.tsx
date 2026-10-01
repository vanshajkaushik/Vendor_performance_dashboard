import React from 'react';
import { AlertTriangle, TrendingUp, PackageCheck } from 'lucide-react';
import { CategoryData, PricingAnomaly } from '../types';
import { CategoryPieChart } from '../components/charts/CategoryPieChart';

interface ProductsViewProps {
  categories: CategoryData[];
  anomalies: PricingAnomaly[];
}

export const ProductsView: React.FC<ProductsViewProps> = ({ categories, anomalies }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <CategoryPieChart data={categories} />
        </div>

        {/* Category Performance Table */}
        <div className="lg:col-span-2 bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
          <h3 className="text-sm font-bold text-white tracking-wide mb-1">
            Category Profitability & Margin Contribution
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            Aggregated revenue, procurement spend, and gross margins across portfolio categories
          </p>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase text-[11px] bg-slate-900/40">
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3 text-center">Products</th>
                  <th className="py-2.5 px-3 text-right">Procurement Spend</th>
                  <th className="py-2.5 px-3 text-right">Sales Revenue</th>
                  <th className="py-2.5 px-3 text-right">Gross Profit</th>
                  <th className="py-2.5 px-3 text-right">Gross Margin</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {categories.map((c) => (
                  <tr key={c.category} className="hover:bg-slate-800/30">
                    <td className="py-3 px-3 font-semibold text-slate-200">{c.category}</td>
                    <td className="py-3 px-3 text-center text-slate-400 font-mono">{c.product_count}</td>
                    <td className="py-3 px-3 text-right font-mono text-amber-400">${c.procurement_spend.toLocaleString()}</td>
                    <td className="py-3 px-3 text-right font-mono text-sky-400">${c.sales_revenue.toLocaleString()}</td>
                    <td className="py-3 px-3 text-right font-mono text-emerald-400 font-semibold">${c.gross_profit.toLocaleString()}</td>
                    <td className="py-3 px-3 text-right font-mono text-emerald-300 font-bold">{c.gross_margin_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Pricing Anomalies Matrix */}
      <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
        <div className="flex items-center gap-2 mb-1">
          <AlertTriangle className="w-4 h-4 text-rose-400" />
          <h3 className="text-sm font-bold text-white tracking-wide">
            Automated Pricing Anomaly Detector (&gt;7% Benchmark Variance)
          </h3>
        </div>
        <p className="text-xs text-slate-400 mb-4">
          Identifies instances where supplier purchase prices deviate significantly from target unit costs
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-[11px] bg-slate-900/40">
                <th className="py-2.5 px-3">Product Name</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Supplier Name</th>
                <th className="py-2.5 px-3 text-right">Benchmark Cost</th>
                <th className="py-2.5 px-3 text-right">Avg Purchase Price</th>
                <th className="py-2.5 px-3 text-right">Variance %</th>
                <th className="py-2.5 px-3 text-right">Units Sourced</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {anomalies.map((a, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30">
                  <td className="py-2.5 px-3">
                    <div className="font-semibold text-slate-200">{a.product_name}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{a.product_id}</div>
                  </td>
                  <td className="py-2.5 px-3 text-slate-400">{a.category}</td>
                  <td className="py-2.5 px-3 text-slate-300 font-medium">{a.vendor_name}</td>
                  <td className="py-2.5 px-3 text-right font-mono text-slate-400">${a.unit_cost.toFixed(2)}</td>
                  <td className="py-2.5 px-3 text-right font-mono text-slate-200">${a.avg_purchase_price.toFixed(2)}</td>
                  <td className={`py-2.5 px-3 text-right font-mono font-semibold ${
                    a.price_variance_pct > 0 ? 'text-rose-400' : 'text-emerald-400'
                  }`}>
                    {a.price_variance_pct > 0 ? `+${a.price_variance_pct}%` : `${a.price_variance_pct}%`}
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono text-slate-400">{a.total_qty.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
