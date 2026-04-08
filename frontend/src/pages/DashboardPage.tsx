import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import AlertCard from "../components/AlertCard";

type Alert = {
  id: string;
  fingerprint: string;
  ruleName: string;
  category: string;
  severity: string;
  status: string;
  message: string;
  createdAt: string;
};

type DashboardPageProps = {
  onSelectAlert: (alertId: string) => void;
};

export default function DashboardPage({ onSelectAlert }: DashboardPageProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    try {
      const res = await apiClient.get("/alerts");
      setAlerts(res.data);
    } catch {
      // Fallback to demo data if API not available
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const triggerAlert = async (alertId: string) => {
    await apiClient.post(`/alerts/${alertId}/trigger`);
    onSelectAlert(alertId);
    fetchAlerts();
  };

  const createAlert = async () => {
    const res = await apiClient.post("/alerts", {
      ruleName: "mysql_pool_exhausted",
      category: "database",
      severity: "HIGH",
      message: "Connection pool usage at 96% (48/50) on service-a",
    });
    fetchAlerts();
    onSelectAlert(res.data.id);
  };

  return (
    <section className="rounded-3xl bg-white p-6 shadow-lg">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Alert Dashboard</h2>
          <p className="text-sm text-slate-600">
            {loading ? "Loading..." : `${alerts.length} alerts`}
          </p>
        </div>
        <button
          onClick={createAlert}
          className="rounded-full bg-signal px-4 py-2 text-sm font-semibold text-white"
        >
          Create Alert
        </button>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {alerts.map((alert) => (
          <AlertCard
            key={alert.id}
            title={alert.ruleName}
            severity={alert.severity}
            summary={alert.message}
            status={alert.status}
            onTrigger={() => triggerAlert(alert.id)}
          />
        ))}
      </div>
    </section>
  );
}
