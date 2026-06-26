"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { AppHeader } from "@/components/app-header";
import { api, ActionItem, Intelligence } from "@/lib/api";
import { getCategoryStyle, getCategoryLabel, getRatingStars, formatRelativeTime } from "@/lib/utils";
import { ExternalLink, Star, Tag, AlertCircle, FileText, MessageCircle, CheckCircle, ThumbsUp, ThumbsDown } from "lucide-react";

export default function IntelligenceDetailPage() {
  const params = useParams();
  const [intel, setIntel] = useState<Intelligence | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      api.intelligences.get(Number(params.id))
        .then(setIntel)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [params.id]);

  async function updatePreference(value: -1 | 1) {
    if (!intel) return;
    const current = intel.preference ?? null;
    const next = current === value ? null : value;
    setIntel({ ...intel, preference: next });
    try {
      const updated = await api.intelligences.preference(intel.id, next);
      setIntel(updated);
    } catch (e) {
      console.error(e);
      setIntel({ ...intel, preference: current });
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="text-zinc-400 animate-pulse">加载中...</div>
      </div>
    );
  }

  if (!intel) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="text-zinc-500">情报不存在</div>
      </div>
    );
  }

  const catStyle = getCategoryStyle(intel.category);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <AppHeader maxWidth="max-w-3xl" />

      <main className="max-w-3xl mx-auto px-6 py-6 space-y-4">
        <Card className="bg-zinc-900 border-zinc-800">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between mb-4">
              <h1 className="text-lg font-semibold text-zinc-100 leading-relaxed flex-1">{intel.title}</h1>
              <div className="flex items-center gap-2 ml-4 flex-shrink-0">
                <button
                  onClick={() => updatePreference(1)}
                  className={`p-1.5 rounded transition ${intel.preference === 1 ? "text-green-400 bg-green-500/10" : "text-zinc-500 hover:text-green-400"}`}
                  aria-label="喜欢"
                >
                  <ThumbsUp className="w-4 h-4" />
                </button>
                <button
                  onClick={() => updatePreference(-1)}
                  className={`p-1.5 rounded transition ${intel.preference === -1 ? "text-red-400 bg-red-500/10" : "text-zinc-500 hover:text-red-400"}`}
                  aria-label="不喜欢"
                >
                  <ThumbsDown className="w-4 h-4" />
                </button>
                {intel.url && (
                  <a href={intel.url} target="_blank" rel="noopener noreferrer" className="text-zinc-500 hover:text-amber-400 transition">
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3 mb-4 flex-wrap">
              <Badge className={`${catStyle.color} text-xs`}>{getCategoryLabel(intel.category)}</Badge>
              <span className="text-xs text-zinc-500">{intel.source_name}</span>
              <span className="text-xs text-zinc-500">{formatRelativeTime(intel.collected_at)}</span>
              {intel.published_at && (
                <span className="text-xs text-zinc-600">发布于 {formatRelativeTime(intel.published_at)}</span>
              )}
            </div>

            {intel.is_analyzed && (
              <>
                <Separator className="bg-zinc-800 mb-4" />

                <div className="grid grid-cols-1 gap-4">
                  <AnalysisSection
                    icon={<Star className="w-4 h-4 text-amber-500" />}
                    title="情报评级"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl font-bold text-amber-500 font-mono">{intel.rating}</span>
                      <span className="text-amber-500/80 text-lg">{intel.rating ? getRatingStars(intel.rating) : ""}</span>
                    </div>
                    {intel.rating_reason && <p className="text-xs text-zinc-400 mt-1">{intel.rating_reason}</p>}
                  </AnalysisSection>

                  {intel.summary && (
                    <AnalysisSection
                      icon={<FileText className="w-4 h-4 text-blue-400" />}
                      title="一句话摘要"
                    >
                      <p className="text-sm text-zinc-300">{intel.summary}</p>
                    </AnalysisSection>
                  )}

                  {intel.bullet_summary && intel.bullet_summary.length > 0 && (
                    <AnalysisSection
                      icon={<FileText className="w-4 h-4 text-cyan-400" />}
                      title="核心要点"
                    >
                      <ul className="space-y-1.5">
                        {intel.bullet_summary.map((item, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm text-zinc-300">
                            <span className="text-amber-500/70 mt-0.5 flex-shrink-0">•</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </AnalysisSection>
                  )}

                  {intel.plain_explanation && (
                    <AnalysisSection
                      icon={<MessageCircle className="w-4 h-4 text-purple-400" />}
                      title="大白话解读"
                    >
                      <p className="text-sm text-zinc-300 leading-relaxed">{intel.plain_explanation}</p>
                    </AnalysisSection>
                  )}

                  {intel.action_items && intel.action_items.length > 0 && (
                    <AnalysisSection
                      icon={<CheckCircle className="w-4 h-4 text-green-400" />}
                      title="下一步行动"
                    >
                      <div className="space-y-2">
                        {intel.action_items.map((item, index) => (
                          <ActionItemRow key={index} item={item} />
                        ))}
                      </div>
                    </AnalysisSection>
                  )}

                  {intel.potential_impact && (
                    <AnalysisSection
                      icon={<AlertCircle className="w-4 h-4 text-orange-400" />}
                      title="潜在影响"
                    >
                      <p className="text-sm text-zinc-300">{intel.potential_impact}</p>
                    </AnalysisSection>
                  )}

                  {intel.tags && intel.tags.length > 0 && (
                    <AnalysisSection
                      icon={<Tag className="w-4 h-4 text-green-400" />}
                      title="标签"
                    >
                      <div className="flex gap-1.5 flex-wrap">
                        {intel.tags.map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs text-zinc-400 border-zinc-700">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </AnalysisSection>
                  )}
                </div>
              </>
            )}

            {!intel.is_analyzed && (
              <div className="text-zinc-600 text-sm mt-4 text-center py-4">
                AI 分析中，请稍后刷新查看...
              </div>
            )}

            <Separator className="bg-zinc-800 my-4" />

            <div>
              <h3 className="text-xs text-zinc-500 mb-2 uppercase tracking-wider">原始内容</h3>
              <div className="text-sm text-zinc-400 leading-relaxed whitespace-pre-wrap max-h-96 overflow-y-auto">
                {intel.content}
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

function AnalysisSection({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <span className="text-xs font-medium text-zinc-300 uppercase tracking-wider">{title}</span>
      </div>
      {children}
    </div>
  );
}

function ActionItemRow({ item }: { item: ActionItem }) {
  const config = {
    act: { label: "立即行动", className: "bg-red-500/15 text-red-300 border-red-500/30" },
    watch: { label: "持续关注", className: "bg-yellow-500/15 text-yellow-300 border-yellow-500/30" },
    opportunity: { label: "机会捕捉", className: "bg-green-500/15 text-green-300 border-green-500/30" },
  }[item.type];

  return (
    <div className="flex items-start gap-2 rounded-md bg-zinc-950/50 border border-zinc-800 p-2">
      <Badge className={`${config.className} text-[10px] px-1.5 py-0 flex-shrink-0`}>{config.label}</Badge>
      <span className="text-sm text-zinc-300 leading-relaxed">{item.text}</span>
    </div>
  );
}
