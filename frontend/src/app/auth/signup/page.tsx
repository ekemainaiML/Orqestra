"use client";
import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { Loader2, UserPlus, ChefHat, ArrowLeft } from "lucide-react";

export default function SignupPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError("");

      if (password !== confirm) {
        setError("Passwords do not match");
        return;
      }
      if (username.trim().length < 2) {
        setError("Username must be at least 2 characters");
        return;
      }
      if (password.length < 4) {
        setError("Password must be at least 4 characters");
        return;
      }

      setLoading(true);
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${apiBase}/auth/signup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: username.trim(), password }),
        });
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(
            (body as { detail?: string }).detail || "Signup failed"
          );
        }
        setSuccess(true);
        await login(username.trim(), password);
        setTimeout(() => router.push("/"), 500);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Signup failed");
      } finally {
        setLoading(false);
      }
    },
    [username, password, confirm, login, router]
  );

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center mx-auto mb-4">
            <UserPlus size={24} className="text-emerald-400" />
          </div>
          <h2 className="text-lg font-bold text-text-primary mb-1">
            Account Created
          </h2>
          <p className="text-sm text-text-muted">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface">
      <div className="w-full max-w-sm mx-auto p-6">
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-brand-500 flex items-center justify-center mb-4">
            <ChefHat size={24} className="text-gray-950" />
          </div>
          <h1 className="text-xl font-bold text-text-primary">Create Account</h1>
          <p className="text-sm text-text-muted mt-1">
            Join the Orqestra platform
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="label">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input"
              placeholder="Choose a username"
              required
              autoFocus
            />
          </div>
          <div>
            <label htmlFor="password" className="label">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
              placeholder="At least 4 characters"
              required
            />
          </div>
          <div>
            <label htmlFor="confirm" className="label">
              Confirm Password
            </label>
            <input
              id="confirm"
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              className="input"
              placeholder="Repeat password"
              required
            />
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !username || !password || !confirm}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {loading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <UserPlus size={16} />
            )}
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="text-xs text-text-muted text-center mt-6">
          Already have an account?{" "}
          <Link
            href="/auth/login"
            className="text-brand-400 hover:text-brand-300 underline"
          >
            Sign in
          </Link>
        </p>

        <div className="mt-4 text-center">
          <Link
            href="/auth/login"
            className="btn-ghost inline-flex items-center gap-1.5 text-xs"
          >
            <ArrowLeft size={12} />
            Back to login
          </Link>
        </div>
      </div>
    </div>
  );
}
