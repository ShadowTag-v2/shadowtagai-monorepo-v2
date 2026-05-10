import Link from 'next/link';

export default function NotFound() {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        fontFamily: "'Inter', system-ui, sans-serif",
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
        color: '#fff',
        padding: '24px',
        textAlign: 'center',
      }}
    >
      <span
        style={{
          fontSize: '72px',
          fontWeight: 800,
          lineHeight: 1,
          background: 'linear-gradient(135deg, #667eea, #764ba2)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}
      >
        404
      </span>
      <h2
        style={{
          fontSize: '20px',
          fontWeight: 600,
          margin: '16px 0 8px',
          color: 'rgba(255,255,255,0.9)',
        }}
      >
        Page Not Found
      </h2>
      <p
        style={{
          fontSize: '14px',
          color: 'rgba(255,255,255,0.5)',
          maxWidth: '360px',
          lineHeight: 1.6,
        }}
      >
        The page you&apos;re looking for doesn&apos;t exist or has been moved.
      </p>
      <Link
        href="/"
        style={{
          marginTop: '24px',
          padding: '12px 28px',
          background: 'linear-gradient(135deg, #667eea, #764ba2)',
          color: '#fff',
          textDecoration: 'none',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: 600,
          letterSpacing: '0.02em',
          transition: 'opacity 0.2s',
        }}
      >
        Return Home
      </Link>
    </div>
  );
}
