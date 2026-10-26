import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "THREAD — Creative intelligence",
  description: "Explore how a creative project changes over time, with evidence you can inspect.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
