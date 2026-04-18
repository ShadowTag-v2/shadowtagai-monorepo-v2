import React, { useState } from 'react';
import { useCaptureLead } from '../hooks/useCaptureLead';

export function LeadCaptureForm() {
  const { captureLead, loading, error, success } = useCaptureLead();
  const [email, setEmail] = useState('');
  const [company, setCompany] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await captureLead({ email, company });
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white dark:bg-slate-900 rounded-xl shadow-md border border-slate-200 dark:border-slate-800">
      <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-4 tracking-tight">Access Sentinel Intelligence</h2>
      <p className="text-sm text-slate-600 dark:text-slate-400 mb-6">Equip your executive team with our automated B2B Sovereign workflows.</p>

      {success ? (
        <div className="p-4 bg-green-50/50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <p className="text-green-700 dark:text-green-400 font-medium">Capture confirmed. The Vanguard will reach out shortly.</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Corporate Email</label>
            <input
              type="email"
              required
              disabled={loading}
              className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 bg-transparent text-slate-900 dark:text-slate-100 transition-colors"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="operator@company.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Company Vector</label>
            <input
              type="text"
              required
              disabled={loading}
              className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 bg-transparent text-slate-900 dark:text-slate-100 transition-colors"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="Holding Corp LLC"
            />
          </div>

          {error && (
            <div className="text-red-600 dark:text-red-400 text-sm font-medium pt-2">
              Error: {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-4 bg-slate-900 hover:bg-slate-800 dark:bg-slate-100 dark:hover:bg-slate-200 dark:text-slate-900 text-white font-semibold py-2 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {loading ? <span className="animate-pulse">Tracking...</span> : <span>Initiate Sequence</span>}
          </button>
        </form>
      )}
    </div>
  );
}
