import type React from 'react';
import { useState } from 'react';

interface MarketplaceProps {
  videoId: string;
}

export const MicroLicensingMarketplace: React.FC<MarketplaceProps> = ({ videoId }) => {
  const [purchasing, setPurchasing] = useState(false);
  const [success, setSuccess] = useState(false);

  const handlePurchase = async () => {
    setPurchasing(true);
    try {
      // Mock API call to MCP server
      const res = await fetch('/api/mcp/purchase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ videoId, agentWalletToken: 'agnt_mock_wallet_123' }),
      });
      if (res.ok) {
        setSuccess(true);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setPurchasing(false);
    }
  };

  if (success) {
    return (
      <div className="p-6 bg-green-50 rounded-lg text-green-800 text-center">
        <h3 className="text-xl font-bold mb-2">License Granted!</h3>
        <p>Workflow data unlocked successfully.</p>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white shadow-lg rounded-lg border border-gray-100">
      <h2 className="text-2xl font-bold mb-4">Micro-Licensing Marketplace</h2>
      <div className="space-y-4">
        <div className="flex justify-between items-center p-4 bg-gray-50 rounded">
          <div>
            <h4 className="font-semibold text-gray-800">Workflow License</h4>
            <p className="text-sm text-gray-500">Unlocks full remix tree & provenance data</p>
          </div>
          <div className="text-right">
            <span className="text-xl font-bold text-blue-600">$2.99</span>
          </div>
        </div>

        <button
          onClick={handlePurchase}
          disabled={purchasing}
          className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-bold rounded-lg transition-colors"
        >
          {purchasing ? 'Processing...' : 'Purchase via Agent Wallet'}
        </button>
      </div>
    </div>
  );
};
