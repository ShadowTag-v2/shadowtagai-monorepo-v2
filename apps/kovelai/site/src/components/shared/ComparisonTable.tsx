export default function ComparisonTable() {
  const rows = [
    {
      feature: 'Client web searches',
      risk: '⚠️ Discoverable by opposing counsel',
      safe: '✅ Shielded under privilege',
    },
    {
      feature: 'AI chatbot conversations',
      risk: '⚠️ Subpoenaed and weaponized',
      safe: '✅ Protected via Kovel Doctrine',
    },
    {
      feature: 'Client pre-trial anxiety',
      risk: '⚠️ Panic searches create discoverable evidence',
      safe: '✅ Client relaxes, recalls facts safely',
    },
    {
      feature: 'Data retention',
      risk: '⚠️ Browser logs everywhere',
      safe: '✅ Zero retention (RAM only)',
    },
    {
      feature: 'Attorney awareness',
      risk: '❌ Ambushed by random client searches',
      safe: '✅ Full real-time visibility',
    },
    {
      feature: 'First legal opinion',
      risk: '❌ Other side sees it first',
      safe: '✅ Attorney gives the first opinion',
    },
    {
      feature: 'Billing',
      risk: '$0 (unbilled panic calls)',
      safe: '✅ Auto-billed via client credit card',
    },
  ];

  return (
    <section className="py-20 md:py-28" id="comparison">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">Why CounselConduit</div>
        <h2 className="section-title">Your Client Without CounselConduit vs. With</h2>
        <p className="section-desc mb-10">
          Every day without privilege protection is another day opposing counsel can mine your
          clients&apos; web and AI activity and use it against them at trial.
        </p>
        <div className="overflow-x-auto glass-card p-0">
          <table className="comparison-table">
            <thead>
              <tr>
                <th scope="col">Feature</th>
                <th scope="col" className="text-error">
                  Client Unprotected
                </th>
                <th scope="col" className="text-blue">
                  Client Shielded by CounselConduit
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
