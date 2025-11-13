'use client';

import { PipelineStatus } from '../../components/PipelineStatus';

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Realtime telemetry</h2>
      <PipelineStatus />
    </div>
  );
}
