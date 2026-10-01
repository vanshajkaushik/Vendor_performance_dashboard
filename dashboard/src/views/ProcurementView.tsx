import React from 'react';
import { AlertCircle, CheckCircle2, ShieldAlert, Package, Layers } from 'lucide-react';
import { InventoryItem, VendorSummary } from '../types';
import { PriceVarianceChart } from '../components/charts/PriceVarianceChart';

interface ProcurementViewProps {
  inventory: InventoryItem[];
  vendors: VendorSummary[];
}

export const ProcurementView: React.FC<ProcurementViewProps> = ({ inventory, vendors }) => {
  const criticalCount = inventory.filter((i) => i.status.includes('CRITICAL')).length;
  const warningCount = inventory.filter((i) => i.status.includes('WARNING')).length;
  const healthyCount = inventory.filter((i) => i.status.includes('HEALTHY')).length;

  return (
    <div className="space-y-6">
      {/* Inventory Health Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 shadow-lg flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20 flex items-center justify-center shrink-0">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">{criticalCount} Items</div>
            <div className="text-xs text-rose-400 font-semibold">Stockout Risk (Below Safety Stock)</div>
          </div>
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 shadow-lg flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center shrink-0">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">{warningCount} Items</div>
            <div className="text-xs text-amber-400 font-semibold">Reorder Required (Below Reorder Point)</div>
          </div>
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 shadow-lg flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center shrink-0">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">{healthyCount} Items</div>
            <div className="text-xs text-emerald-400 font-semibold">Healthy Inventory Stock</div>
          </div>
        </div>
      </div>

      {/* Supplier Price Variance Chart */}
      <PriceVarianceChart vendors={vendors} />

      {/* Inventory Detail Status Table */}
      <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
        <h3 className="text-sm font-bold text-white tracking-wide mb-1">
          Inventory Status & Reorder Replenishment Log
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Current stock levels, safety buffer thresholds, and assigned primary replenishment vendor
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-[11px] bg-slate-900/40">
                <th className="py-2.5 px-3">Product Name</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Supplier</th>
                <th className="py-2.5 px-3 text-right">Current Stock</th>
                <th className="py-2.5 px-3 text-right">Reorder Level</th>
                <th className="py-2.5 px-3 text-right">Inventory Value</th>
                <th className="py-2.5 px-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {inventory.slice(0, 20).map((inv, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30">
                  <td className="py-2.5 px-3 font-semibold text-slate-200">{inv.product_name}</td>
                  <td className="py-2.5 px-3 text-slate-400">{inv.category}</td>
                  <td className="py-2.5 px-3 text-slate-300">{inv.vendor_name}</td>
                  <td className="py-2.5 px-3 text-right font-mono text-slate-200">{inv.stock_quantity.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-right font-mono text-slate-400">{inv.reorder_level.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-right font-mono text-amber-400">${inv.inventory_value.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                      inv.status.includes('CRITICAL')
                        ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                        : inv.status.includes('WARNING')
                        ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                        : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                    }`}>
                      {inv.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
