type AlertCardProps = {
  title: string;
  severity: string;
  summary: string;
};

export default function AlertCard({ title, severity, summary }: AlertCardProps) {
  return (
    <article className="rounded-2xl border border-slate-200 p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{title}</h3>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold">{severity}</span>
      </div>
      <p className="mt-3 text-sm text-slate-600">{summary}</p>
    </article>
  );
}
