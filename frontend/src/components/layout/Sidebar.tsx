"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Library,
  Plus,
  ChefHat,
  ShieldCheck,
  Settings2,
} from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/demo", label: "Demo Library", icon: Library },
  { href: "/cases/new", label: "New Request", icon: Plus },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-[240px] bg-surface-2 border-r border-border flex flex-col z-30">
      <div className="p-5 border-b border-border">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center group-hover:bg-brand-400 transition-colors">
            <ChefHat size={18} className="text-gray-950" />
          </div>
          <div>
            <span className="font-bold text-base text-text-primary tracking-tight">
              Orqestra
            </span>
            <span className="block text-[10px] text-text-muted uppercase tracking-widest font-medium">
              AI Workforce
            </span>
          </div>
        </Link>
      </div>

      <nav className="flex-1 p-3 space-y-0.5">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const isActive =
            href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "bg-brand-500/10 text-brand-400 border border-brand-500/20"
                  : "text-text-secondary hover:text-text-primary hover:bg-surface-3 border border-transparent"
              }`}
            >
              <Icon size={18} />
              <span>{label}</span>
              {isActive && (
                <div className="ml-auto w-1 h-4 rounded-full bg-brand-500" />
              )}
            </Link>
          );
        })}

        <div className="pt-4 pb-1">
          <span className="px-3 text-[10px] font-semibold text-text-muted uppercase tracking-widest">
            Admin
          </span>
        </div>

        {[
          { href: "/admin/workflows", label: "Workflows", icon: Settings2 },
          { href: "/admin/workflows/validate", label: "Validate Workflow", icon: ShieldCheck },
        ].map(({ href, label, icon: Icon }) => {
          const isActive = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "bg-brand-500/10 text-brand-400 border border-brand-500/20"
                  : "text-text-secondary hover:text-text-primary hover:bg-surface-3 border border-transparent"
              }`}
            >
              <Icon size={18} />
              <span>{label}</span>
              {isActive && (
                <div className="ml-auto w-1 h-4 rounded-full bg-brand-500" />
              )}
            </Link>
          );
        })}
      </nav>

      <div className="p-3 border-t border-border space-y-1">
        <ThemeToggle />
        <div className="flex items-center gap-2 px-3 py-1.5 text-xs text-text-muted">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span>All systems nominal</span>
        </div>
      </div>
    </aside>
  );
}
