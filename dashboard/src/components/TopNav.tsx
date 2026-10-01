import React from 'react';
import { RefreshCw, ShieldCheck, Database, Calendar } from 'lucide-react';

interface TopNavProps {
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const TopNav: React.FC<TopNavProps> = ({ onRefresh, isRefreshing }) => {
  return (
    <header className="h-16 bg-[#0f172a]/90 backdrop-blur border-b border-slate-800 flex items-center justify-between px-6 z-10 sticky top-0">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <span className="text-slate-500 font-medium">Workspace</span>
          <span>/</span>
          <span className="text-slate-200 font-semibold">Vendor Performance & Sourcing Intelligence</span>
        </div>
        <span className="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <ShieldCheck className="w-3.5 h-3.5" /> 3NF SQL Normalized
        </span>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-800/60 px-3 py-1.5 rounded-md border border-slate-700/60">
          <Calendar className="w-3.5 h-3.5 text-sky-400" />
          <span>Time Horizon: 2024 - 2025</span>
        </div>

        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold shadow-md shadow-sky-600/20 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
          {isRefreshing ? 'Refreshing...' : 'Refresh Slicers'}
        </button>
      </div>
    </header>
  );
};
