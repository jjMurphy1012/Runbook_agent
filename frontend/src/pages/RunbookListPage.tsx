import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

type Runbook = {
  id: string;
  title: string;
  rootCause: string | null;
  version: number;
  status: string;
  content: string | null;
  updatedAt: string;
};

type RunbookListPageProps = {
  onSelectRunbook: (id: string) => void;
};

const statusBadge: Record<string, string> = {
  DRAFT: "bg-yellow-100 text-yellow-800",
  PENDING_REVIEW: "bg-blue-100 text-blue-800",
  APPROVED: "bg-green-100 text-green-800",
  ARCHIVED: "bg-slate-100 text-slate-600",
};

export default function RunbookListPage({ onSelectRunbook }: RunbookListPageProps) {
  const [runbooks, setRunbooks] = useState<Runbook[]>([]);

  useEffect(() => {
    apiClient.get("/runbooks").then((res) => setRunbooks(res.data)).catch(() => {});
  }, []);

  return (
    <section className="rounded-3xl bg-white p-6 shadow-lg">
      <h2 className="text-2xl font-semibold">Runbook Library</h2>
      <p className="mt-1 text-sm text-slate-600">
        {runbooks.length} runbooks
      </p>
      <div className="mt-4 grid gap-3">
        {runbooks.map((rb) => (
          <div
            key={rb.id}
            onClick={() => onSelectRunbook(rb.id)}
            className="cursor-pointer rounded-2xl border border-slate-200 p-4 transition hover:border-trace"
          >
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">{rb.title}</h3>
              <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusBadge[rb.status] || "bg-slate-100"}`}>
                {rb.status}
              </span>
            </div>
            {rb.rootCause && (
              <p className="mt-2 text-sm text-slate-600">{rb.rootCause}</p>
            )}
            <p className="mt-1 text-xs text-slate-400">v{rb.version}</p>
          </div>
        ))}
        {runbooks.length === 0 && (
          <p className="text-sm text-slate-500">
            No runbooks yet. Run an agent workflow to generate one.
          </p>
        )}
      </div>
    </section>
  );
}
