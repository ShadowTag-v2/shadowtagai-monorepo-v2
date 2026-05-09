export function StatsBar() {
  const stats = [
    { value: "2,400+", label: "Law Firms", suffix: "" },
    { value: "$4.2M", label: "Queries Billed", suffix: "/mo" },
    { value: "99.97%", label: "Uptime SLA", suffix: "" },
    { value: "<200ms", label: "P95 Latency", suffix: "" },
  ];

  return (
    <section className="relative z-10 -mt-1">
      <div className="max-w-[1200px] mx-auto px-6">
        <div className="glass-card p-8 grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-2xl md:text-3xl font-bold gradient-text">
                {stat.value}
                <span className="text-sm text-[#8b949e]">{stat.suffix}</span>
              </div>
              <div className="text-sm text-[#8b949e] mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
