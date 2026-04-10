import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@packages/ui/dark-luxury.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "HeadFadeAi | Gamified Turing Test",
  description: "Can you tell what is real?",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-black text-white antialiased`}>{children}</body>
    </html>
  );
}
