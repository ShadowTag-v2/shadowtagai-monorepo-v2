"use client";
import { useState } from "react";
import { BrowserProvider } from "ethers";

export default function WalletConnect() {
  const [wallet, setWallet] = useState<string | null>(null);

  const connectWallet = async () => {
    if (typeof window.ethereum !== "undefined") {
      try {
        const provider = new BrowserProvider(window.ethereum);
        const signer = await provider.getSigner();
        const address = await signer.getAddress();
        setWallet(address);
      } catch (err) {
        console.error("User denied connection", err);
      }
    } else {
      alert("Please install MetaMask!");
    }
  };

  return (
    <div className="p-4 border border-gray-700 rounded-lg">
      {!wallet ? (
        <button
          onClick={connectWallet}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-all"
        >
          Connect Wallet
        </button>
      ) : (
        <div>
          <p className="text-green-400 text-sm">
            Connected: {wallet.slice(0, 6)}...{wallet.slice(-4)}
          </p>
          <div className="mt-2 h-2 w-2 bg-green-500 rounded-full inline-block animate-pulse"></div>
          <span className="ml-2 text-xs text-gray-400">Judge 6 Verifying Identity...</span>
        </div>
      )}
    </div>
  );
}
