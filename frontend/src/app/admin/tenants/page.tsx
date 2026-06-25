"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { TenantInfo } from "@/lib/types";
import { Loader2, Plus, Pencil, Trash2, X } from "lucide-react";

export default function AdminTenantsPage() {
  const [tenants, setTenants] = useState<TenantInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    (async () => {
      try { setTenants(await api.auth.listTenants()); } catch {}
      setLoading(false);
    })();
  }, []);

  const reloadTenants = () => api.auth.listTenants().then(setTenants).catch(() => {});

  const resetForm = () => { setName(""); setSlug(""); setEditId(null); setShowForm(false); };
  const startEdit = (t: TenantInfo) => { setName(t.name); setSlug(t.slug); setEditId(t.id); setShowForm(true); };

  const handleSave = async () => {
    if (!name.trim() || !slug.trim()) return;
    setSaving(true);
    try {
      if (editId) await api.auth.updateTenant(editId, { name: name.trim(), slug: slug.trim() });
      else await api.auth.createTenant({ name: name.trim(), slug: slug.trim() });
      resetForm(); await reloadTenants();
    } catch (e) { alert(e instanceof Error ? e.message : "Failed"); }
    setSaving(false);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this tenant? This cannot be undone.")) return;
    try { await api.auth.deleteTenant(id); await reloadTenants(); }
    catch (e) { alert(e instanceof Error ? e.message : "Failed"); }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 size={20} className="animate-spin text-text-muted" /></div>;

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Tenants</h1>
          <p className="text-sm text-text-muted mt-1">Manage multi-tenancy configuration</p>
        </div>
        <button onClick={() => { resetForm(); setShowForm(true); }} className="btn-primary text-xs flex items-center gap-1.5">
          <Plus size={14} /> Add Tenant
        </button>
      </div>

      {showForm && (
        <div className="card p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold">{editId ? "Edit Tenant" : "New Tenant"}</h3>
            <button onClick={resetForm} className="text-text-muted hover:text-text-primary"><X size={14} /></button>
          </div>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Tenant name" className="input text-sm w-full" />
          <input value={slug} onChange={(e) => setSlug(e.target.value.toLowerCase().replace(/\s+/g, "-"))} placeholder="tenant-slug" className="input text-sm w-full font-mono" />
          <div className="flex justify-end gap-2">
            <button onClick={resetForm} className="btn-ghost text-xs">Cancel</button>
            <button onClick={handleSave} disabled={saving || !name.trim() || !slug.trim()} className="btn-primary text-xs flex items-center gap-1.5">
              {saving && <Loader2 size={12} className="animate-spin" />}
              {editId ? "Update" : "Create"}
            </button>
          </div>
        </div>
      )}

      <div className="card p-0 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wider px-4 py-3">Name</th>
              <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wider px-4 py-3">Slug</th>
              <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wider px-4 py-3 hidden md:table-cell">Created</th>
              <th className="text-right px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {tenants.map((t) => (
              <tr key={t.id} className="hover:bg-surface-4/50">
                <td className="px-4 py-3 text-sm text-text-primary">{t.name}</td>
                <td className="px-4 py-3"><code className="text-xs bg-surface-4 px-1.5 py-0.5 rounded">{t.slug}</code></td>
                <td className="px-4 py-3 text-xs text-text-muted hidden md:table-cell">{t.created_at ? new Date(t.created_at).toLocaleDateString() : "--"}</td>
                <td className="px-4 py-3 text-right">
                  <button onClick={() => startEdit(t)} className="btn-ghost p-1 mr-1"><Pencil size={12} /></button>
                  <button onClick={() => handleDelete(t.id)} disabled={t.slug === "default"} className="btn-ghost p-1 text-red-400 disabled:opacity-30"><Trash2 size={12} /></button>
                </td>
              </tr>
            ))}
            {tenants.length === 0 && (
              <tr><td colSpan={4} className="px-4 py-8 text-center text-sm text-text-muted">No tenants yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
