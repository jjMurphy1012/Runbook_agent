import RunbookDiffView from "../components/RunbookDiffView";

export default function RunbookListPage() {
  return (
    <section className="grid gap-4 rounded-3xl bg-white p-6 shadow-lg md:grid-cols-[1.2fr,0.8fr]">
      <div>
        <h2 className="text-2xl font-semibold">Runbook Library</h2>
        <p className="mt-2 text-sm text-slate-600">
          Approved and draft runbooks will be listed here after postmortem generation.
        </p>
        <div className="mt-4 rounded-2xl border border-slate-200 p-4">
          <h3 className="font-semibold">mysql_slow_query</h3>
          <p className="mt-2 text-sm text-slate-600">
            Diagnose saturation, inspect connection lifecycle, recycle pods only after safe fallback.
          </p>
        </div>
      </div>
      <RunbookDiffView />
    </section>
  );
}
