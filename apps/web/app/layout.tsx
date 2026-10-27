import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SHOWME — Demonstrations into understanding",
  description: "Showme learns a physical procedure from a demonstration, then helps people perform and explore it.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
