"use client";
import { usePathname } from "next/navigation";
import { ChevronRight } from "lucide-react";

const PAGE_TITLES: Record<string, string> = {
  "/": "Dashboard",
  "/demo": "Demo Library",
};

export function Header() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  const crumbs: { label: string; href: string }[] = [];
  let href = "";
  for (const seg of segments) {
    href += `/${seg}`;
    if (seg === "cases") crumbs.push({ label: "Cases", href });
    else if (seg === "new") crumbs.push({ label: "New Request", href });
    else if (seg === "audit") crumbs.push({ label: "Audit Trail", href });
    else if (seg === "benchmark") crumbs.push({ label: "Benchmark", href });
    else if (seg === "replay") crumbs.push({ label: "Replay", href });
    else if (seg === "[id]" || seg.length > 20) continue;
    else if (seg === "demo") crumbs.push({ label: "Demo Library", href });
    else if (seg === "cases") continue;
    else crumbs.push({ label: seg, href });
  }

  return (
    <header className="sticky top-0 z-20 bg-surface/80 backdrop-blur-xl border-b border-border">
      <div className="flex items-center h-14 px-6 lg:px-8">
        {crumbs.length > 0 ? (
          <nav className="flex items-center gap-1.5 text-sm">
            {crumbs.map((c, i) => (
              <span key={c.href} className="flex items-center gap-1.5">
                {i > 0 && (
                  <ChevronRight size={14} className="text-text-muted" />
                )}
                <span
                  className={
                    i === crumbs.length - 1
                      ? "text-text-primary font-medium"
                      : "text-text-muted"
                  }
                >
                  {c.label}
                </span>
              </span>
            ))}
          </nav>
        ) : (
          <span className="text-sm text-text-muted">Dashboard</span>
        )}
        <div className="ml-auto flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-text-muted">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span className="hidden sm:inline">
              Qwen Cloud &middot; Connected
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
