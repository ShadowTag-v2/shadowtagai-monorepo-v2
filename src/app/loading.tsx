export default function GlobalLoading() {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
        <div
          style={{
            width: '40px',
            height: '40px',
            border: '3px solid rgba(255,255,255,0.1)',
            borderTop: '3px solid #fff',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
          }}
        />
        <span
          style={{
            color: 'rgba(255,255,255,0.5)',
            fontSize: '13px',
            fontFamily: "'Inter', system-ui, sans-serif",
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
          }}
        >
          Loading
        </span>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    </div>
  );
}
