"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Zap, ChevronDown } from "lucide-react";
import { useState } from "react";
import { useProfile } from "@/lib/profile-context";

const NAV_ITEMS = [
  { href: "/", label: "仪表盘" },
  { href: "/feed", label: "情报流" },
  { href: "/sources", label: "情报源" },
  { href: "/alerts", label: "预警" },
  { href: "/profiles", label: "画像" },
];

export function AppHeader({ maxWidth = "max-w-5xl" }: { maxWidth?: string }) {
  const pathname = usePathname();
  const { profiles, currentProfileId, currentProfile, setCurrentProfileId } = useProfile();
  const [open, setOpen] = useState(false);

  return (
    <header className="border-b border-zinc-800 px-6 py-4 sticky top-0 bg-zinc-950 z-20">
      <div className={`${maxWidth} mx-auto flex items-center justify-between gap-6`}>
        <div className="flex items-center gap-4">
          <Link href="/" className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" />
            <span className="font-bold tracking-tight">FogBreaker</span>
          </Link>
          <div className="relative">
            <button
              onClick={() => setOpen((v) => !v)}
              onBlur={() => setTimeout(() => setOpen(false), 150)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 hover:border-amber-500/40 transition"
            >
              <span className="text-amber-500/80">画像:</span>
              <span className="font-medium">{currentProfile?.name || "未选择"}</span>
              <ChevronDown className="w-3 h-3 text-zinc-500" />
            </button>
            {open && (
              <div className="absolute left-0 top-full mt-1 w-64 rounded-md bg-zinc-900 border border-zinc-800 shadow-xl py-1 z-30">
                {profiles.map((p) => (
                  <button
                    key={p.id}
                    onMouseDown={(e) => {
                      e.preventDefault();
                      setCurrentProfileId(p.id);
                      setOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs hover:bg-zinc-800 transition ${currentProfileId === p.id ? "text-amber-400" : "text-zinc-300"}`}
                  >
                    <div className="font-medium">{p.name}</div>
                    {p.description && <div className="text-[10px] text-zinc-500 mt-0.5 line-clamp-1">{p.description}</div>}
                  </button>
                ))}
                <Link
                  href="/profiles"
                  onMouseDown={() => setOpen(false)}
                  className="block px-3 py-2 text-[11px] text-zinc-500 border-t border-zinc-800 hover:bg-zinc-800 hover:text-zinc-300 transition"
                >
                  管理画像 →
                </Link>
              </div>
            )}
          </div>
        </div>
        <nav className="flex items-center gap-5 text-sm">
          {NAV_ITEMS.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={active ? "text-amber-500 font-medium" : "text-zinc-400 hover:text-zinc-200 transition"}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
