'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SourceTable } from '../../components/SourceTable';

const client = new QueryClient();

export default function SourcesPage() {
  return (
    <QueryClientProvider client={client}>
      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold">Source Registry</h2>
          <p className="text-sm text-slate-500">Add, pause, or resume feeds.</p>
        </div>
        <SourceTable />
      </section>
    </QueryClientProvider>
  );
}
