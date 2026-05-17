import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { IsolatedAnalytics } from "@/components/analytics/IsolatedAnalytics";
import { QueryProvider } from "@/components/QueryProvider";
import { Sidebar } from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ShadowTag-v2 Platform",
  description: "Autoresearch Swarm Intelligence Dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryProvider>
          <div className="flex h-screen">
            <Sidebar />
            <main className="flex-1 overflow-auto p-6">{children}</main>
          </div>
          <IsolatedAnalytics
            writeKey={process.env.NEXT_PUBLIC_SEGMENT_WRITE_KEY || "YOUR_WRITE_KEY"}
            backendUrl="http://localhost:8080"
          />
        </QueryProvider>
      </body>
    </html>
  );
}
