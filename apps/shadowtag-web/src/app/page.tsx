export default function Home() {
  return (
    <main className="container">
      <div
        className="animate-fade-in delay-1"
        style={{ textAlign: 'center', marginBottom: '4rem' }}
      >
        <h1>
          ShadowTag <span>Omega</span>
        </h1>
        <p>Tactical Oversight & Identity Control</p>
      </div>

      <div className="grid">
        {/* Module 1: Intelligence */}
        <section className="glass-panel animate-fade-in delay-2">
          <h2>Database Search</h2>
          <p style={{ margin: '1rem 0' }}>
            Query the Vector Hippocampus for targets, incidents, or telemetry.
          </p>
          <a href="/search" className="action-button" style={{ marginTop: '1rem', width: '100%' }}>
            Initiate Search
          </a>
        </section>

        {/* Module 2: The Swarm */}
        <section className="glass-panel animate-fade-in delay-3">
          <h2>Swarm Deployment</h2>
          <p style={{ margin: '1rem 0' }}>
            Dispatch Jetski agents or the Autoresearch pipeline to active tasks.
          </p>
          <a
            href="/swarm"
            className="action-button"
            style={{ marginTop: '1rem', width: '100%', filter: 'hue-rotate(60deg)' }}
          >
            Open Cockpit
          </a>
        </section>

        {/* Module 3: Threat Radar */}
        <section className="glass-panel animate-fade-in delay-3">
          <h2>System Telemetry</h2>
          <p style={{ margin: '1rem 0' }}>
            Monitor AlloyDB load, ANE memory cache, and active Temporal workflows.
          </p>
          <a
            href="/metrics"
            className="action-button"
            style={{ marginTop: '1rem', width: '100%', filter: 'hue-rotate(280deg)' }}
          >
            View Dashboard
          </a>
        </section>
      </div>

      <footer style={{ marginTop: 'auto', paddingTop: '4rem', opacity: 0.4, fontSize: '0.9rem' }}>
        God Mode Active • LTV:CAC ≥ 4.0 Verification • Antigravity v4.0
      </footer>
    </main>
  );
}
