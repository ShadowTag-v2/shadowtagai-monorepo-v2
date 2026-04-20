import Image from 'next/image';
import Link from 'next/link';

export default function AboutUsPage() {
  return (
    <div className="min-h-screen bg-white text-black pb-24">
      {/* Dark Hero Header */}
      <div className="w-full bg-[#0A0B12] h-[550px] relative overflow-hidden flex flex-col items-center justify-center">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-emerald-900/40 via-[#0A0B12] to-[#0A0B12] opacity-80"></div>
        {/* Background Hardware Hint (like the screenshot) */}
        <div className="absolute inset-0 opacity-20 transform scale-125 mix-blend-luminosity pointer-events-none">
          {/* Keeping it simple with the neon leaf as main focal */}
        </div>
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

      {/* Executive Team Section */}
      <div className="max-w-6xl mx-auto py-16 px-8">
        <h2 className="text-4xl font-bold text-[#0B0A11] mb-8 font-inter tracking-tight">
          Executive team
        </h2>

        {/* Foundational Accordion Container */}
        <div className="flex flex-col space-y-4">
          {/* Erik Hancock - Interactive Accordion */}
          <details className="w-full group shadow-md border border-gray-200 bg-white" open>
            {/* Accordion Header (Interactive toggle) */}
            <summary className="w-full bg-[#0E0C16] group-open:bg-[#413185] text-white px-6 py-4 flex justify-between items-center cursor-pointer hover:bg-black group-open:hover:bg-[#4f3da3] transition-colors list-none [&::-webkit-details-marker]:hidden">
              <span className="font-semibold text-lg">Erik Hancock</span>
              <div className="flex items-center space-x-4">
                <span className="text-sm">Chief Executive Officer and Director</span>
                <svg
                  className="w-4 h-4 text-white transform group-open:rotate-180 transition-transform duration-300"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <title>Toggle details</title>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2.5"
                    d="M19 9l-7 7-7-7"
                  ></path>
                </svg>
              </div>
            </summary>

            {/* Accordion Content */}
            <div className="w-full flex flex-col md:flex-row p-8 gap-8 border-t border-gray-200">
              {/* Image */}
              <div className="w-full md:w-1/4 shrink-0">
                <div className="relative aspect-[3/4] md:aspect-square w-full filter brightness-105 contrast-105">
                  <Image
                    src="/erik_hancock_new.jpg"
                    alt="Erik Hancock"
                    fill
                    className="object-cover rounded-sm shadow-md"
                    sizes="(max-width: 768px) 100vw, 300px"
                  />
                </div>
              </div>

              {/* Bio Text */}
              <div className="w-full md:w-3/4">
                <div className="prose max-w-none text-gray-900 font-sans text-[15px] leading-[1.65]">
                  <p className="mb-4">
                    Erik Hancock is the Founder and Chief Executive Officer of ShadowTagAi and the
                    primary architect behind the company’s flagship AI research agent,
                    UphillSnowball. Mr. Hancock brings a highly disciplined, strategic approach to
                    the technology sector, drawing on a distinguished 24-year career in active duty
                    military and National Guard service. His extensive military background includes
                    service as a Green Beret, Infantryman, Parachutist, Jumpmaster, and Special
                    Forces Sniper, alongside 36 months of combat deployment in Iraq between 2005 and
                    2010. This high-stakes environment instilled a rigorous, &quot;leave nothing to
                    chance&quot; methodology to risk management and operational security that
                    fundamentally drives his corporate vision.
                  </p>
                  <p className="mb-4">
                    Academically, Mr. Hancock holds a dual Bachelor of Arts in History and German
                    from Auburn University and a Juris Doctor from Empire College School of Law.
                    After successfully passing the California Bar Exam in 2020 and retiring from
                    military service, he recognized a critical need for automated, fail-safe
                    safeguards in legal and business research.
                  </p>
                  <p>
                    Leveraging his deep legal education and tactical training, Mr. Hancock founded
                    ShadowTagAi to address these complex industry vulnerabilities. He is the sole
                    developer of UphillSnowball, which was initially engineered as proprietary
                    internal tooling to ensure meticulous decision-making and mitigate operational
                    risk. UphillSnowball introduces a pioneering self-correcting, recursive-loop
                    architecture—the first of its kind in AI. Under Mr. Hancock&apos;s leadership,
                    ShadowTagAi provides enterprises and law firms with autonomous, continuously
                    refining intelligence solutions that offer round-the-clock research oversight
                    and security.
                  </p>

                  {/* Mobile & Desktop LinkedIn Link */}
                  <div className="mt-8 pt-6 border-t border-gray-100 flex justify-start">
                    <Link
                      href="https://www.linkedin.com/in/erik-hancock-80442476"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center text-[#0a66c2] hover:text-white transition-colors font-medium bg-[#f3f9ff] hover:bg-[#0a66c2] border border-[#d6e9f9] px-5 py-2.5 rounded-md md:rounded-full text-sm shadow-sm"
                    >
                      <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                        <title>LinkedIn</title>
                        <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                      </svg>
                      Connect with Erik
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </details>

          {/* End of Executive Team section */}
        </div>
      </div>
    </div>
  );
}
