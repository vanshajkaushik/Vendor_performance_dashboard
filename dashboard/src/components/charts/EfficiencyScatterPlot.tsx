import React from 'react';
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine
} from 'recharts';

interface EfficiencyScatterPlotProps {
  data: any[];
  onSelectVendor: (id: string) => void;
}

export const EfficiencyScatterPlot: React.FC<EfficiencyScatterPlotProps> = ({ data, onSelectVendor }) => {
  const formatMillions = (val: number) => `$${(val / 1_000_000).toFixed(0)}M`;

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl text-xs space-y-1">
          <div className="font-bold text-white">{item.vendor_name} ({item.vendor_id})</div>
          <div className="text-slate-400">Category: {item.vendor_category}</div>
          <div className="text-sky-400">Procurement: ${item.total_procurement_cost.toLocaleString()}</div>
          <div className="text-emerald-400">Revenue: ${item.total_revenue.toLocaleString()}</div>
          <div className="text-amber-400">Gross Margin: {item.gross_margin_pct}%</div>
          <div className="text-indigo-300 font-semibold">VPS Score: {item.vendor_performance_score}</div>
          <div className="text-slate-400 text-[10px] mt-1 pt-1 border-t border-slate-800">
            Ratio (Spend/Sales): {item.purchase_to_sales_ratio}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
      <div className="mb-4">
        <h3 className="text-sm font-bold text-white tracking-wide">
          Purchase-to-Sales Efficiency Matrix (Frontier Plot)
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Top-left quadrant: High Revenue / Low Spend (Optimal). Bubble size represents Vendor Performance Score (VPS).
        </p>
      </div>

      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart
            margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
            onClick={(e: any) => {
              if (e && e.activePayload && e.activePayload[0]) {
                onSelectVendor(e.activePayload[0].payload.vendor_id);
              }
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              type="number"
              dataKey="total_procurement_cost"
              name="Procurement Spend"
              stroke="#64748b"
              tickFormatter={formatMillions}
              tick={{ fontSize: 11 }}
              label={{ value: 'Procurement Spend ($)', position: 'insideBottom', offset: -10, fill: '#64748b', fontSize: 11 }}
            />
            <YAxis
              type="number"
              dataKey="total_revenue"
              name="Attributed Sales"
              stroke="#64748b"
              tickFormatter={formatMillions}
              tick={{ fontSize: 11 }}
              label={{ value: 'Attributed Sales ($)', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }}
            />
            <ZAxis type="number" dataKey="vendor_performance_score" range={[60, 320]} name="Score" />
            <Tooltip content={<CustomTooltip />} />
            <Scatter name="Vendors" data={data} fill="#38bdf8" className="cursor-pointer" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
