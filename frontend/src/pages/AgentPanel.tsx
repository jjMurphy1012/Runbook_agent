import { useEffect, useState } from "react";
import { apiClient, API_BASE_URL } from "../api/client";
import SSELogViewer from "../components/SSELogViewer";
import { useSSE } from "../hooks/useSSE";

type AgentPanelProps = {
  alertId: string | null;
};

export default function AgentPanel({ alertId }: AgentPanelProps) {
  const [sseUrl, setSseUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!alertId) {
      setSseUrl(null);
      return;
    }
    let cancelled = false;
    apiClient
      .post<{ token: string }>(`/stream/token/${alertId}`)
      .then((res) => {
        if (!cancelled) {
          setSseUrl(
            `${API_BASE_URL}/api/stream/${alertId}?token=${encodeURIComponent(res.data.token)}`,
          );
        }
      })
      .catch(() => {
        if (!cancelled) setSseUrl(null);
      });
    return () => {
      cancelled = true;
    };
  }, [alertId]);

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
