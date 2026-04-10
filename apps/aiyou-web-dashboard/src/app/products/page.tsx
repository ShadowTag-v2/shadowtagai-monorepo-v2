import Image from "next/image";
import Link from "next/link";

export default function ProductsPage() {
  return (
    <div className="w-full bg-white pb-24">
      {/* Hero Section */}
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
            Products
          </h1>
        </div>
      </div>

      {/* Intro Header */}
      <div className="max-w-5xl mx-auto mt-16 px-6 relative z-20">
        <h1 className="text-[40px] font-bold text-gray-900 font-inter mb-6">
          High-Performance, Fully Compliant Autonomous Nodes
        </h1>
        <p className="text-lg text-gray-700 font-serif leading-relaxed">
          Built for professionals and operators alike, ShadowTag provides a full range of
          next-generation, high-performance cognitive arrays proudly verified in the USA. From
          advanced zero-trust execution electronics to precision-engineered memory subsystems, you
          can count on ShadowTag for the cutting-edge accuracy you want, the cryptographic
          verification you require, and the reliable autonomy you demand.
        </p>

        {/* Product Card 1 */}
        <div className="mt-16 bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow duration-300 flex flex-col md:flex-row">
          <div className="md:w-5/12 bg-gray-100 flex items-center justify-center p-12 relative min-h-[300px]">
            <div className="absolute inset-0 bg-gradient-to-br from-zinc-200 to-zinc-300 opacity-50"></div>
            <div className="relative z-10 flex flex-col items-center">
              <div className="w-40 h-32 bg-zinc-800 rounded-sm shadow-2xl border-b-4 border-r-4 border-zinc-900 flex items-center justify-center">
                <span className="text-zinc-600 font-bold text-2xl tracking-widest uppercase text-center leading-tight">
                  S-KV
                  <br />
                  <span className="text-xs">SLAB</span>
                </span>
              </div>
              <div className="w-48 h-10 bg-zinc-900 mt-[-20px] rounded-sm transform relative z-[-1] scale-x-90 blur-[1px]"></div>
            </div>
          </div>

          <div className="md:w-7/12 p-10 flex flex-col justify-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 font-inter">
              Google Cloud Enterprise Architecture
            </h2>
            <p className="text-gray-600 text-sm leading-relaxed mb-8 flex-grow">
              Engineered specifically for Google Cloud environments, ShadowTag leverages BigQuery
              and Ice Lake data architectures to deliver high-performance, verifiable intelligence
              execution. Providing an uncompromising, tamper-proof audit trail, our structural loops
              perform rigorous algorithmic shepardizing—validating all precedents, internal
              documents, and regulatory citations. Ensure complete data sovereignty while deploying
              hallucination-free reasoning directly on top of the industry&apos;s most robust cloud
              infrastructure.
            </p>
            <div className="flex space-x-4 self-end">
              <span className="px-6 py-2 border border-gray-400 text-gray-400 font-bold rounded-full cursor-not-allowed text-sm text-center tracking-wide">
                Data Sheet
              </span>
              <Link
                href="/contact"
                className="px-6 py-2 border border-emerald-600 bg-emerald-600 text-white font-bold rounded-full hover:bg-emerald-700 hover:border-emerald-700 transition-colors text-sm text-center shadow-md"
              >
                Request Quote
              </Link>
            </div>
          </div>
        </div>

        {/* Product Card 2 */}
        <div className="mt-10 bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow duration-300 flex flex-col md:flex-row">
          <div className="md:w-5/12 bg-gray-50 flex items-center justify-center p-12 relative min-h-[300px]">
            <div className="absolute inset-0 bg-gradient-to-br from-gray-50 to-gray-200 opacity-50"></div>
            <div className="relative z-10">
              <div className="w-56 h-32 bg-[#0a0a0a] rounded-xl shadow-2xl flex items-center justify-center border-b-[6px] border-zinc-900">
                <span className="text-white font-mono tracking-widest text-opacity-80">
                  J-6 SHIELD
                </span>
              </div>
            </div>
          </div>

          <div className="md:w-7/12 p-10 flex flex-col justify-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 font-inter">Judge 6</h2>
            <p className="text-gray-600 text-sm leading-relaxed mb-8 flex-grow">
              Built in the USA, leading with an automated tier risk management framework. The J6
              Shield delivers industry-leading situational awareness via dual 1920×1080 semantic
              index validation. A built-in DVR, onboard log caching, and a flexible memory input
              range guarantees zero-hallucination tracking. Protects against existential liabilities
              without compromising execution velocity.
            </p>
            <div className="flex space-x-4 self-end">
              <span className="px-6 py-2 border border-gray-400 text-gray-400 font-bold rounded-full cursor-not-allowed text-sm text-center tracking-wide">
                Data Sheet
              </span>
              <Link
                href="/contact"
                className="px-6 py-2 border border-emerald-600 bg-emerald-600 text-white font-bold rounded-full hover:bg-emerald-700 hover:border-emerald-700 transition-colors text-sm text-center shadow-md"
              >
                Request Quote
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
