import { NextResponse } from 'next/server';

const metrics = [
  { id: 'ingestion', label: 'Ingestion Lag', value: 4, unit: 'minutes' },
  { id: 'summaries', label: 'Summaries / hr', value: 124, unit: 'events' },
  { id: 'alerts', label: 'Open Alerts', value: 1, unit: 'incidents' }
];

export async function GET() {
  return NextResponse.json(metrics);
}
