import { TestShowcase } from '@/components/TestShowcase';

export const metadata = {
  title: 'E2E Testing Showcase - MedGemma',
  description: 'Interactive showcase for testing Playwright E2E tests',
};

export default function TestShowcasePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <TestShowcase />
    </main>
  );
}
