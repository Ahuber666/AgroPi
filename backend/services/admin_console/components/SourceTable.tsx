'use client';

import { useQuery } from '@tanstack/react-query';

export type Source = {
  id: string;
  name: string;
  locale: string;
  status: 'active' | 'paused';
  lastFetched: string;
};

async function fetchSources(): Promise<Source[]> {
  const response = await fetch('/api/sources');
  if (!response.ok) {
    throw new Error('Failed to load sources');
  }
  return response.json();
}

export function SourceTable() {
  const { data, isLoading, error } = useQuery({ queryKey: ['sources'], queryFn: fetchSources });

  if (isLoading) {
    return <p>Loading sources…</p>;
  }

  if (error || !data) {
    return <p className="text-red-600">Failed to load sources.</p>;
  }

  return (
    <table className="w-full border-collapse text-sm">
      <thead>
        <tr className="bg-slate-100 text-left">
          <th className="p-2">Name</th>
          <th className="p-2">Locale</th>
          <th className="p-2">Status</th>
          <th className="p-2">Last Fetch</th>
        </tr>
      </thead>
      <tbody>
        {data.map((source) => (
          <tr key={source.id} className="border-b">
            <td className="p-2 font-medium">{source.name}</td>
            <td className="p-2">{source.locale}</td>
            <td className="p-2">
              <span className={source.status === 'active' ? 'text-green-600' : 'text-amber-600'}>{source.status}</span>
            </td>
            <td className="p-2">{source.lastFetched}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
