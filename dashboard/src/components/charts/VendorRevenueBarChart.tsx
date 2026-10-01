import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { VendorSummary } from '../../types';

interface VendorRevenueBarChartProps {
  vendors: VendorSummary[];
  onSelectVendor: (id: string) => void;
}

export const VendorRevenueBarChart: React.FC<VendorRevenueBarChartProps> = ({ vendors, onSelectVendor }) => {
  const top10 = [...vendors]
    .sort((a, b) => b.total_revenue - a.total_revenue)
    .slice(0, 10);

  const formatMillions = (val: number) => `$${(val / 1_000_000).toFixed(1)}M`;

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
      <div className="mb-4">
        <h3 className="text-sm font-bold text-white tracking-wide">
          Top 10 Vendors by Attributed Revenue
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Click any bar to drill down into vendor profile, contracts, and margins
        </p>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={top10}
            margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
            onClick={(e: any) => {
              if (e && e.activePayload && e.activePayload[0]) {
                onSelectVendor(e.activePayload[0].payload.vendor_id);
              }
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
            <XAxis type="number" stroke="#64748b" tickFormatter={formatMillions} tick={{ fontSize: 11 }} />
            <YAxis
              type="category"
              dataKey="vendor_name"
              stroke="#94a3b8"
              tick={{ fontSize: 11 }}
              width={140}
            />
            <Tooltip
              formatter={(val: number) => [`$${val.toLocaleString()}`, 'Attributed Revenue']}
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, fontSize: 12 }}
            />
            <Bar dataKey="total_revenue" fill="#38bdf8" radius={[0, 4, 4, 0]} className="cursor-pointer hover:opacity-80 transition-opacity" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
