import React from 'react';
import { Sparkles, TrendingUp, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { AutomatedInsight } from '../types';

interface InsightsBannerProps {
  insights: AutomatedInsight[];
}

export const InsightsBanner: React.FC<InsightsBannerProps> = ({ insights }) => {
  if (!insights || insights.length === 0) return null;

  const getIcon = (type: string) => {
    switch (type) {
      case 'revenue':
      case 'margin':
        return <TrendingUp className="w-4 h-4 text-emerald-400" />;
      case 'efficiency':
      case 'pricing':
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      case 'savings':
        return <CheckCircle className="w-4 h-4 text-sky-400" />;
      default:
        return <Info className="w-4 h-4 text-slate-400" />;
    }
  };

  const getBadgeStyle = (severity: string) => {
    switch (severity) {
      case 'positive':
        return 'bg-emerald-950/40 border-emerald-500/30 text-emerald-200';
      case 'warning':
        return 'bg-amber-950/40 border-amber-500/30 text-amber-200';
      case 'danger':
        return 'bg-rose-950/40 border-rose-500/30 text-rose-200';
      default:
        return 'bg-sky-950/40 border-sky-500/30 text-sky-200';
    }
  };

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 shadow-lg shadow-black/20 mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="w-4 h-4 text-amber-400" />
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
          Automated Strategic Insights Engine (NLP Computed)
        </h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {insights.slice(0, 3).map((item, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-lg border flex gap-3 items-start text-xs ${getBadgeStyle(item.severity)}`}
          >
            <div className="mt-0.5 shrink-0">{getIcon(item.type)}</div>
            <div>
              <div className="font-semibold mb-0.5 tracking-tight">{item.title}</div>
              <div
                className="leading-relaxed opacity-90"
                dangerouslySetInnerHTML={{ __html: item.message }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
