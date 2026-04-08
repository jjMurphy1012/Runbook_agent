export default function RunbookDiffView() {
  return (
    <div className="rounded-2xl border border-dashed border-trace p-4">
      <h3 className="font-semibold">Draft Diff</h3>
      <p className="mt-2 text-sm text-slate-600">
        Proposed changes will appear here when comparing runbook versions.
      </p>
    </div>
  );
}
