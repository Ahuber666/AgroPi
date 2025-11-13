import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { email } = await request.json();
  if (!email.endsWith('@dailybrief.ai')) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 403 });
  }
  return NextResponse.json({ token: 'mock-admin-token', email });
}
