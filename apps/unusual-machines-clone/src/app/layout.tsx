import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Home - Unusual Machines',
  description:
    'Unusual Machines, Inc. (NYSE: UMAC) — Here to serve the American drone industry. Investor Relations.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          rel="icon"
          href="https://cdn-sites-assets.mziq.com/wp-content/themes/mziq_unusual_machines/img/favicon/favicon.ico"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
