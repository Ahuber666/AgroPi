import { get } from '../../lib/api';

type RequestRow = {
  id: string;
  source: string;
  reason: string;
  status: string;
};

export default async function TakedownsPage() {
  const requests = await get<RequestRow[]>('/api/takedowns');
  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">Takedown Requests</h2>
      <div className="rounded border bg-white shadow">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-100">
              <th className="p-2 text-left">Source</th>
              <th className="p-2 text-left">Reason</th>
              <th className="p-2 text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            {requests.map((row) => (
              <tr key={row.id} className="border-b">
                <td className="p-2">{row.source}</td>
                <td className="p-2">{row.reason}</td>
                <td className="p-2">{row.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
