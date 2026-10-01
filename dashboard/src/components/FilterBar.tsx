import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';
import { FilterState, VendorSummary } from '../types';

interface FilterBarProps {
  filters: FilterState;
  setFilters: React.Dispatch<React.SetStateAction<FilterState>>;
  vendors: VendorSummary[];
}

export const FilterBar: React.FC<FilterBarProps> = ({ filters, setFilters, vendors }) => {
  const categories = ['Electronics', 'Industrial Machinery', 'Raw Materials', 'Office Supplies', 'Packaging'];
  const locations = ['US-West', 'US-East', 'US-Midwest', 'US-South', 'Germany', 'Japan', 'Taiwan', 'Canada'];

  const handleReset = () => {
    setFilters({
      vendor: 'all',
      category: 'all',
      location: 'all',
      startDate: '',
      endDate: ''
    });
  };

  return (
    <div className="bg-[#111827] border border-slate-800/80 rounded-xl p-4 shadow-lg shadow-black/20 mb-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          <Filter className="w-4 h-4 text-sky-400" />
          <span>Interactive Power BI Slicers</span>
        </div>

        <button
          onClick={handleReset}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" /> Reset Filters
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mt-3">
        {/* Category Slicer */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Vendor Category</label>
          <select
            value={filters.category}
            onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
            className="w-full bg-[#0f172a] border border-slate-700/80 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500 transition-colors"
          >
            <option value="all">All Categories (5)</option>
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Location Slicer */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Geographic Region</label>
          <select
            value={filters.location}
            onChange={(e) => setFilters(prev => ({ ...prev, location: e.target.value }))}
            className="w-full bg-[#0f172a] border border-slate-700/80 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500 transition-colors"
          >
            <option value="all">All Regions (8)</option>
            {locations.map((loc) => (
              <option key={loc} value={loc}>{loc}</option>
            ))}
          </select>
        </div>

        {/* Vendor Dropdown */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Specific Supplier</label>
          <select
            value={filters.vendor}
            onChange={(e) => setFilters(prev => ({ ...prev, vendor: e.target.value }))}
            className="w-full bg-[#0f172a] border border-slate-700/80 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500 transition-colors"
          >
            <option value="all">All Suppliers (25)</option>
            {vendors.map((v) => (
              <option key={v.vendor_id} value={v.vendor_id}>
                {v.vendor_name} ({v.vendor_id})
              </option>
            ))}
          </select>
        </div>

        {/* Quick Date Presets */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Date Preset</label>
          <select
            onChange={(e) => {
              const val = e.target.value;
              if (val === 'all') setFilters(prev => ({ ...prev, startDate: '', endDate: '' }));
              else if (val === '2024') setFilters(prev => ({ ...prev, startDate: '2024-01-01', endDate: '2024-12-31' }));
              else if (val === '2025') setFilters(prev => ({ ...prev, startDate: '2025-01-01', endDate: '2025-12-31' }));
              else if (val === 'q4') setFilters(prev => ({ ...prev, startDate: '2025-10-01', endDate: '2025-12-31' }));
            }}
            className="w-full bg-[#0f172a] border border-slate-700/80 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500 transition-colors"
          >
            <option value="all">Full 24-Month Horizon</option>
            <option value="2025">FY 2025</option>
            <option value="2024">FY 2024</option>
            <option value="q4">Q4 Peak Surge (2025)</option>
          </select>
        </div>

        {/* Active Filter Indicator */}
        <div className="flex items-end">
          <div className="w-full bg-slate-800/40 rounded-lg border border-slate-700/40 px-3 py-1.5 text-xs text-slate-300 flex items-center justify-between">
            <span className="text-slate-400">Active Slicers:</span>
            <span className="font-semibold text-sky-400">
              {[filters.category, filters.location, filters.vendor].filter(x => x !== 'all').length + (filters.startDate ? 1 : 0)} Applied
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
