import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend
} from 'recharts';
import { CategoryData } from '../../types';

interface CategoryPieChartProps {
  data: CategoryData[];
}

const COLORS = ['#0284c7', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

export const CategoryPieChart: React.FC<CategoryPieChartProps> = ({ data }) => {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
      <div className="mb-2">
        <h3 className="text-sm font-bold text-white tracking-wide">
          Sales Revenue Contribution by Category
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Product category revenue breakdown across procurement categories
        </p>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={85}
              paddingAngle={4}
              dataKey="sales_revenue"
              nameKey="category"
            >
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(val: number) => [`$${val.toLocaleString()}`, 'Revenue']}
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, fontSize: 12 }}
            />
            <Legend wrapperStyle={{ fontSize: 11, paddingTop: 6 }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
