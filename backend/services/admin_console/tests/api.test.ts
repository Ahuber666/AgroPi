import { describe, expect, it } from 'vitest';
import { GET as getSources } from '../app/api/sources/route';

describe('sources API', () => {
  it('returns default sources', async () => {
    const response = await getSources();
    const payload = await response.json();
    expect(payload.length).toBeGreaterThan(0);
  });
});
