import Image from "next/image";

export default function CareersPage() {
  return (
    <div className="w-full bg-white min-h-screen text-black pb-32">
      {/* Simplified Workable-style Layout */}
      <div className="max-w-4xl mx-auto px-8 pt-20">
        {/* Logo Section */}
        <div className="flex items-center space-x-4 mb-12">
          <div className="relative w-16 h-16 rounded-full overflow-hidden bg-black shadow-md flex items-center justify-center">
            <Image
              src="/neon-leaf-final.jpg"
              alt="ShadowTag"
              fill
              className="object-cover scale-105"
            />
          </div>
          <div className="flex flex-col">
            <span className="text-3xl font-black tracking-tighter text-[#1b103c] uppercase">
              ShadowTag
            </span>
            <span className="text-xs tracking-widest text-emerald-600 font-bold uppercase mt-[-4px]">
              Intelligence
            </span>
          </div>
        </div>

        {/* Header */}
        <h1 className="text-[32px] font-bold text-[#1b103c] mb-8 font-inter">
          Careers at ShadowTag
        </h1>

        {/* Body Text */}
        <div className="prose max-w-2xl text-[15px] leading-[1.8] text-gray-600 font-sans">
          <p className="mb-6">
            ShadowTag is a U.S.-based artificial intelligence and security company focused on the
            autonomous operations and compliance segments of the enterprise market. Our structural
            architecture—built around the UphillSnowball logic system—is reshaping the industry
            through zero-hallucination deterministic pipelines, stringent risk-management
            frameworks, and a deep connection with the operational security community.
          </p>
          <p className="mb-6">
            We’re expanding into heavy enterprise and defense—bringing our obsessive attention to
            performance, architectural design, and U.S.-based algorithmic verification into
            high-stakes environments like legal intelligence, algorithmic auditing, and military
            innovation. With our infrastructure already aligning with the rigorous Judge 6 Risk
            Protocols, we are actively solving integration issues for customers who demand speed,
            agility, and uncompromising compliance.
          </p>
          <p className="mb-6">
            If you love working at the intersection of enterprise architecture, deterministic
            reasoning, and cutting-edge technology, you’ll feel right at home here.
          </p>
        </div>

        {/* Deliberately leaving the remainder blank per instructions. No "View jobs" button. No "Job Openings" section. */}
      </div>
    </div>
  );
}
