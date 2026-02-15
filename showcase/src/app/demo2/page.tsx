import { Demo2MultiPatient } from '@/components/Demo2MultiPatient';

export const metadata = {
  title: 'Demo 2: Hospital Workflow - MedGemma Showcase',
  description: 'Multi-patient batch processing with real-world clinical scenarios',
};

export default function Demo2Page() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <Demo2MultiPatient />
    </main>
  );
}
