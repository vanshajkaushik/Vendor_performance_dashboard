import React, { useEffect, useState } from 'react';
import { X, Building2, DollarSign, Award, MapPin, Mail, Phone, Calendar, ArrowUpRight, TrendingUp } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { VendorDetailResponse } from '../types';
import { fetchVendorDetails } from '../services/api';

interface VendorDetailModalProps {
  vendorId: string | null;
  onClose: () => void;
}

export const VendorDetailModal: React.FC<VendorDetailModalProps> = ({ vendorId, onClose }) => {
  const [data, setData] = useState<VendorDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!vendorId) return;
    setLoading(true);
    fetchVendorDetails(vendorId)
      .then((res) => setData(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [vendorId]);

  if (!vendorId) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#111827] border border-slate-700 w-full max-w-4xl max-h-[90vh] rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-sky-500/20 text-sky-400 border border-sky-500/30 flex items-center justify-center font-bold">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white tracking-tight">
                  {loading ? 'Loading...' : data?.profile.vendor_name}
                </h2>
                <span className="text-xs px-2 py-0.5 rounded font-mono bg-slate-800 text-slate-300 border border-slate-700">
                  {vendorId}
                </span>
              </div>
              <p className="text-xs text-slate-400">
                {data?.profile.vendor_category} • {data?.profile.location} • Contract Start: {data?.profile.contract_start_date}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm">Loading vendor analytics drill-down...</div>
          ) : data ? (
            <>
              {/* Strategic Recommendation Banner */}
              <div className="p-4 rounded-xl bg-sky-950/40 border border-sky-500/30 text-sky-200 text-xs flex gap-3 items-start">
                <Award className="w-5 h-5 text-sky-400 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-sky-300 mb-0.5">Strategic Recommendation & Analysis</div>
                  <div className="leading-relaxed">{data.profile.recommendation}</div>
                </div>
              </div>

              {/* Score Breakdown Radar/Metrics Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 text-center">
                  <div className="text-[10px] uppercase font-semibold text-slate-400">VPS Total Score</div>
                  <div className="text-xl font-bold text-sky-400 mt-1">{data.profile.vendor_performance_score}/100</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">{data.profile.performance_tier}</div>
                </div>
                <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 text-center">
                  <div className="text-[10px] uppercase font-semibold text-slate-400">Gross Margin</div>
                  <div className="text-xl font-bold text-emerald-400 mt-1">{data.profile.gross_margin_pct}%</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Capture Rate</div>
                </div>
                <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 text-center">
                  <div className="text-[10px] uppercase font-semibold text-slate-400">Spend/Sales Ratio</div>
                  <div className="text-xl font-bold text-amber-400 mt-1">{data.profile.purchase_to_sales_ratio}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Target &lt; 0.65</div>
                </div>
                <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 text-center">
                  <div className="text-[10px] uppercase font-semibold text-slate-400">Price Variance</div>
                  <div className={`text-xl font-bold mt-1 ${data.profile.price_variance_pct < 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {data.profile.price_variance_pct > 0 ? `+${data.profile.price_variance_pct}%` : `${data.profile.price_variance_pct}%`}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">vs Benchmark</div>
                </div>
                <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 text-center">
                  <div className="text-[10px] uppercase font-semibold text-slate-400">Turnover Ratio</div>
                  <div className="text-xl font-bold text-indigo-400 mt-1">{data.profile.inventory_turnover}x</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Annualized</div>
                </div>
              </div>

              {/* Monthly Spend Trajectory Chart */}
              <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
                  Historical Procurement Spend Trajectory (Monthly)
                </h4>
                <div className="h-48 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data.monthly_trend} margin={{ top: 5, right: 10, left: 10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="month" stroke="#64748b" tick={{ fontSize: 10 }} />
                      <YAxis stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
                      <Tooltip
                        formatter={(val: number) => [`$${val.toLocaleString()}`, 'Monthly Spend']}
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, fontSize: 11 }}
                      />
                      <Area type="monotone" dataKey="spend" stroke="#0284c7" fill="#0284c7" fillOpacity={0.25} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Products Supplied Matrix */}
              <div>
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
                  Supplied Products Breakdown ({data.products.length} catalog items)
                </h4>
                <div className="border border-slate-800 rounded-lg overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                        <th className="py-2.5 px-3">Product Name</th>
                        <th className="py-2.5 px-3">Subcategory</th>
                        <th className="py-2.5 px-3 text-right">Benchmark Cost</th>
                        <th className="py-2.5 px-3 text-right">Avg Paid</th>
                        <th className="py-2.5 px-3 text-right">Variance</th>
                        <th className="py-2.5 px-3 text-right">Units Sourced</th>
                        <th className="py-2.5 px-3 text-right">Total Spend</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {data.products.map((p) => (
                        <tr key={p.product_id} className="hover:bg-slate-800/30">
                          <td className="py-2 px-3">
                            <div className="font-semibold text-slate-200">{p.product_name}</div>
                            <div className="text-[10px] text-slate-500 font-mono">{p.product_id}</div>
                          </td>
                          <td className="py-2 px-3 text-slate-400">{p.subcategory}</td>
                          <td className="py-2 px-3 text-right font-mono text-slate-400">${p.unit_cost.toFixed(2)}</td>
                          <td className="py-2 px-3 text-right font-mono text-slate-200">${p.avg_price_paid.toFixed(2)}</td>
                          <td className={`py-2 px-3 text-right font-mono ${p.price_variance_pct < 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {p.price_variance_pct > 0 ? `+${p.price_variance_pct}%` : `${p.price_variance_pct}%`}
                          </td>
                          <td className="py-2 px-3 text-right font-mono text-slate-300">{p.units_purchased.toLocaleString()}</td>
                          <td className="py-2 px-3 text-right font-mono font-semibold text-amber-400">${p.total_spend.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
};
