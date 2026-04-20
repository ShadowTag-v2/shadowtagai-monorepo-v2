'use client';
import { useCopilotAction } from '@copilotkit/react-core';
import { motion } from 'framer-motion';
import { Activity, ShieldAlert, ShieldCheck } from 'lucide-react';

export function ThreatRadarWidget() {
  useCopilotAction(
    {
      name: 'render_threat_radar',
      description: 'Renders the interactive Threat Radar widget for target company analysis.',
      parameters: [
        {
          name: 'ticker',
          type: 'string',
          description: 'The target company ticker symbol.',
        },
        {
          name: 'score',
          type: 'number',
          description: 'The calculated viability score.',
        },
        {
          name: 'cloudflare_fraud_flag',
          type: 'boolean',
          description: 'Whether Cloudflare Radar detected infrastructure fraud.',
        },
        {
          name: 'action',
          type: 'string',
          description: 'The recommended Sovereign action.',
        },
      ],
      handler: async (args) => {
        // Must return string back to the LLM so it knows the tool executed
        return `Threat radar displayed for ${args.ticker || 'target'}. Fraud Flag: ${args.cloudflare_fraud_flag}.`;
      },
      render: (props) => {
        const { status, args } = props;

        if (status !== 'complete') {
          return (
            <div className="p-6 border border-gray-800 bg-gray-950 rounded-xl text-emerald-400 font-mono flex items-center shadow-[0_0_15px_rgba(16,185,129,0.1)]">
              <Activity className="animate-spin w-5 h-5 mr-3" />
              <span>
                [A2UI] Establishing Cloudflare Radar Link for {args.ticker || 'TARGET'}...
              </span>
            </div>
          );
        }

        return (
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className={`p-6 border ${args.cloudflare_fraud_flag ? 'border-red-600 bg-red-950/20 shadow-[0_0_20px_rgba(220,38,38,0.2)]' : 'border-emerald-600 bg-emerald-950/20 shadow-[0_0_20px_rgba(16,185,129,0.2)]'} rounded-xl font-mono`}
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-black text-white uppercase tracking-wider">
                  {args.ticker} THREAT RADAR
                </h3>
                <p className="text-gray-400 text-sm">Real-time infrastructure intelligence.</p>
              </div>
              {args.cloudflare_fraud_flag ? (
                <ShieldAlert className="w-8 h-8 text-red-500 animate-pulse" />
              ) : (
                <ShieldCheck className="w-8 h-8 text-emerald-500" />
              )}
            </div>

            <div className="grid grid-cols-2 gap-4 mt-6">
              <div className="bg-black/40 p-3 rounded border border-gray-800">
                <span className="block text-xs text-gray-500 uppercase">Viability Score</span>
                <span className="text-2xl font-bold text-white">{args.score}</span>
              </div>
              <div className="bg-black/40 p-3 rounded border border-gray-800">
                <span className="block text-xs text-gray-500 uppercase">Kinetic Action</span>
                <span
                  className={`text-xl font-bold ${args.action?.includes('SHORT') ? 'text-red-400' : 'text-emerald-400'}`}
                >
                  {args.action}
                </span>
              </div>
              <div className="col-span-2 bg-black/40 p-3 rounded border border-gray-800">
                <span className="block text-xs text-gray-500 uppercase flex mb-1">
                  Infrastructure Fraud Policy
                </span>
                {args.cloudflare_fraud_flag ? (
                  <span className="text-sm font-bold text-red-400 border border-red-500/50 bg-red-500/10 px-2 py-1 flex items-center">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-ping mr-2"></span>
                    ANOMALIES DETECTED - L7 ATTACK SURFACE
                  </span>
                ) : (
                  <span className="text-sm text-emerald-400 border border-emerald-500/50 bg-emerald-500/10 px-2 py-1 inline-flex">
                    CLEAN - VERIFIED BY CLOUDFLARE MCP
                  </span>
                )}
              </div>
            </div>
          </motion.div>
        );
      },
    },
    [],
  );

  return null;
}
