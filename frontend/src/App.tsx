import AgentPanel from "./pages/AgentPanel";
import DashboardPage from "./pages/DashboardPage";
import RunbookListPage from "./pages/RunbookListPage";

export default function App() {
  return (
    <main className="min-h-screen bg-mist text-ink">
      <section className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-10">
        <header className="rounded-3xl bg-ink p-8 text-white shadow-xl">
          <p className="text-sm uppercase tracking-[0.3em] text-signal">RunbookAgent</p>
          <h1 className="mt-4 text-4xl font-semibold">AI-assisted incident diagnosis scaffold</h1>
          <p className="mt-3 max-w-3xl text-sm text-slate-200">
            Initial UI shell for alert triage, live multi-agent traces, and runbook review.
          </p>
        </header>
        <DashboardPage />
        <AgentPanel />
        <RunbookListPage />
      </section>
    </main>
  );
}
