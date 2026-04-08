import { useState } from "react";
import AgentPanel from "./pages/AgentPanel";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import RunbookListPage from "./pages/RunbookListPage";
import RunbookReviewPage from "./pages/RunbookReviewPage";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [username, setUsername] = useState("");
  const [selectedAlertId, setSelectedAlertId] = useState<string | null>(null);
  const [selectedRunbookId, setSelectedRunbookId] = useState<string | null>(null);

  const handleLogin = (newToken: string, user: string) => {
    setToken(newToken);
    setUsername(user);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUsername("");
  };

  if (!token) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-mist">
        <LoginPage onLogin={handleLogin} />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-mist text-ink">
      <section className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-10">
        <header className="rounded-3xl bg-ink p-8 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-signal">RunbookAgent</p>
              <h1 className="mt-4 text-4xl font-semibold">AI-assisted incident diagnosis</h1>
            </div>
            <div className="flex items-center gap-4">
              {username && <span className="text-sm text-slate-300">{username}</span>}
              <button
                onClick={handleLogout}
                className="rounded-full border border-white/30 px-4 py-1 text-sm text-white"
              >
                Logout
              </button>
            </div>
          </div>
        </header>

        <DashboardPage onSelectAlert={setSelectedAlertId} />
        <AgentPanel alertId={selectedAlertId} />

        {selectedRunbookId ? (
          <RunbookReviewPage
            runbookId={selectedRunbookId}
            onBack={() => setSelectedRunbookId(null)}
          />
        ) : (
          <RunbookListPage onSelectRunbook={setSelectedRunbookId} />
        )}
      </section>
    </main>
  );
}
