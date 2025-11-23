import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Solar PV LLM AI',
  description: 'AI-powered Solar PV system with LLM capabilities for beginners to experts',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 antialiased">
        <main className="flex min-h-screen flex-col">
          {children}
        </main>
      </body>
    </html>
  );
}
