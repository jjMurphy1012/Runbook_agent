import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

type RunbookReviewProps = {
  runbookId: string | null;
  onBack: () => void;
};

type Runbook = {
  id: string;
  title: string;
  rootCause: string | null;
  version: number;
  status: string;
  content: string | null;
  updatedAt: string;
};

export default function RunbookReviewPage({ runbookId, onBack }: RunbookReviewProps) {
  const [runbook, setRunbook] = useState<Runbook | null>(null);

  useEffect(() => {
    if (!runbookId) return;
    apiClient.get(`/runbooks/${runbookId}`).then((res) => setRunbook(res.data)).catch(() => {});
  }, [runbookId]);

  if (!runbookId || !runbook) {
    return null;
  }

  const handleApprove = async () => {
    const res = await apiClient.post(`/runbooks/${runbookId}/approve`);
    setRunbook(res.data);
  };

  const handleReject = async () => {
    const res = await apiClient.post(`/runbooks/${runbookId}/reject`);
    setRunbook(res.data);
  };

  return (
    <section className="rounded-3xl bg-white p-6 shadow-lg">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <button onClick={onBack} className="text-sm text-trace underline">
            Back to list
          </button>
          <h2 className="mt-2 text-2xl font-semibold">{runbook.title}</h2>
          <p className="text-sm text-slate-600">
            v{runbook.version} &middot; {runbook.status}
          </p>
        </div>
        {(runbook.status === "DRAFT" || runbook.status === "PENDING_REVIEW") && (
          <div className="flex gap-2">
            <button
              onClick={handleApprove}
              className="rounded-full bg-green-600 px-4 py-2 text-sm font-semibold text-white"
            >
              Approve
            </button>
            <button
              onClick={handleReject}
              className="rounded-full bg-red-600 px-4 py-2 text-sm font-semibold text-white"
            >
              Reject
            </button>
          </div>
        )}
      </div>
      {runbook.rootCause && (
        <div className="mb-4 rounded-xl bg-orange-50 p-3 text-sm">
          <strong>Root Cause:</strong> {runbook.rootCause}
        </div>
      )}
      <div className="prose prose-sm max-w-none rounded-2xl bg-slate-50 p-4">
        <pre className="whitespace-pre-wrap text-sm">{runbook.content || "No content"}</pre>
      </div>
    </section>
  );
}
