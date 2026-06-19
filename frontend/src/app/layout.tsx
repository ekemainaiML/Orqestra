import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Orqestra — AI Workforce Platform",
  description:
    "Multi-agent organizational decision-making platform powered by Qwen",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-gray-950">
      <body className="h-full text-gray-100">{children}</body>
    </html>
  );
}
