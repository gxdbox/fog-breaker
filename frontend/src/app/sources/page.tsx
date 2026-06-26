"use client";

import { useCallback, useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AppHeader } from "@/components/app-header";
import { useProfile } from "@/lib/profile-context";
import { api, Collection } from "@/lib/api";
import { Plus, Trash2, Power, PowerOff, Rss, Hash, Flame, DollarSign, ShoppingBag } from "lucide-react";

const SOURCE_TYPE_CONFIG: Record<string, { icon: React.ReactNode; label: string }> = {
  rss: { icon: <Rss className="w-4 h-4" />, label: "RSS" },
  hackernews: { icon: <Hash className="w-4 h-4" />, label: "HackerNews" },
  weibo: { icon: <Flame className="w-4 h-4" />, label: "微博热搜" },
  cbr_rate: { icon: <DollarSign className="w-4 h-4" />, label: "俄央行汇率" },
  ozon_seller: { icon: <ShoppingBag className="w-4 h-4" />, label: "Ozon店铺API" },
};

export default function SourcesPage() {
  const { currentProfileId, currentProfile, loading: profileLoading } = useProfile();
  const [collections, setCollections] = useState<Collection[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [newName, setNewName] = useState("");
  const [newType, setNewType] = useState("rss");
  const [newUrl, setNewUrl] = useState("");
  const [newCategory, setNewCategory] = useState("general");
  const [newLanguage, setNewLanguage] = useState("zh");

  const loadCollections = useCallback(async () => {
    try {
      const data = await api.collections.list(currentProfileId);
      setCollections(data);
    } catch (e) {
      console.error(e);
    }
  }, [currentProfileId]);

  useEffect(() => {
    if (profileLoading) return;
    loadCollections();
  }, [loadCollections, profileLoading]);

  async function handleToggle(id: number) {
    try {
      await api.collections.toggle(id);
      loadCollections();
    } catch (e) {
      console.error(e);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("确定删除此情报源？")) return;
    try {
      await api.collections.delete(id);
      loadCollections();
    } catch (e) {
      console.error(e);
    }
  }

  async function handleAdd() {
    if (!newName.trim()) return;
    try {
      const config: Record<string, unknown> = {};
      if (newType === "rss") {
        config.url = newUrl;
        if (newLanguage) config.language = newLanguage;
      }
      if (newType === "hackernews") config.max_items = 30;
      if (newType === "cbr_rate") config.currencies = ["CNY", "USD", "EUR"];
      await api.collections.create({
        name: newName,
        source_type: newType,
        config,
        category: newCategory,
        profile_id: currentProfileId,
      } as Partial<Collection>);
      setShowAdd(false);
      setNewName("");
      setNewUrl("");
      loadCollections();
    } catch (e) {
      console.error(e);
    }
  }

  const categories = currentProfile?.category_schema?.length
    ? currentProfile.category_schema
    : [
        { value: "tech", label: "技术" },
        { value: "business", label: "商业" },
        { value: "policy", label: "政策" },
        { value: "social", label: "社会" },
        { value: "general", label: "综合" },
      ];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <AppHeader />

      <main className="max-w-5xl mx-auto px-6 py-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold">情报源管理</h2>
            <p className="text-xs text-zinc-500 mt-1">
              当前画像: <span className="text-amber-400">{currentProfile?.name || "—"}</span>
            </p>
          </div>
          <Button
            onClick={() => setShowAdd(!showAdd)}
            className="bg-amber-500/20 text-amber-400 border border-amber-500/30 hover:bg-amber-500/30"
            size="sm"
          >
            <Plus className="w-4 h-4 mr-1" />
            添加情报源
          </Button>
        </div>

        {showAdd && (
          <Card className="bg-zinc-900 border-amber-500/30 mb-6">
            <CardContent className="pt-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-zinc-500 mb-1 block">名称</label>
                  <Input
                    className="bg-zinc-800 border-zinc-700"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="例: RBC 商业版"
                  />
                </div>
                <div>
                  <label className="text-xs text-zinc-500 mb-1 block">类型</label>
                  <select
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200"
                    value={newType}
                    onChange={(e) => setNewType(e.target.value)}
                  >
                    <option value="rss">RSS</option>
                    <option value="hackernews">HackerNews</option>
                    <option value="weibo">微博热搜</option>
                    <option value="cbr_rate">俄央行汇率</option>
                    <option value="ozon_seller">Ozon 店铺 API</option>
                  </select>
                </div>
                {newType === "rss" && (
                  <>
                    <div>
                      <label className="text-xs text-zinc-500 mb-1 block">RSS URL</label>
                      <Input
                        className="bg-zinc-800 border-zinc-700"
                        value={newUrl}
                        onChange={(e) => setNewUrl(e.target.value)}
                        placeholder="https://example.com/feed"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-zinc-500 mb-1 block">语言</label>
                      <select
                        className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200"
                        value={newLanguage}
                        onChange={(e) => setNewLanguage(e.target.value)}
                      >
                        <option value="zh">中文</option>
                        <option value="en">English</option>
                        <option value="ru">Русский</option>
                      </select>
                    </div>
                  </>
                )}
                <div>
                  <label className="text-xs text-zinc-500 mb-1 block">分类</label>
                  <select
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200"
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                  >
                    {categories.map((c) => (
                      <option key={c.value} value={c.value}>{c.label}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-2 mt-3">
                <Button variant="ghost" size="sm" onClick={() => setShowAdd(false)} className="text-zinc-400">
                  取消
                </Button>
                <Button size="sm" onClick={handleAdd} className="bg-amber-600 hover:bg-amber-700 text-white">
                  添加
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="space-y-2">
          {collections.length === 0 ? (
            <Card className="bg-zinc-900 border-zinc-800">
              <CardContent className="py-8 text-center text-zinc-500 text-sm">当前画像下暂无情报源</CardContent>
            </Card>
          ) : (
            collections.map((col) => {
              const typeConfig = SOURCE_TYPE_CONFIG[col.source_type] || { icon: <Rss className="w-4 h-4" />, label: col.source_type };
              return (
                <Card key={col.id} className="bg-zinc-900 border-zinc-800">
                  <CardContent className="py-3 px-4 flex items-center gap-4">
                    <div className={`p-2 rounded-md ${col.is_active ? "bg-amber-500/10 text-amber-500" : "bg-zinc-800 text-zinc-600"}`}>
                      {typeConfig.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">{col.name}</span>
                        <Badge variant="outline" className="text-[10px] text-zinc-500 border-zinc-700">
                          {typeConfig.label}
                        </Badge>
                        <Badge variant="outline" className="text-[10px] text-zinc-500 border-zinc-700">
                          {col.category}
                        </Badge>
                        {typeof col.config?.language === "string" && col.config.language !== "zh" && (
                          <Badge variant="outline" className="text-[10px] text-zinc-400 border-zinc-700">
                            {(col.config.language as string).toUpperCase()}
                          </Badge>
                        )}
                      </div>
                      <div className="text-[10px] text-zinc-600 mt-0.5">
                        每 {col.poll_interval_minutes} 分钟采集
                        {col.last_fetched_at && ` · 上次采集: ${new Date(col.last_fetched_at).toLocaleString("zh-CN")}`}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleToggle(col.id)}
                        className={col.is_active ? "text-green-500 hover:text-green-400" : "text-zinc-600 hover:text-zinc-400"}
                      >
                        {col.is_active ? <Power className="w-4 h-4" /> : <PowerOff className="w-4 h-4" />}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(col.id)}
                        className="text-zinc-600 hover:text-red-400"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })
          )}
        </div>
      </main>
    </div>
  );
}
