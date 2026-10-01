import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell
} from 'recharts';
import { VendorSummary } from '../../types';

interface GrossMarginBarChartProps {
  vendors: VendorSummary[];
  onSelectVendor: (id: string) => void;
}

export const GrossMarginBarChart: React.FC<GrossMarginBarChartProps> = ({ vendors, onSelectVendor }) => {
  const sorted = [...vendors]
    .sort((a, b) => b.gross_margin_pct - a.gross_margin_pct)
    .slice(0, 10);

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
      <div className="mb-4">
        <h3 className="text-sm font-bold text-white tracking-wide">
          Gross Profit Margin % by Top Suppliers
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Benchmark margin capture: green indicates high profit margins (&gt;55%), amber indicates moderate
        </p>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={sorted}
            margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
            onClick={(e: any) => {
              if (e && e.activePayload && e.activePayload[0]) {
                onSelectVendor(e.activePayload[0].payload.vendor_id);
              }
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
            <XAxis type="number" stroke="#64748b" unit="%" domain={[0, 75]} tick={{ fontSize: 11 }} />
            <YAxis
              type="category"
              dataKey="vendor_name"
              stroke="#94a3b8"
              tick={{ fontSize: 11 }}
              width={140}
            />
            <Tooltip
              formatter={(val: number) => [`${val}%`, 'Gross Margin']}
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, fontSize: 12 }}
            />
            <Bar dataKey="gross_margin_pct" radius={[0, 4, 4, 0]} className="cursor-pointer">
              {sorted.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.gross_margin_pct >= 55 ? '#10b981' : entry.gross_margin_pct >= 45 ? '#0284c7' : '#f59e0b'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
