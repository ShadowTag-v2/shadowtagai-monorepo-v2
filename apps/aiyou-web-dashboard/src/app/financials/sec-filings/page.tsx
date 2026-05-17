import Image from "next/image";
import React from "react";

export default function GeneratedSubPage() {
  return (
    <div className="min-h-screen bg-white text-black">
      {/* Dark Hero Header */}
      <div className="w-full bg-[#0A0B12] h-[550px] relative overflow-hidden flex flex-col items-center justify-center">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-emerald-900/40 via-[#0A0B12] to-[#0A0B12] opacity-80"></div>
        <div className="relative z-10 flex flex-col items-center justify-center text-center h-full w-full py-12 px-8">
          <div className="w-[360px] h-[360px] rounded-full overflow-hidden mb-8 relative shadow-[0_0_80px_rgba(16,185,129,0.3)] ring-1 ring-emerald-500/10 bg-[#0A0B12]">
            <Image
              src="/neon-leaf-final.jpg"
              alt="Neon Leaf Logo"
              fill
              className="object-cover scale-[1.03]"
              priority
            />
          </div>
          <h1 className="text-5xl text-white font-bold capitalize tracking-tight relative z-10 w-full text-center max-w-6xl mx-auto shrink-0">
            Sec Filings
          </h1>
        </div>
      </div>

      {/* Content Area with Sidebar */}
      <div className="max-w-6xl mx-auto py-16 px-8 flex flex-col md:flex-row gap-16">
        {/* Sidebar Navigation Mock */}
        <div className="w-full md:w-1/4">
          <div className="text-[#1B103C] font-bold border-l-[3px] border-[#1b103c] pl-4 cursor-pointer mb-2 bg-gray-50 py-3 shadow-sm">
            Sec Filings Protocol
          </div>
          <div className="text-gray-500 font-semibold border-l-[3px] border-transparent pl-4 cursor-pointer mb-2 hover:bg-gray-50 py-3 transition-colors hover:text-black hover:border-gray-300">
            Compliance
          </div>
          <div className="text-gray-500 font-semibold border-l-[3px] border-transparent pl-4 cursor-pointer mb-2 hover:bg-gray-50 py-3 transition-colors hover:text-black hover:border-gray-300">
            Documentation
          </div>
        </div>

        {/* Main Content Details */}
        <div className="w-full md:w-3/4">
          <div className="bg-[#0B0A11] text-white py-3 px-6 font-semibold mb-6 text-sm tracking-wide uppercase">
            Sec Filings Execution Log
          </div>
        </div>
      </div>
    </div>
  );
}
