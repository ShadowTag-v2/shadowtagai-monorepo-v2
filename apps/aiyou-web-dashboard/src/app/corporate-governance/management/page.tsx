import Image from "next/image";
import Link from "next/link";

export default function ManagementPage() {
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
            Management
          </h1>
        </div>
      </div>

      {/* Content Area with Sidebar */}
      <div className="max-w-6xl mx-auto py-16 px-8 flex flex-col md:flex-row gap-16">
        {/* Simple Sidebar Navigation */}
        <div className="w-full md:w-1/4">
          <div className="text-[#1B103C] font-bold border-l-[3px] border-[#1b103c] pl-4 cursor-pointer mb-2 bg-gray-50 py-3 shadow-sm">
            Management
          </div>

          {/* Specific "one pulldown" request */}
          <details className="mt-4 bg-gray-50 border border-gray-200 rounded-md overflow-hidden group cursor-pointer shadow-sm">
            <summary className="p-3 font-semibold text-gray-700 focus:outline-none flex justify-between items-center bg-white group-hover:bg-gray-50 transition-colors">
              <span>Executive Roster</span>
              <svg
                className="w-4 h-4 text-emerald-500 transform group-open:rotate-180 transition-transform"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <title>Expand</title>
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M19 9l-7 7-7-7"
                ></path>
              </svg>
            </summary>
            <div className="p-3 border-t border-gray-200 bg-gray-50 text-sm flex flex-col space-y-2">
              <span className="text-emerald-700 font-bold hover:underline">Erik Hancock - CEO</span>
              <span className="text-gray-500 hover:text-gray-900 transition-colors">
                More to follow...
              </span>
            </div>
          </details>
        </div>

        {/* Main Content Details */}
        <div className="w-full md:w-3/4">
          <div className="flex flex-col bg-white rounded-xl shadow-[0_0_40px_rgba(0,0,0,0.03)] border border-gray-100 p-8 md:p-12">
            {/* Header Section */}
            <div className="w-full flex justify-between items-start mb-8 border-b border-gray-100 pb-6">
              <div>
                <h2 className="text-4xl font-bold text-[#1b103c] mb-2 font-inter tracking-tight">
                  Erik Hancock
                </h2>
                <h3 className="font-semibold text-emerald-600 uppercase tracking-widest text-[15px]">
                  Chief Executive Officer and Director
                </h3>
              </div>
              <Link
                href="https://www.linkedin.com/in/erik-hancock-80442476"
                target="_blank"
                rel="noopener noreferrer"
                className="hidden md:inline-flex items-center text-[#0a66c2] hover:text-white transition-colors font-medium bg-[#f3f9ff] hover:bg-[#0a66c2] border border-[#d6e9f9] px-5 py-2 rounded-full text-sm shadow-sm"
              >
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <title>LinkedIn</title>
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                </svg>
                Connect
              </Link>
            </div>

            {/* Image Section - Placed Below Title */}
            <div className="w-full md:w-2/5 shrink-0 mb-8">
              <div className="rounded-xl overflow-hidden shadow-lg border border-gray-200 aspect-[3/4] relative transform hover:scale-[1.01] transition-transform duration-300">
                <Image
                  src="/erik_hancock.jpg"
                  alt="Erik Hancock - CEO"
                  fill
                  className="object-cover"
                  sizes="(max-width: 768px) 100vw, 400px"
                  priority
                />
              </div>
            </div>

            {/* Mobile LinkedIn Link */}
            <Link
              href="https://www.linkedin.com/in/erik-hancock-80442476"
              target="_blank"
              rel="noopener noreferrer"
              className="md:hidden inline-flex items-center justify-center text-[#0a66c2] transition-colors mb-8 font-medium bg-[#f3f9ff] border border-[#d6e9f9] px-4 py-3 rounded-md text-sm shadow-sm w-full"
            >
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <title>LinkedIn</title>
                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
              </svg>
              Connect on LinkedIn
            </Link>

            {/* Bio Section */}
            <div className="w-full flex flex-col">
              <div className="prose max-w-none text-gray-600 font-inter leading-relaxed text-lg">
                <p className="font-semibold text-gray-800 mb-6 border-l-4 border-emerald-500 pl-4 py-1">
                  Pioneering architect behind the UphillSnowball recursive deployment framework and
                  leader of the Sovereign Logic Syndicate.
                </p>

                <div className="p-6 bg-gray-50 border border-gray-100 rounded-lg shadow-inner italic text-gray-600 text-base">
                  [ Executive expanded biography to follow securely. Profile node initialized. ]
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
