import React, { useState } from 'react';
import { Search, ChevronRight, PlusCircle, Upload, Building2 } from 'lucide-react';
import { VendorSummary } from '../types';
import { AddVendorModal } from '../components/AddVendorModal';
import { ImportCsvModal } from '../components/ImportCsvModal';

interface VendorsViewProps {
  vendors: VendorSummary[];
  onSelectVendor: (id: string) => void;
  onRefresh?: () => void;
}

export const VendorsView: React.FC<VendorsViewProps> = ({ vendors, onSelectVendor, onRefresh }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [tierFilter, setTierFilter] = useState('all');
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isImportOpen, setIsImportOpen] = useState(false);

  const filtered = vendors.filter((v) => {
    const matchesSearch =
      v.vendor_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      v.vendor_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      v.vendor_category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTier = tierFilter === 'all' || v.performance_tier.toLowerCase().includes(tierFilter.toLowerCase());
    return matchesSearch && matchesTier;
  });

  const getTierBadge = (tier: string) => {
    if (tier.includes('Tier 1') || tier.includes('Strategic')) {
      return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">Tier 1: Strategic</span>;
    }
    if (tier.includes('Tier 2') || tier.includes('Preferred')) {
      return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-sky-500/15 text-sky-400 border border-sky-500/30">Tier 2: Preferred</span>;
    }
    if (tier.includes('Tier 3') || tier.includes('Standard') || tier.includes('Operational')) {
      return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">Tier 3: Standard</span>;
    }
    if (tier.includes('New') || tier.includes('Insufficient')) {
      return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-500/15 text-purple-300 border border-purple-500/30">New / Insufficient Data</span>;
    }
    return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">Tier 4: At-Risk</span>;
  };

  return (
    <div className="space-y-6">
      <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-white tracking-wide">
              Vendor Scorecard & Strategic Directory
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Comprehensive ranking based on weighted VPS score (OTIF, Defect Rate, Price Variance, Lead Time, Concentration)
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            <div className="relative flex-1 md:w-56">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search vendor name or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-[#0f172a] border border-slate-700/80 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-sky-500"
              />
            </div>

            <select
              value={tierFilter}
              onChange={(e) => setTierFilter(e.target.value)}
              className="bg-[#0f172a] border border-slate-700/80 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
            >
              <option value="all">All Tiers</option>
              <option value="Strategic">Tier 1: Strategic</option>
              <option value="Preferred">Tier 2: Preferred</option>
              <option value="Standard">Tier 3: Standard</option>
              <option value="At-Risk">Tier 4: At-Risk</option>
              <option value="New">New / Insufficient Data</option>
            </select>

            <button
              onClick={() => setIsImportOpen(true)}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-medium rounded-lg transition flex items-center space-x-1.5"
            >
              <Upload className="w-3.5 h-3.5 text-purple-400" />
              <span>Import CSV</span>
            </button>

            <button
              onClick={() => setIsAddOpen(true)}
              className="px-3 py-1.5 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-lg transition flex items-center space-x-1.5 shadow-md shadow-sky-500/20"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Add Vendor</span>
            </button>
          </div>
        </div>

        {/* Vendors Table */}
        <div className="overflow-x-auto mt-5">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase font-semibold text-[11px] bg-slate-900/40">
                <th className="py-3 px-4">Rank / Supplier</th>
                <th className="py-3 px-3">Category</th>
                <th className="py-3 px-3">Region</th>
                <th className="py-3 px-3 text-right">Procurement Spend</th>
                <th className="py-3 px-3 text-right">Attributed Revenue</th>
                <th className="py-3 px-3 text-right">Gross Margin</th>
                <th className="py-3 px-3 text-right">Price Var</th>
                <th className="py-3 px-3 text-center">VPS Score</th>
                <th className="py-3 px-3 text-center">Tier Badge</th>
                <th className="py-3 px-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((v, idx) => (
                <tr
                  key={v.vendor_id}
                  className="hover:bg-slate-800/40 transition-colors group cursor-pointer"
                  onClick={() => onSelectVendor(v.vendor_id)}
                >
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-slate-500 text-[11px] w-5">#{idx + 1}</span>
                      <div>
                        <div className="font-semibold text-slate-200 group-hover:text-sky-400 transition-colors">
                          {v.vendor_name}
                        </div>
                        <div className="text-[10px] text-slate-500 font-mono">{v.vendor_id} • Rating: {v.rating ?? '—'}★</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-3 text-slate-300">{v.vendor_category || 'General'}</td>
                  <td className="py-3 px-3 text-slate-400">{v.location || '—'}</td>
                  <td className="py-3 px-3 text-right font-mono text-amber-400">
                    ${(v.total_procurement_cost || 0).toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-sky-400">
                    ${(v.total_revenue || 0).toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-right font-mono font-semibold text-emerald-400">
                    {v.gross_margin_pct ?? 0}%
                  </td>
                  <td className={`py-3 px-3 text-right font-mono ${(v.price_variance_pct || 0) < 0 ? 'text-emerald-400' : (v.price_variance_pct || 0) > 8 ? 'text-rose-400' : 'text-slate-300'}`}>
                    {(v.price_variance_pct || 0) > 0 ? `+${v.price_variance_pct}%` : `${v.price_variance_pct || 0}%`}
                  </td>
                  <td className="py-3 px-3 text-center">
                    {v.vendor_performance_score === null || v.vendor_performance_score === undefined ? (
                      <span className="text-slate-500 font-mono">N/A</span>
                    ) : (
                      <div className="inline-flex items-center justify-center font-bold px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20 font-mono">
                        {v.vendor_performance_score}
                      </div>
                    )}
                  </td>
                  <td className="py-3 px-3 text-center">{getTierBadge(v.performance_tier)}</td>
                  <td className="py-3 px-3 text-center">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectVendor(v.vendor_id);
                      }}
                      className="inline-flex items-center gap-1 text-sky-400 hover:text-sky-300 font-medium text-[11px]"
                    >
                      Details <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <AddVendorModal
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        onVendorAdded={() => {
          if (onRefresh) onRefresh();
          setIsAddOpen(false);
        }}
      />

      <ImportCsvModal
        isOpen={isImportOpen}
        onClose={() => setIsImportOpen(false)}
        onImportComplete={() => {
          if (onRefresh) onRefresh();
          setIsImportOpen(false);
        }}
      />
    </div>
  );
};
