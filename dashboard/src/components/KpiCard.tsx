import React from 'react';
import { LucideIcon } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  badgeText?: string;
  badgePositive?: boolean;
  icon: LucideIcon;
  colorScheme?: 'sky' | 'emerald' | 'amber' | 'indigo' | 'purple';
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  subtitle,
  badgeText,
  badgePositive = true,
  icon: Icon,
  colorScheme = 'sky'
}) => {
  const colorStyles = {
    sky: 'border-l-4 border-l-sky-500 text-sky-400 bg-sky-500/10',
    emerald: 'border-l-4 border-l-emerald-500 text-emerald-400 bg-emerald-500/10',
    amber: 'border-l-4 border-l-amber-500 text-amber-400 bg-amber-500/10',
    indigo: 'border-l-4 border-l-indigo-500 text-indigo-400 bg-indigo-500/10',
    purple: 'border-l-4 border-l-purple-500 text-purple-400 bg-purple-500/10'
  };

  return (
    <div className={`bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20 hover:border-slate-700 transition-all ${colorStyles[colorScheme]}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</span>
        <div className={`p-2 rounded-lg ${colorStyles[colorScheme].split(' ')[2]} text-inherit`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-3">
        <div className="text-2xl lg:text-3xl font-bold tracking-tight text-white">{value}</div>
      </div>

      <div className="mt-2 flex items-center justify-between text-xs">
        {subtitle && <span className="text-slate-400 font-medium">{subtitle}</span>}
        {badgeText && (
          <span className={`px-2 py-0.5 rounded-full font-semibold ${
            badgePositive
              ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
              : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
          }`}>
            {badgeText}
          </span>
        )}
      </div>
    </div>
  );
};
