import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AnyAgent — Journey",
  description: "The self-updating progress journey for this codebase, from graded, evidence-backed deliveries.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
