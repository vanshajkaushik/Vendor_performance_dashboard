import React from 'react';
import {
  LayoutDashboard,
  Building2,
  Package,
  ShoppingCart,
  LineChart,
  Database,
  Layers,
  Sparkles,
  BarChart2
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const navItems = [
    { id: 'overview', label: 'Executive Overview', icon: LayoutDashboard },
    { id: 'vendors', label: 'Vendor Scorecard', icon: Building2 },
    { id: 'products', label: 'Products & Pricing', icon: Package },
    { id: 'procurement', label: 'Procurement & Stock', icon: ShoppingCart },
    { id: 'analytics', label: 'Efficiency & Matrix', icon: LineChart },
    { id: 'pipeline', label: 'ETL & Data Quality', icon: Database },
    { id: 'powerbi', label: 'Power BI Deliverables', icon: BarChart2, highlight: true },
  ];

  return (
    <aside className="w-64 bg-[#0d1322] border-r border-slate-800/80 flex flex-col justify-between shrink-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-800/60 gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <Layers className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-sm tracking-wide text-white flex items-center gap-1.5">
              POWER ANALYTICS
              <span className="text-[10px] px-1.5 py-0.2 bg-sky-500/20 text-sky-400 font-semibold rounded border border-sky-500/30">PRO</span>
            </div>
            <div className="text-xs text-slate-400 font-medium">Vendor Performance BI</div>
          </div>
        </div>

        {/* Navigation Section */}
        <div className="p-3">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2">
            Analytics Views
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? item.highlight
                        ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30 shadow-sm'
                        : 'bg-sky-500/15 text-sky-400 border border-sky-500/30 shadow-sm'
                      : item.highlight
                        ? 'text-amber-400/90 hover:text-amber-300 hover:bg-amber-500/10'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? (item.highlight ? 'text-amber-400' : 'text-sky-400') : item.highlight ? 'text-amber-400/80' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/60">
        <div className="bg-slate-800/40 rounded-lg p-3 border border-slate-700/40">
          <div className="flex items-center gap-2 text-xs font-semibold text-sky-400 mb-1">
            <Sparkles className="w-3.5 h-3.5" /> Live Data Pipeline
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Star Schema engine loaded with 33,000+ records.
          </p>
          <div className="mt-2 text-[10px] text-slate-400 font-mono flex items-center justify-between">
            <span>Status: Active</span>
            <span className="text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> 100% Valid
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};
