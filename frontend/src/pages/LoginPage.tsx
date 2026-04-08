import { useState } from "react";
import { apiClient } from "../api/client";

type LoginPageProps = {
  onLogin: (token: string, username: string) => void;
};

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const endpoint = isRegister ? "/auth/register" : "/auth/login";
    try {
      const res = await apiClient.post(endpoint, { username, password });
      const { token, username: user } = res.data;
      localStorage.setItem("token", token);
      onLogin(token, user);
    } catch (err: any) {
      setError(err.response?.data?.message || "Authentication failed");
    }
  };

  return (
    <section className="mx-auto max-w-md rounded-3xl bg-white p-8 shadow-lg">
      <h2 className="text-2xl font-semibold">{isRegister ? "Register" : "Login"}</h2>
      <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="rounded-xl border border-slate-300 px-4 py-2"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="rounded-xl border border-slate-300 px-4 py-2"
        />
        {error && <p className="text-sm text-red-500">{error}</p>}
        <button type="submit" className="rounded-full bg-signal px-6 py-2 text-white font-semibold">
          {isRegister ? "Register" : "Login"}
        </button>
        <button
          type="button"
          onClick={() => setIsRegister(!isRegister)}
          className="text-sm text-slate-500 underline"
        >
          {isRegister ? "Already have an account? Login" : "Need an account? Register"}
        </button>
      </form>
    </section>
  );
}
