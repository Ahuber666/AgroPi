import { NextResponse } from 'next/server';

const sources = [
  { id: 'nyt', name: 'New York Times', locale: 'en-US', status: 'active', lastFetched: '2m ago' },
  { id: 'guardian', name: 'The Guardian', locale: 'en-GB', status: 'active', lastFetched: '5m ago' },
  { id: 'el-pais', name: 'El País', locale: 'es-ES', status: 'paused', lastFetched: '10m ago' }
];

export async function GET() {
  return NextResponse.json(sources);
}

export async function POST(request: Request) {
  const payload = await request.json();
  sources.push({ ...payload, lastFetched: 'pending', status: 'active' });
  return NextResponse.json(sources, { status: 201 });
}
