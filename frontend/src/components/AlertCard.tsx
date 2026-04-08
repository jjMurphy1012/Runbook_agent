type AlertCardProps = {
  title: string;
  severity: string;
  summary: string;
  status?: string;
  onTrigger?: () => void;
};

const severityColor: Record<string, string> = {
  LOW: "bg-green-100 text-green-800",
  MEDIUM: "bg-yellow-100 text-yellow-800",
  HIGH: "bg-orange-100 text-orange-800",
  CRITICAL: "bg-red-100 text-red-800",
};

const statusColor: Record<string, string> = {
  PENDING: "bg-slate-100 text-slate-700",
  PROCESSING: "bg-blue-100 text-blue-700",
  RESOLVED: "bg-green-100 text-green-700",
  ESCALATED: "bg-red-100 text-red-700",
};

export default function AlertCard({ title, severity, summary, status, onTrigger }: AlertCardProps) {
  return (
    <article className="rounded-2xl border border-slate-200 p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{title}</h3>
        <div className="flex gap-2">
          {status && (
            <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusColor[status] || "bg-slate-100"}`}>
              {status}
            </span>
          )}
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${severityColor[severity] || "bg-slate-100"}`}>
            {severity}
          </span>
        </div>
      </div>
      <p className="mt-3 text-sm text-slate-600">{summary}</p>
      {onTrigger && status === "PENDING" && (
        <button
          onClick={onTrigger}
          className="mt-3 rounded-full bg-trace px-3 py-1 text-xs font-semibold text-white"
        >
          Run Agent
        </button>
      )}
    </article>
  );
}
