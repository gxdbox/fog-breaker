"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { AppHeader } from "@/components/app-header";
import { useProfile } from "@/lib/profile-context";
import { api, Intelligence } from "@/lib/api";
import { getCategoryStyle, getCategoryLabel, formatRelativeTime } from "@/lib/utils";
import { Search, Filter, ChevronDown, ChevronUp, ThumbsUp, ThumbsDown } from "lucide-react";

const DEFAULT_CATEGORIES = [
  { value: "tech", label: "技术" },
  { value: "business", label: "商业" },
  { value: "policy", label: "政策" },
  { value: "social", label: "社会" },
];

export default function FeedPage() {
  const { currentProfileId, currentProfile, loading: profileLoading } = useProfile();
  const [intelligences, setIntelligences] = useState<Intelligence[]>([]);
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const categories = useMemo(() => {
    const list = currentProfile?.category_schema?.length ? currentProfile.category_schema : DEFAULT_CATEGORIES;
    return [{ value: "", label: "全部" }, ...list];
  }, [currentProfile]);

  useEffect(() => {
    setCategory("");
  }, [currentProfileId]);

  useEffect(() => {
    if (profileLoading) return;
    let cancelled = false;
    async function load() {
      try {
        const params: Record<string, string> = { limit: "50" };
        if (category) params.category = category;
        const data = await api.intelligences.list(params, currentProfileId);
        if (!cancelled) setIntelligences(data);
      } catch (e) {
        console.error(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [category, currentProfileId, profileLoading]);

  async function loadFeed() {
    try {
      const params: Record<string, string> = { limit: "50" };
      if (category) params.category = category;
      const data = await api.intelligences.list(params, currentProfileId);
      setIntelligences(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch() {
    setLoading(true);
    if (!search.trim()) {
      loadFeed();
      return;
    }
    try {
      const data = await api.intelligences.search(search, currentProfileId);
      setIntelligences(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function updatePreference(id: number, value: -1 | 1) {
    const current = intelligences.find((item) => item.id === id)?.preference ?? null;
    const next = current === value ? null : value;
    setIntelligences((items) => items.map((item) => item.id === id ? { ...item, preference: next } : item));
    try {
      await api.intelligences.preference(id, next);
    } catch (e) {
      console.error(e);
      setIntelligences((items) => items.map((item) => item.id === id ? { ...item, preference: current } : item));
    }
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <AppHeader />

      <main className="max-w-5xl mx-auto px-6 py-6">
        <div className="flex items-center gap-3 mb-6 flex-wrap">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <Input
              placeholder="搜索情报..."
              className="pl-9 bg-zinc-900 border-zinc-800"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
          </div>
          <div className="flex items-center gap-1 flex-wrap">
            <Filter className="w-4 h-4 text-zinc-500 mr-1" />
            {categories.map((cat) => (
              <button
                key={cat.value}
                onClick={() => setCategory(cat.value)}
                className={`px-3 py-1.5 text-xs rounded-md transition ${
                  category === cat.value
                    ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                    : "bg-zinc-900 text-zinc-400 border border-zinc-800 hover:border-zinc-700"
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="text-zinc-500 text-center py-16 animate-pulse">加载中...</div>
        ) : intelligences.length === 0 ? (
          <div className="text-zinc-500 text-center py-16">暂无情报数据</div>
        ) : (
          <div className="space-y-2">
            {intelligences.map((intel) => {
              const catStyle = getCategoryStyle(intel.category);
              const isExpanded = expandedId === intel.id;
              return (
                <Card key={intel.id} className="bg-zinc-900 border-zinc-800 hover:border-zinc-700 transition mb-2">
                  <CardContent className="py-4 px-4">
                    <div className="flex gap-4">
                      <div className="flex-shrink-0 w-14 text-center pt-1">
                        {intel.rating ? (
                          <div className="text-amber-500 text-lg font-mono leading-none">{intel.rating}</div>
                        ) : (
                          <div className="text-zinc-700 text-lg">—</div>
                        )}
                        <div className="text-[9px] text-zinc-600 mt-1">评级</div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-zinc-200 mb-1 line-clamp-1">{intel.title}</h3>
                        {intel.bullet_summary && intel.bullet_summary.length > 0 ? (
                          <div className="mb-2">
                            <ul className="text-xs text-zinc-400 space-y-0.5">
                              {intel.bullet_summary.slice(0, isExpanded ? undefined : 2).map((b, i) => (
                                <li key={i} className="flex items-start gap-1.5">
                                  <span className="text-amber-500/60 mt-0.5 flex-shrink-0">•</span>
                                  <span>{b}</span>
                                </li>
                              ))}
                            </ul>
                            {intel.bullet_summary.length > 2 && (
                              <button
                                onClick={(e) => { e.preventDefault(); setExpandedId(isExpanded ? null : intel.id); }}
                                className="text-[10px] text-zinc-600 hover:text-zinc-400 flex items-center gap-0.5 mt-1"
                              >
                                {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                                {isExpanded ? "收起" : `还有${intel.bullet_summary.length - 2}个要点`}
                              </button>
                            )}
                          </div>
                        ) : intel.summary ? (
                          <p className="text-xs text-zinc-500 line-clamp-2 mb-2">{intel.summary}</p>
                        ) : (
                          <p className="text-xs text-zinc-600 line-clamp-2 mb-2">{intel.content.slice(0, 150)}</p>
                        )}
                        <div className="flex items-center gap-2 flex-wrap">
                          <Badge className={`${catStyle.color} text-[10px] px-1.5 py-0`}>
                            {getCategoryLabel(intel.category)}
                          </Badge>
                          {intel.language && intel.language !== "zh" && (
                            <Badge variant="outline" className="text-[10px] px-1.5 py-0 text-zinc-400 border-zinc-700">
                              {intel.language.toUpperCase()}
                            </Badge>
                          )}
                          {intel.action_items && intel.action_items.length > 0 && (
                            intel.action_items.some(a => a.type === "act") ? (
                              <Badge className="bg-red-500/20 text-red-400 border-red-500/30 text-[10px] px-1.5 py-0">需行动</Badge>
                            ) : intel.action_items.some(a => a.type === "watch") ? (
                              <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30 text-[10px] px-1.5 py-0">需关注</Badge>
                            ) : null
                          )}
                          {intel.tags?.slice(0, 3).map((tag) => (
                            <Badge key={tag} variant="outline" className="text-[10px] px-1.5 py-0 text-zinc-500 border-zinc-700">
                              {tag}
                            </Badge>
                          ))}
                          <span className="text-[10px] text-zinc-600">{intel.source_name}</span>
                          <span className="text-[10px] text-zinc-600">{formatRelativeTime(intel.collected_at)}</span>
                          <div className="flex items-center gap-1 ml-auto">
                            <button
                              onClick={() => updatePreference(intel.id, 1)}
                              className={`p-1 rounded transition ${intel.preference === 1 ? "text-green-400 bg-green-500/10" : "text-zinc-600 hover:text-green-400"}`}
                              aria-label="喜欢"
                            >
                              <ThumbsUp className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => updatePreference(intel.id, -1)}
                              className={`p-1 rounded transition ${intel.preference === -1 ? "text-red-400 bg-red-500/10" : "text-zinc-600 hover:text-red-400"}`}
                              aria-label="不喜欢"
                            >
                              <ThumbsDown className="w-3.5 h-3.5" />
                            </button>
                            <Link href={`/feed/${intel.id}`} className="text-[10px] text-amber-500/60 hover:text-amber-400">详情 →</Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
