import './globals.css';
import type { ReactNode } from 'react';

export const metadata = {
  title: 'DailyBrief Admin Console',
  description: 'Source registry, ingestion, summarization, and takedown operations',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <header className="border-b bg-white">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
            <div>
              <h1 className="text-xl font-semibold">DailyBrief Admin</h1>
              <p className="text-sm text-slate-500">Ingestion and policy operations</p>
            </div>
            <nav className="flex gap-4 text-sm">
              <a href="/dashboard" className="hover:text-blue-600">
                Dashboard
              </a>
              <a href="/sources" className="hover:text-blue-600">
                Sources
              </a>
              <a href="/events" className="hover:text-blue-600">
                Events
              </a>
              <a href="/takedowns" className="hover:text-blue-600">
                Takedowns
              </a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
