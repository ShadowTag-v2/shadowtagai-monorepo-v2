export default function StatsBar() {
  const stats = [
    { value: '100%', label: 'Searches Privileged' },
    { value: '24/7', label: 'Client Access' },
    { value: 'Real-Time', label: 'Attorney Visibility' },
    { value: 'Auto', label: 'Credit Card Billing', accent: true },
  ];

  return (
    <section className="py-8 border-y border-[rgba(77,70,58,0.15)]">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {stats.map((s) => (
            <div key={s.label}>
              <div
                className={`text-2xl md:text-3xl font-extrabold tracking-tight mb-1 ${
                  s.accent ? 'text-secondary-text' : 'text-gold'
                }`}
              >
                {s.value}
              </div>
              <div className="text-xs uppercase tracking-[0.05em] text-[#998f81]">{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
