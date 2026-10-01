import React, { useState } from 'react';
import { X, UploadCloud, FileSpreadsheet, AlertTriangle, CheckCircle2, AlertCircle, ArrowRight } from 'lucide-react';
import { previewVendorCsv, confirmVendorCsvImport, ImportPreviewResponse } from '../services/api';

interface ImportCsvModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImportComplete: () => void;
}

export const ImportCsvModal: React.FC<ImportCsvModalProps> = ({ isOpen, onClose, onImportComplete }) => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<ImportPreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ inserted: number; message: string } | null>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setPreview(null);
      setError(null);
      setResult(null);
    }
  };

  const handlePreview = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    try {
      const data = await previewVendorCsv(file);
      setPreview(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to preview CSV file.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!preview || preview.valid_rows === 0) return;
    setConfirming(true);
    setError(null);

    try {
      const res = await confirmVendorCsvImport(preview.valid_records);
      setResult({ inserted: res.inserted, message: res.message });
      setTimeout(() => {
        onImportComplete();
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Import failed.');
    } finally {
      setConfirming(false);
    }
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setError(null);
    setResult(null);
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between p-6 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Batch Vendor CSV Ingestion</h3>
              <p className="text-xs text-slate-400">Multi-stage pipeline: Schema validation, duplicate detection, user confirmation</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {error && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 shrink-0 text-rose-400 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {result && (
            <div className="p-5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm flex items-center space-x-3">
              <CheckCircle2 className="w-6 h-6 shrink-0 text-emerald-400" />
              <div>
                <p className="font-semibold text-base">{result.message}</p>
                <p className="text-xs text-emerald-400/80 mt-0.5">Database committed. Reloading vendor registry view...</p>
              </div>
            </div>
          )}

          {!preview && !result && (
            <div className="space-y-4">
              <div className="border-2 border-dashed border-slate-700 hover:border-purple-500/50 rounded-2xl p-8 text-center transition bg-slate-800/30">
                <UploadCloud className="w-12 h-12 text-slate-400 mx-auto mb-3" />
                <p className="text-sm font-medium text-slate-200">Select Vendor CSV File</p>
                <p className="text-xs text-slate-400 mt-1 mb-4">Must include headers: vendor_code, vendor_name, category_id, email, etc.</p>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="hidden"
                  id="csv-file-input"
                />
                <label
                  htmlFor="csv-file-input"
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold rounded-lg cursor-pointer transition inline-block"
                >
                  Browse Files
                </label>
                {file && (
                  <p className="mt-3 text-xs text-purple-300 font-mono">Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)</p>
                )}
              </div>

              <div className="bg-slate-800/40 border border-slate-800 rounded-xl p-4 text-xs text-slate-400 space-y-1">
                <p className="font-semibold text-slate-300">Expected CSV Columns:</p>
                <p className="font-mono text-slate-400">vendor_code, vendor_name, category_id, contact_name, email, phone, city, country, payment_terms, lead_time_days</p>
                <p className="text-slate-500 pt-1">Sample test file available at: <code className="text-slate-400">data/raw/sample_vendor_import.csv</code></p>
              </div>

              <div className="flex justify-end space-x-3">
                <button onClick={onClose} className="px-4 py-2 text-sm text-slate-400 hover:text-white">Cancel</button>
                <button
                  onClick={handlePreview}
                  disabled={!file || loading}
                  className="px-5 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-purple-900 text-white text-sm font-medium rounded-lg transition"
                >
                  {loading ? 'Validating Dataset...' : 'Generate Validation Preview'}
                </button>
              </div>
            </div>
          )}

          {preview && !result && (
            <div className="space-y-6">
              {/* Validation Summary Cards */}
              <div className="grid grid-cols-4 gap-3">
                <div className="bg-slate-800/60 border border-slate-700/60 p-3 rounded-xl">
                  <p className="text-xs text-slate-400">Total Scanned</p>
                  <p className="text-xl font-bold text-white mt-1">{preview.total_rows}</p>
                </div>
                <div className="bg-emerald-950/30 border border-emerald-500/30 p-3 rounded-xl">
                  <p className="text-xs text-emerald-400">Eligible to Ingest</p>
                  <p className="text-xl font-bold text-emerald-400 mt-1">{preview.valid_rows}</p>
                </div>
                <div className="bg-amber-950/30 border border-amber-500/30 p-3 rounded-xl">
                  <p className="text-xs text-amber-400">Duplicates Detected</p>
                  <p className="text-xl font-bold text-amber-400 mt-1">{preview.duplicate_rows}</p>
                </div>
                <div className="bg-rose-950/30 border border-rose-500/30 p-3 rounded-xl">
                  <p className="text-xs text-rose-400">Invalid / Corrupt</p>
                  <p className="text-xl font-bold text-rose-400 mt-1">{preview.invalid_rows}</p>
                </div>
              </div>

              {/* Duplicate & Error Drill-down */}
              {preview.error_details.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                    <AlertCircle className="w-4 h-4" />
                    <span>Detailed Row Rejection Log ({preview.error_details.length} issues)</span>
                  </h4>
                  <div className="max-h-48 overflow-y-auto border border-rose-500/20 bg-rose-950/10 rounded-xl">
                    <table className="w-full text-xs text-left">
                      <thead className="text-rose-300/70 border-b border-rose-500/20 bg-rose-900/20 sticky top-0">
                        <tr>
                          <th className="py-2 px-3">Row</th>
                          <th className="py-2 px-3">Vendor Code</th>
                          <th className="py-2 px-3">Vendor Name</th>
                          <th className="py-2 px-3">Issue Reason</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-rose-500/10 font-mono text-slate-300">
                        {preview.error_details.map((err, idx) => (
                          <tr key={idx} className="hover:bg-rose-950/30">
                            <td className="py-2 px-3 text-rose-400">#{err.row}</td>
                            <td className="py-2 px-3 text-white font-semibold">{err.vendor_code || '—'}</td>
                            <td className="py-2 px-3">{err.vendor_name || '—'}</td>
                            <td className="py-2 px-3 text-rose-300">{err.reason}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Ready to insert table */}
              {preview.valid_records.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Valid Records Preview ({preview.valid_records.length})</span>
                  </h4>
                  <div className="max-h-40 overflow-y-auto border border-emerald-500/20 bg-emerald-950/10 rounded-xl">
                    <table className="w-full text-xs text-left">
                      <thead className="text-emerald-300/70 border-b border-emerald-500/20 bg-emerald-900/20 sticky top-0">
                        <tr>
                          <th className="py-2 px-3">Code</th>
                          <th className="py-2 px-3">Vendor Name</th>
                          <th className="py-2 px-3">Email</th>
                          <th className="py-2 px-3">City</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-emerald-500/10 text-slate-300">
                        {preview.valid_records.slice(0, 10).map((v, idx) => (
                          <tr key={idx}>
                            <td className="py-1.5 px-3 font-mono font-bold text-white">{v.vendor_code}</td>
                            <td className="py-1.5 px-3">{v.vendor_name}</td>
                            <td className="py-1.5 px-3 text-slate-400">{v.email}</td>
                            <td className="py-1.5 px-3">{v.city}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <div className="flex justify-between items-center pt-4 border-t border-slate-800">
                <button
                  onClick={reset}
                  className="text-xs text-slate-400 hover:text-white"
                >
                  Choose Different File
                </button>
                <div className="flex space-x-3">
                  <button onClick={onClose} className="px-4 py-2 text-sm text-slate-400 hover:text-white">Cancel</button>
                  <button
                    onClick={handleConfirm}
                    disabled={preview.valid_rows === 0 || confirming}
                    className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-500 text-white text-sm font-semibold rounded-lg transition flex items-center space-x-2"
                  >
                    {confirming ? 'Committing...' : `Confirm Import (${preview.valid_rows} Records)`}
                    <ArrowRight className="w-4 h-4 ml-1" />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
