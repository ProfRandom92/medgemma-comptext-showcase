import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'MedGemma × CompText | Healthcare AI Showcase',
  description:
    'Interactive showcase: Privacy-first multi-agent healthcare AI with 94% token reduction. Solving the context bottleneck in clinical diagnostics.',
  keywords: [
    'healthcare AI',
    'compression',
    'medical LLM',
    'privacy-first',
    'edge computing',
    'clinical diagnostics',
  ],
  authors: [{ name: 'MedGemma Challenge Team' }],
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="theme-color" content="#0f172a" />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
