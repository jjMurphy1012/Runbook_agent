import AlertCard from "../components/AlertCard";

const alerts = [
  {
    title: "mysql_pool_exhausted",
    severity: "HIGH",
    summary: "Connection pool usage at 96% on service-a",
  },
  {
    title: "cpu_high_load",
    severity: "HIGH",
    summary: "CPU usage at 98% for 15 minutes on payment-service",
  },
];

export default function DashboardPage() {
  return (
    <section className="rounded-3xl bg-white p-6 shadow-lg">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Alert Dashboard</h2>
          <p className="text-sm text-slate-600">Seed scenarios for the initial demo workflow.</p>
        </div>
        <button className="rounded-full bg-signal px-4 py-2 text-sm font-semibold text-white">
          Trigger Alert
        </button>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {alerts.map((alert) => (
          <AlertCard key={alert.title} {...alert} />
        ))}
      </div>
    </section>
  );
}
