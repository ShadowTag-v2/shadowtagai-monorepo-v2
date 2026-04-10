import Image from "next/image";

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
            Contact
          </h1>
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-4xl mx-auto py-24 px-8 flex justify-center text-center">
        <div className="flex flex-col items-center">
          <h2 className="text-2xl font-bold font-inter text-[#1b103c] mb-8 uppercase tracking-widest border-b-2 border-emerald-500 pb-2">
            Headquarters
          </h2>
          <address className="not-italic flex flex-col items-center space-y-1.5 text-gray-700 font-medium">
            <p className="font-black text-2xl text-gray-900 tracking-wide mb-1">Erik Hancock</p>
            <p className="text-emerald-700 font-bold tracking-widest uppercase text-sm mb-6">
              Founder — CEO
            </p>

            <div className="bg-gray-50 border border-gray-100 px-12 py-8 rounded-sm shadow-sm flex flex-col items-center">
              <p className="text-lg font-bold text-gray-900 mb-2">ShadowTagAi Inc.</p>
              <p>495 N Main St., #119</p>
              <p>Lakeport, CA 95453</p>

              <div className="mt-8 pt-6 border-t border-gray-200 flex flex-col space-y-3 px-8 text-left self-stretch">
                <p className="flex justify-between w-full m-0">
                  <span className="text-gray-900 font-bold">Telephone:</span>{" "}
                  <a
                    href="tel:369-235-5643"
                    className="hover:text-emerald-700 transition-colors ml-8"
                  >
                    (369) 235-5643
                  </a>
                </p>
                <p className="flex justify-between w-full m-0">
                  <span className="text-gray-900 font-bold">Facsimile:</span>{" "}
                  <span className="ml-8">(707) 263-8659</span>
                </p>
                <p className="flex justify-between w-full m-0">
                  <span className="text-gray-900 font-bold">Email:</span>{" "}
                  <a
                    href="mailto:redacted@shadowtag-v4.local"
                    className="hover:text-emerald-700 transition-colors ml-8"
                  >
                    redacted@shadowtag-v4.local
                  </a>
                </p>
              </div>
            </div>
          </address>
        </div>
      </div>
    </div>
  );
}
