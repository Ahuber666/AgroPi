'use client';

import { useQuery } from '@tanstack/react-query';

type Metric = {
  id: string;
  label: string;
  value: number;
  unit: string;
};

async function fetchMetrics(): Promise<Metric[]> {
  const response = await fetch('/api/metrics');
  if (!response.ok) {
    throw new Error('Failed to fetch metrics');
  }
  return response.json();
}

export function PipelineStatus() {
  const { data, isLoading } = useQuery({ queryKey: ['metrics'], queryFn: fetchMetrics, refetchInterval: 5000 });

  if (isLoading || !data) {
    return <p>Loading metrics…</p>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {data.map((metric) => (
        <div key={metric.id} className="rounded border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">{metric.label}</p>
          <p className="text-2xl font-semibold">{metric.value}</p>
          <p className="text-xs uppercase tracking-wide text-slate-400">{metric.unit}</p>
        </div>
      ))}
    </div>
  );
}
