import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "TerraLens — Satellite Land Intelligence",
  description:
    "AI-powered satellite imagery classification with explainability (Grad-CAM) and temporal change detection. Built on EuroSAT with CNN_LeakyReLU_Skip (93.16% accuracy).",
  authors: [
    { name: "Rajvardhan Patil" },
    { name: "Adwait Desai" },
  ],
};

export const viewport: Viewport = {
  themeColor: "#020817",
  colorScheme: "dark",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="h-full">{children}</body>
    </html>
  );
}
