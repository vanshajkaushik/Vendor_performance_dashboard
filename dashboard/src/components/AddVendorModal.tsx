import React, { useState } from 'react';
import { X, Building2, AlertTriangle, CheckCircle, Mail, Phone, MapPin, Tag } from 'lucide-react';
import { createVendor, VendorCreateData } from '../services/api';

interface AddVendorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onVendorAdded: () => void;
}

export const AddVendorModal: React.FC<AddVendorModalProps> = ({ isOpen, onClose, onVendorAdded }) => {
  const [formData, setFormData] = useState<VendorCreateData>({
    vendor_code: '',
    vendor_name: '',
    category_id: 1,
    contact_name: '',
    email: '',
    phone: '',
    city: '',
    country: 'USA',
    payment_terms: 'Net 30',
    lead_time_days: 14,
    status: 'Active',
    contract_start_date: new Date().toISOString().split('T')[0]
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const res = await createVendor(formData);
      if (res.success) {
        setSuccess(`Vendor ${res.vendor_code} added successfully! Status initialized as "New / Insufficient Data".`);
        setTimeout(() => {
          onVendorAdded();
          onClose();
        }, 1500);
      } else {
        setError(res.error || 'Failed to create vendor');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between p-6 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Register New Vendor</h3>
              <p className="text-xs text-slate-400">Add vendor with automated duplicate prevention & Star Schema enrollment</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 shrink-0 text-rose-400 mt-0.5" />
              <div>
                <span className="font-semibold">Duplicate or Validation Error:</span> {error}
              </div>
            </div>
          )}

          {success && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 shrink-0 text-emerald-400" />
              <span>{success}</span>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Vendor Code *</label>
              <input
                type="text"
                required
                placeholder="e.g. VND-099"
                value={formData.vendor_code}
                onChange={e => setFormData({ ...formData, vendor_code: e.target.value.toUpperCase() })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Vendor / Legal Entity Name *</label>
              <input
                type="text"
                required
                placeholder="Acme Industrial Logistics"
                value={formData.vendor_name}
                onChange={e => setFormData({ ...formData, vendor_name: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Category</label>
              <select
                value={formData.category_id}
                onChange={e => setFormData({ ...formData, category_id: parseInt(e.target.value) })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              >
                <option value={1}>Raw Materials</option>
                <option value={2}>Packaging</option>
                <option value={3}>Electronics & Components</option>
                <option value={4}>Machinery & Equipment</option>
                <option value={5}>MRO Supplies</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Contact Email *</label>
              <input
                type="email"
                required
                placeholder="procurement@acme.com"
                value={formData.email}
                onChange={e => setFormData({ ...formData, email: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Contact Person Name</label>
              <input
                type="text"
                placeholder="John Doe"
                value={formData.contact_name}
                onChange={e => setFormData({ ...formData, contact_name: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Phone Number</label>
              <input
                type="text"
                placeholder="+1-555-0199"
                value={formData.phone}
                onChange={e => setFormData({ ...formData, phone: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">City / Region</label>
              <input
                type="text"
                placeholder="Dallas, TX"
                value={formData.city}
                onChange={e => setFormData({ ...formData, city: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Country</label>
              <input
                type="text"
                value={formData.country}
                onChange={e => setFormData({ ...formData, country: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Payment Terms</label>
              <select
                value={formData.payment_terms}
                onChange={e => setFormData({ ...formData, payment_terms: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              >
                <option value="Net 15">Net 15</option>
                <option value="Net 30">Net 30</option>
                <option value="Net 45">Net 45</option>
                <option value="Net 60">Net 60</option>
                <option value="2/10 Net 30">2/10 Net 30</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Quoted Lead Time (Days)</label>
              <input
                type="number"
                min="1"
                max="90"
                value={formData.lead_time_days}
                onChange={e => setFormData({ ...formData, lead_time_days: parseInt(e.target.value) || 14 })}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700 text-xs text-slate-400 flex items-center space-x-2">
            <Tag className="w-4 h-4 text-amber-400 shrink-0" />
            <span>
              <strong>Note:</strong> Newly created vendors without transaction history will receive performance tier <strong>New / Insufficient Data</strong> and an unrated score (N/A) until PO executions occur.
            </span>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 text-sm bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white font-medium rounded-lg transition flex items-center space-x-2"
            >
              {loading ? (
                <span>Registering...</span>
              ) : (
                <>
                  <Building2 className="w-4 h-4" />
                  <span>Register Vendor</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
