import SSELogViewer from "../components/SSELogViewer";
import { useSSE } from "../hooks/useSSE";

type AgentPanelProps = {
  alertId: string | null;
};

export default function AgentPanel({ alertId }: AgentPanelProps) {
  const sseUrl = alertId ? `http://localhost:8080/api/stream/${alertId}` : null;
  const { messages, connected, clear } = useSSE(sseUrl);

  return (
    <section className="rounded-3xl bg-white p-6 shadow-lg">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Agent Trace</h2>
          <p className="text-sm text-slate-600">
            {alertId
              ? `Streaming events for alert ${alertId.substring(0, 8)}...`
              : "Select an alert to begin"}
          </p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clear}
            className="rounded-full border border-slate-300 px-3 py-1 text-xs"
          >
            Clear
          </button>
        )}
      </div>
      <SSELogViewer messages={messages} connected={connected} />
    </section>
  );
}
