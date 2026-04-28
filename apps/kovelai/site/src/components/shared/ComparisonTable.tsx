export default function ComparisonTable() {
  const rows = [
    {
      feature: 'Client web searches',
      risk: '⚠️ Discoverable — other side obtains them',
      safe: "✅ Privileged through your firm's portal",
    },
    {
      feature: 'AI chatbot conversations',
      risk: '⚠️ Subpoenaed and weaponized at trial',
      safe: '✅ Protected under Kovel Doctrine',
    },
    {
      feature: 'Client sends you AI legal opinions',
      risk: '⚠️ Incorrect, irritating, discoverable',
      safe: '✅ You see it first, give the real opinion',
    },
    {
      feature: 'Pre-trial client anxiety',
      risk: '⚠️ Panic searches create evidence for other side',
      safe: '✅ Client searches freely, recalls all facts',
    },
    {
      feature: 'Attorney awareness',
      risk: '❌ Ambushed by random client searches',
      safe: '✅ Full real-time visibility on every session',
    },
    {
      feature: 'First legal opinion',
      risk: '❌ Client gets it from ChatGPT, surprises you',
      safe: '✅ You give the first opinion from oversight seat',
    },
    {
      feature: 'Billing',
      risk: '$0 (unbilled panic calls and wasted time)',
      safe: '✅ Auto-billed via client credit card per cycle',
    },
    {
      feature: 'Client pitch',
      risk: '❌ No leverage to channel client research',
      safe: '✅ "Through our portal, or proceed at your peril"',
    },
  ];

  return (
    <section className="py-20 md:py-28" id="comparison">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">Why You Deploy KovelAI</div>
        <h2 className="section-title">Your Client Without KovelAI vs. With</h2>
        <p className="section-desc mb-10">
          Every day without your firm&apos;s privileged portal is another day opposing counsel can
          mine your client&apos;s web and AI activity. You buy KovelAI for your clients the same way
          a police chief buys vests for the force.
        </p>
        <div className="overflow-x-auto glass-card p-0">
          <table className="comparison-table">
            <thead>
              <tr>
                <th scope="col">Scenario</th>
                <th scope="col" className="text-error">
                  Client Unprotected
                </th>
                <th scope="col" className="text-blue">
                  Client on Your Firm&apos;s KovelAI
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.feature}>
                  <th scope="row" className="comparison-feature">
                    {r.feature}
                  </th>
                  <td className="risk-cell">{r.risk}</td>
                  <td className="safe-cell">{r.safe}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
