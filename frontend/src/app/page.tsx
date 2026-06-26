"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AppHeader } from "@/components/app-header";
import { useProfile } from "@/lib/profile-context";
import { api, AlertLog, DailyBriefing, DashboardStats, Intelligence } from "@/lib/api";
import { getCategoryStyle, getCategoryLabel, getRatingStars, formatRelativeTime } from "@/lib/utils";
import { Activity, AlertTriangle, BarChart3, Eye, FileText, TrendingUp } from "lucide-react";

export default function DashboardPage() {
  const { currentProfileId, loading: profileLoading } = useProfile();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [briefing, setBriefing] = useState<DailyBriefing | null>(null);
  const [recent, setRecent] = useState<Intelligence[]>([]);
  const [alerts, setAlerts] = useState<AlertLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (profileLoading) return;
    let cancelled = false;
    async function load() {
      try {
        const [s, b, r, a] = await Promise.all([
          api.dashboard.stats(currentProfileId),
          api.dashboard.briefing(currentProfileId).catch(() => null),
          api.intelligences.list({ limit: "10" }, currentProfileId),
          api.alerts.logs(currentProfileId),
        ]);
        if (cancelled) return;
        setStats(s);
        setBriefing(b);
        setRecent(r);
        setAlerts(a.slice(0, 5));
      } catch (e) {
        console.error(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    const interval = setInterval(load, 60000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [currentProfileId, profileLoading]);

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-950 text-zinc-100">
        <AppHeader maxWidth="max-w-7xl" />
        <div className="flex items-center justify-center py-32 text-zinc-400 animate-pulse">加载情报中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <AppHeader maxWidth="max-w-7xl" />

      <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        <div className="grid grid-cols-4 gap-4">
          <StatCard icon={<Eye className="w-4 h-4" />} label="情报总量" value={stats?.total_intelligences ?? 0} sub="当前画像" />
          <StatCard icon={<TrendingUp className="w-4 h-4" />} label="今日新增" value={stats?.today_new ?? 0} sub="今日已采集" />
          <StatCard icon={<BarChart3 className="w-4 h-4" />} label="今日已分析" value={stats?.today_analyzed ?? 0} sub="AI已处理" />
          <StatCard icon={<AlertTriangle className="w-4 h-4" />} label="今日预警" value={stats?.today_alerts ?? 0} sub="需关注" />
        </div>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-400" />
              今日情报简报
              {briefing && (
                <Badge variant="outline" className="text-[10px] text-zinc-500 border-zinc-700 ml-1">
                  {briefing.total_count} 条 · 均分 {briefing.avg_rating ?? "—"}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!briefing || briefing.total_count === 0 ? (
              <div className="text-zinc-500 text-sm py-4 text-center">今日暂无可生成简报的情报</div>
            ) : (
              <div className="grid grid-cols-3 gap-4">
                <div className="col-span-2 text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
                  {briefing.ai_summary || "简报生成中，请稍后刷新。"}
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-zinc-500 uppercase tracking-wider">关键情报</div>
                  {briefing.top_intelligences.slice(0, 5).map((intel) => (
                    <Link key={intel.id} href={`/feed/${intel.id}`} className="block rounded-md bg-zinc-950/50 border border-zinc-800 p-2 hover:border-zinc-700 transition">
                      <div className="flex items-start gap-2">
                        <span className="text-amber-500 text-xs font-mono flex-shrink-0">{intel.rating ?? "—"}</span>
                        <div className="min-w-0">
                          <div className="text-xs text-zinc-300 line-clamp-1">{intel.title}</div>
                          {intel.summary && <div className="text-[10px] text-zinc-600 line-clamp-1 mt-0.5">{intel.summary}</div>}
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="grid grid-cols-3 gap-4">
          <div className="col-span-2">
            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <Activity className="w-4 h-4 text-amber-500" />
                  最新情报
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {recent.length === 0 ? (
                  <div className="text-zinc-500 text-sm py-8 text-center">暂无情报数据，请等待采集或检查情报源配置</div>
                ) : (
                  recent.map((intel) => {
                    const catStyle = getCategoryStyle(intel.category);
                    return (
                      <Link key={intel.id} href={`/feed/${intel.id}`}>
                        <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-zinc-800/50 transition cursor-pointer group">
                          <div className="text-amber-500 text-xs mt-1 font-mono whitespace-nowrap">
                            {intel.rating ? getRatingStars(intel.rating) : "—"}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-sm font-medium group-hover:text-amber-400 transition truncate">
                                {intel.title}
                              </span>
                            </div>
                            {intel.summary && (
                              <p className="text-xs text-zinc-500 line-clamp-1">{intel.summary}</p>
                            )}
                            <div className="flex items-center gap-2 mt-1.5">
                              <Badge className={`${catStyle.color} text-[10px] px-1.5 py-0`}>
                                {getCategoryLabel(intel.category)}
                              </Badge>
                              <span className="text-[10px] text-zinc-600">{intel.source_name}</span>
                              <span className="text-[10px] text-zinc-600">{formatRelativeTime(intel.collected_at)}</span>
                            </div>
                          </div>
                        </div>
                      </Link>
                    );
                  })
                )}
              </CardContent>
            </Card>
          </div>

          <div className="space-y-4">
            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-500" />
                  预警通知
                </CardTitle>
              </CardHeader>
              <CardContent>
                {alerts.length === 0 ? (
                  <div className="text-zinc-500 text-sm py-4 text-center">暂无预警</div>
                ) : (
                  <div className="space-y-2">
                    {alerts.map((alert) => (
                      <div key={alert.id} className={`p-2 rounded text-xs ${alert.is_read ? "bg-zinc-800/30 text-zinc-500" : "bg-red-500/10 text-red-300 border border-red-500/20"}`}>
                        <p>{alert.message}</p>
                        <p className="text-zinc-600 mt-1">{formatRelativeTime(alert.triggered_at)}</p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">分类分布</CardTitle>
              </CardHeader>
              <CardContent>
                {stats?.category_distribution && Object.entries(stats.category_distribution).map(([cat, count]) => {
                  const style = getCategoryStyle(cat);
                  const total = Object.values(stats.category_distribution).reduce((a, b) => a + b, 0);
                  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
                  return (
                    <div key={cat} className="flex items-center gap-2 mb-2">
                      <Badge className={`${style.color} text-[10px] px-1.5 py-0`}>{getCategoryLabel(cat)}</Badge>
                      <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                        <div className={`${style.color.split(" ")[0]} h-full rounded-full`} style={{ width: `${pct}%` }} />
                      </div>
                      <span className="text-[10px] text-zinc-500 w-8 text-right">{count}</span>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

function StatCard({ icon, label, value, sub }: { icon: React.ReactNode; label: string; value: number; sub: string }) {
  return (
    <Card className="bg-zinc-900 border-zinc-800">
      <CardContent className="pt-4 pb-4">
        <div className="flex items-center gap-2 text-zinc-500 text-xs mb-2">
          {icon}
          {label}
        </div>
        <div className="text-2xl font-bold font-mono">{value}</div>
        <div className="text-[10px] text-zinc-600 mt-1">{sub}</div>
      </CardContent>
    </Card>
  );
}
