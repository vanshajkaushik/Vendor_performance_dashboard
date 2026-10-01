import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts';
import { MonthlyTrend } from '../../types';

interface TrendChartProps {
  data: MonthlyTrend[];
}

export const TrendChart: React.FC<TrendChartProps> = ({ data }) => {
  const formatMillions = (val: number) => `$${(val / 1_000_000).toFixed(1)}M`;

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl text-xs space-y-1">
          <div className="font-bold text-slate-200 border-b border-slate-800 pb-1">{label}</div>
          <div className="text-sky-400">
            Sales Revenue: ${payload[0]?.value?.toLocaleString()}
          </div>
          <div className="text-amber-400">
            Procurement Spend: ${payload[1]?.value?.toLocaleString()}
          </div>
          <div className="text-emerald-400 font-semibold">
            Gross Margin: {payload[2]?.value}%
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-white tracking-wide">
            Monthly Procurement Spend vs Sales Revenue
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Evaluates revenue expansion against procurement capital deployment with gross margin trend
          </p>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="month" stroke="#64748b" tick={{ fontSize: 11 }} />
            <YAxis yAxisId="left" stroke="#64748b" tickFormatter={formatMillions} tick={{ fontSize: 11 }} />
            <YAxis yAxisId="right" orientation="right" stroke="#10b981" unit="%" tick={{ fontSize: 11 }} domain={[20, 80]} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 11, paddingTop: 10 }} />
            <Bar yAxisId="left" dataKey="sales_revenue" name="Sales Revenue" fill="#0284c7" radius={[4, 4, 0, 0]} />
            <Bar yAxisId="left" dataKey="procurement_spend" name="Procurement Spend" fill="#d97706" radius={[4, 4, 0, 0]} />
            <Line yAxisId="right" type="monotone" dataKey="gross_margin_pct" name="Gross Margin %" stroke="#10b981" strokeWidth={2.5} dot={{ r: 3 }} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
