const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/**
 * Placeholder skeleton page — real UI comes in Phase 6.
 */
export default function App() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-4">
      <main className="max-w-lg rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-slate-500">Task 1 skeleton</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-900">Sneaker Recommendation System</h1>
        <p className="mt-3 text-slate-600">
          Frontend is running. Business pages and forms will be added in later tasks.
        </p>
        <p className="mt-4 text-sm text-slate-500">
          API base: <code className="rounded bg-slate-100 px-1">{API_BASE_URL}</code>
        </p>
      </main>
    </div>
  );
}
