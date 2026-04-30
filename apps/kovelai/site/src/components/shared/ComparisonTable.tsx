export default function ComparisonTable() {
  const rows = [
    { feature: 'Client web searches', risk: '⚠️ Discoverable', safe: '✅ Privileged' },
    {
      feature: 'AI chatbot conversations',
      risk: '⚠️ Subpoena target',
      safe: '✅ Shielded under Kovel',
    },
    {
      feature: 'After-hours client inquiries',
      risk: '❌ Lost to voicemail',
      safe: '✅ Captured & retained',
    },
    {
      feature: 'Data retention',
      risk: '⚠️ Browser logs everywhere',
      safe: '✅ Zero retention (RAM only)',
    },
    {
      feature: 'Revenue per interaction',
      risk: '$0 (unbilled panic calls)',
      safe: '$50–$250/session (billable)',
    },
    { feature: 'Paralegal cost for intake', risk: '$45–$75/hour', safe: '$0 (automated)' },
    {
      feature: 'Compliance posture',
      risk: '❌ Hope-based',
      safe: '✅ SOC 2 audit-ready, HIPAA-supportive',
    },
  ];

  return (
    <section className="py-20 md:py-28" id="comparison">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">Why KovelAI</div>
        <h2 className="section-title">KovelAI vs. Doing Nothing</h2>
        <p className="section-desc mb-10">
          Every day without privilege protection is another day opposing counsel can mine your
          clients&apos; digital footprint.
        </p>
        <div className="overflow-x-auto glass-card p-0">
          <table className="comparison-table">
            <thead>
              <tr>
                <th scope="col">Feature</th>
                <th scope="col" className="text-error">
                  Without KovelAI
                </th>
                <th scope="col" className="text-blue">
                  Shielded by Attorney-Client Privilege
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
