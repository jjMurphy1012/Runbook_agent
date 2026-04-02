import SSELogViewer from "../components/SSELogViewer";

export default function AgentPanel() {
  const mockMessages = [
    "[Triage] classify alert and read cache",
    "[Diagnostic] plan log_query + metrics_query",
    "[Remediation] simulate safe recovery steps",
    "[Postmortem] draft runbook for review",
  ];

  return (
    <section className="rounded-3xl bg-white p-6 shadow-lg">
      <h2 className="text-2xl font-semibold">Agent Trace</h2>
      <p className="mb-4 text-sm text-slate-600">Live SSE output will render here once the backend is wired.</p>
      <SSELogViewer messages={mockMessages} />
    </section>
  );
}
