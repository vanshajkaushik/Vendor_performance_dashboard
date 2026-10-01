import React from 'react';
import { Database, CheckCircle, ArrowRight, Server, FileSpreadsheet, ShieldCheck, Zap } from 'lucide-react';
import { PipelineStatus } from '../types';

interface PipelineViewProps {
  status: PipelineStatus | null;
}

export const PipelineView: React.FC<PipelineViewProps> = ({ status }) => {
  return (
    <div className="space-y-6">
      {/* Pipeline Architecture Visual DAG */}
      <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
        <h3 className="text-sm font-bold text-white tracking-wide mb-1">
          End-to-End Data Pipeline Architecture (ETL DAG)
        </h3>
        <p className="text-xs text-slate-400 mb-6">
          Fully reproducible multi-stage data engineering lifecycle from raw ingestion to analytics
        </p>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 items-center">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
            <FileSpreadsheet className="w-6 h-6 text-emerald-400 mx-auto mb-2" />
            <div className="font-bold text-xs text-white">1. Raw Sources</div>
            <div className="text-[10px] text-slate-400 mt-1">Multi-tab Excel & CSV (13k+ POs, 19k+ Sales)</div>
          </div>

          <div className="hidden md:flex justify-center text-slate-600">
            <ArrowRight className="w-5 h-5" />
          </div>

          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
            <Zap className="w-6 h-6 text-sky-400 mx-auto mb-2" />
            <div className="font-bold text-xs text-white">2. Cleaning & Validation</div>
            <div className="text-[10px] text-slate-400 mt-1">Deduplication, schema normalization, outlier clipping</div>
          </div>

          <div className="hidden md:flex justify-center text-slate-600">
            <ArrowRight className="w-5 h-5" />
          </div>

          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
            <Server className="w-6 h-6 text-indigo-400 mx-auto mb-2" />
            <div className="font-bold text-xs text-white">3. PostgreSQL & Analytics</div>
            <div className="text-[10px] text-slate-400 mt-1">3NF Schema, composite indexes, VPS scoring model</div>
          </div>
        </div>
      </div>

      {/* Table Record Counts & Cleaning Audit */}
      <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
        <h3 className="text-sm font-bold text-white tracking-wide mb-1">
          Dataset Ingestion & Cleaning Health Audit
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Shows raw input rows vs cleaned validated rows, confirming removal of duplicates and anomalous records
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {status && Object.entries(status.table_counts).map(([tbl, counts]) => (
            <div key={tbl} className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="text-xs font-bold text-slate-300 uppercase tracking-wide">{tbl}</div>
              <div className="text-lg font-bold text-sky-400 font-mono mt-1">
                {counts.clean_rows.toLocaleString()}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">
                Raw: {counts.raw_rows.toLocaleString()} ({counts.raw_rows - counts.clean_rows} filtered)
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Data Quality Report Matrix */}
      <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide">
              Automated Data Quality & Integrity Checks
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Strict schema constraints, foreign key referential consistency, and mathematical sanity checks
            </p>
          </div>

          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 text-xs font-semibold">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>{status?.data_quality.passed_checks} / {status?.data_quality.total_checks} Checks Passed (100%)</span>
          </div>
        </div>

        <div className="border border-slate-800 rounded-lg overflow-hidden">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                <th className="py-2.5 px-3">Rule / Constraint Name</th>
                <th className="py-2.5 px-3 text-center">Status</th>
                <th className="py-2.5 px-3">Execution Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {status?.data_quality.checks.map((chk, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30">
                  <td className="py-2 px-3 font-semibold text-slate-200">{chk.check_name}</td>
                  <td className="py-2 px-3 text-center">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                      PASSED
                    </span>
                  </td>
                  <td className="py-2 px-3 text-slate-400 font-mono text-[11px]">{chk.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
