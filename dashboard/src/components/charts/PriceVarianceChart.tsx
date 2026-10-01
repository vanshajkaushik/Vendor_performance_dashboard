import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
  Cell
} from 'recharts';
import { VendorSummary } from '../../types';

interface PriceVarianceChartProps {
  vendors: VendorSummary[];
}

export const PriceVarianceChart: React.FC<PriceVarianceChartProps> = ({ vendors }) => {
  const sorted = [...vendors].sort((a, b) => a.price_variance_pct - b.price_variance_pct);

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
      <div className="mb-4">
        <h3 className="text-sm font-bold text-white tracking-wide">
          Vendor Purchase Price Variance vs Benchmark
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Negative values indicate discounts/cost advantage; positive values indicate pricing premiums
        </p>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={sorted} margin={{ top: 10, right: 10, left: -20, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis
              dataKey="vendor_name"
              stroke="#64748b"
              angle={-45} textAnchor="end" tick={{ fontSize: 9 }}
              interval={0}
            />
            <YAxis stroke="#64748b" unit="%" tick={{ fontSize: 11 }} />
            <Tooltip
              formatter={(val: number) => [`${val}%`, 'Price Variance']}
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, fontSize: 12 }}
            />
            <ReferenceLine y={0} stroke="#475569" />
            <Bar dataKey="price_variance_pct">
              {sorted.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.price_variance_pct < 0 ? '#10b981' : entry.price_variance_pct > 8 ? '#f43f5e' : '#f59e0b'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
