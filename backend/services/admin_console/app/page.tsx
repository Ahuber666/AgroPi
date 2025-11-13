import Link from 'next/link';

export default function LandingPage() {
  return (
    <section className="space-y-6">
      <div className="rounded-lg bg-white p-6 shadow">
        <h2 className="text-2xl font-semibold">Welcome back, Admin</h2>
        <p className="text-slate-600">Jump back into your workflow.</p>
        <div className="mt-4 flex gap-4">
          <Link href="/dashboard" className="rounded bg-blue-600 px-4 py-2 text-white">
            View Dashboard
          </Link>
          <Link href="/sources" className="rounded border border-blue-600 px-4 py-2 text-blue-600">
            Manage Sources
          </Link>
        </div>
      </div>
    </section>
  );
}
