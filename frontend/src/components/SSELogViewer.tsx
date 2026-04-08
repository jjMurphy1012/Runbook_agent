import type { SSEMessage } from "../hooks/useSSE";

type SSELogViewerProps = {
  messages: SSEMessage[];
  connected: boolean;
};

const stageLabel: Record<string, string> = {
  triage: "Triage",
  evidence_collection: "Evidence Collection",
  diagnostic: "Diagnostic",
  diagnostic_reflection: "Reflection",
  remediation: "Remediation",
  postmortem: "Postmortem",
  complete: "Complete",
  alert_created: "Alert Created",
};

export default function SSELogViewer({ messages, connected }: SSELogViewerProps) {
  return (
    <div className="rounded-2xl bg-ink p-4 text-sm text-slate-100">
      <div className="mb-2 flex items-center gap-2">
        <span className={`h-2 w-2 rounded-full ${connected ? "bg-green-400" : "bg-slate-500"}`} />
        <span className="text-xs text-slate-400">
          {connected ? "Connected" : "Disconnected"}
        </span>
      </div>
      {messages.length === 0 ? (
        <p className="py-4 text-center text-slate-500">
          Select an alert and click "Run Agent" to see live traces
        </p>
      ) : (
        messages.map((msg, i) => (
          <div key={i} className="border-b border-white/10 py-2 last:border-b-0">
            <span className="mr-2 inline-block rounded bg-trace/20 px-2 py-0.5 text-xs text-trace">
              {stageLabel[msg.event] || msg.event}
            </span>
            <span className="text-slate-300">{msg.data}</span>
          </div>
        ))
      )}
    </div>
  );
}
