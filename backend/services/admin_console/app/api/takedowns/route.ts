import { NextResponse } from 'next/server';

const requests = [
  { id: 'td-1', source: 'Publisher', reason: 'Copyright claim', status: 'pending' }
];

export async function GET() {
  return NextResponse.json(requests);
}

export async function POST(request: Request) {
  const payload = await request.json();
  requests.push({ ...payload, status: 'pending' });
  return NextResponse.json(requests, { status: 201 });
}
