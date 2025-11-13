import { get } from '../../lib/api';

type EventRow = {
  id: string;
  title: string;
  pipelineStage: string;
  disputed: boolean;
};

async function listEvents(): Promise<EventRow[]> {
  return get<EventRow[]>('http://localhost:8110/slates?locale=en-US&topics=world');
}

export default async function EventsPage() {
  const rows = await listEvents();
  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">Event Monitoring</h2>
      <div className="rounded border bg-white shadow">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-100 text-left">
              <th className="p-2">Event</th>
              <th className="p-2">Stage</th>
              <th className="p-2">Disputed</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-b">
                <td className="p-2">{row.title}</td>
                <td className="p-2">{row.pipelineStage}</td>
                <td className="p-2">{row.disputed ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
