"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { NotificationSettings } from "@/lib/types";
import { Loader2, Save, Mail, MessageSquare } from "lucide-react";

export default function NotificationsPage() {
  const [settings, setSettings] = useState<NotificationSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const fetchSettings = () => {
    api.auth.getNotificationSettings().then(setSettings).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { fetchSettings(); }, []);

  const update = async () => {
    if (!settings) return;
    setSaving(true); setSaved(false);
    try {
      await api.auth.updateNotificationSettings(settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) { alert(e instanceof Error ? e.message : "Failed to save"); }
    setSaving(false);
  };

  const set = (key: keyof NotificationSettings, val: string | number) =>
    setSettings((prev) => prev ? { ...prev, [key]: val } : prev);

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 size={20} className="animate-spin text-text-muted" /></div>;

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Notifications</h1>
          <p className="text-sm text-text-muted mt-1">Configure email and Slack notification channels</p>
        </div>
        <button onClick={update} disabled={saving || !settings} className="btn-primary text-xs flex items-center gap-1.5">
          {saving ? <Loader2 size={12} className="animate-spin" /> : <Save size={12} />}
          {saving ? "Saving..." : saved ? "Saved!" : "Save Settings"}
        </button>
      </div>

      {settings && (
        <>
          <div className="card p-4 space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-border">
              <Mail size={14} className="text-text-muted" />
              <h3 className="text-sm font-semibold text-text-primary">SMTP / Email</h3>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2 sm:col-span-1 space-y-1">
                <label className="text-xs text-text-muted">SMTP Host</label>
                <input value={settings.smtp_host} onChange={(e) => set("smtp_host", e.target.value)} placeholder="smtp.example.com" className="input text-sm w-full" />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-text-muted">Port</label>
                <input type="number" value={settings.smtp_port} onChange={(e) => set("smtp_port", parseInt(e.target.value) || 587)} className="input text-sm w-full" />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-text-muted">Username</label>
                <input value={settings.smtp_username} onChange={(e) => set("smtp_username", e.target.value)} placeholder="user@example.com" className="input text-sm w-full" />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-text-muted">Password</label>
                <input type="password" value={settings.smtp_password === "********" ? "" : settings.smtp_password} onChange={(e) => set("smtp_password", e.target.value)} placeholder="Leave blank to keep current" className="input text-sm w-full" />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-text-muted">From Address</label>
                <input value={settings.smtp_from} onChange={(e) => set("smtp_from", e.target.value)} placeholder="noreply@orqestra.ai" className="input text-sm w-full" />
              </div>
            </div>
          </div>

          <div className="card p-4 space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-border">
              <MessageSquare size={14} className="text-text-muted" />
              <h3 className="text-sm font-semibold text-text-primary">Slack</h3>
            </div>
            <div className="space-y-1">
              <label className="text-xs text-text-muted">Webhook URL</label>
              <input value={settings.slack_webhook_url === "********" ? "" : settings.slack_webhook_url} onChange={(e) => set("slack_webhook_url", e.target.value)} placeholder="https://hooks.slack.com/services/..." className="input text-sm w-full font-mono" />
              <p className="text-xs text-text-muted mt-1">Create an incoming webhook in your Slack workspace and paste the URL here.</p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
