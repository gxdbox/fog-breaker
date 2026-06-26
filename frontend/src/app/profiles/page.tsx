"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AppHeader } from "@/components/app-header";
import { useProfile } from "@/lib/profile-context";
import { api, Profile } from "@/lib/api";
import { Layers, Plus, Trash2, Pencil, Save, X } from "lucide-react";

export default function ProfilesPage() {
  const { profiles, reload, currentProfileId, setCurrentProfileId } = useProfile();
  const [editing, setEditing] = useState<number | null>(null);
  const [draft, setDraft] = useState<Partial<Profile>>({});
  const [showAdd, setShowAdd] = useState(false);
  const [newDraft, setNewDraft] = useState<Partial<Profile>>({ name: "", description: "", analyzer_prompt: "", briefing_prompt: "" });

  function startEdit(p: Profile) {
    setEditing(p.id);
    setDraft({
      name: p.name,
      description: p.description,
      analyzer_prompt: p.analyzer_prompt,
      briefing_prompt: p.briefing_prompt,
    });
  }

  async function saveEdit(id: number) {
    try {
      await api.profiles.update(id, draft);
      setEditing(null);
      reload();
    } catch (e) {
      console.error(e);
      alert("保存失败");
    }
  }

  async function handleDelete(p: Profile) {
    if (p.is_default) {
      alert("默认画像不可删除");
      return;
    }
    if (!confirm(`删除画像「${p.name}」？关联的情报源和情报不会删除，但会失去 profile 关联`)) return;
    try {
      await api.profiles.delete(p.id);
      if (currentProfileId === p.id) setCurrentProfileId(null);
      reload();
    } catch (e) {
      console.error(e);
      alert("删除失败");
    }
  }

  async function handleAdd() {
    if (!newDraft.name?.trim()) return;
    try {
      const created = await api.profiles.create(newDraft);
      setShowAdd(false);
      setNewDraft({ name: "", description: "", analyzer_prompt: "", briefing_prompt: "" });
      await reload();
      setCurrentProfileId(created.id);
    } catch (e) {
      console.error(e);
      alert("创建失败：名称可能已存在");
    }
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <AppHeader />

      <main className="max-w-5xl mx-auto px-6 py-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Layers className="w-5 h-5 text-amber-500" />
              画像管理
            </h2>
            <p className="text-xs text-zinc-500 mt-1">每个画像 = 一组采集源 + 一套分析提示词 + 一组告警规则</p>
          </div>
          <Button
            onClick={() => setShowAdd((v) => !v)}
            size="sm"
            className="bg-amber-500/20 text-amber-400 border border-amber-500/30 hover:bg-amber-500/30"
          >
            <Plus className="w-4 h-4 mr-1" />
            新建画像
          </Button>
        </div>

        {showAdd && (
          <Card className="bg-zinc-900 border-amber-500/30 mb-6">
            <CardContent className="pt-4 space-y-3">
              <div>
                <label className="text-xs text-zinc-500 mb-1 block">名称</label>
                <Input
                  className="bg-zinc-800 border-zinc-700"
                  value={newDraft.name || ""}
                  onChange={(e) => setNewDraft({ ...newDraft, name: e.target.value })}
                  placeholder="例: AI 技术追踪"
                />
              </div>
              <div>
                <label className="text-xs text-zinc-500 mb-1 block">描述</label>
                <Input
                  className="bg-zinc-800 border-zinc-700"
                  value={newDraft.description || ""}
                  onChange={(e) => setNewDraft({ ...newDraft, description: e.target.value })}
                  placeholder="一句话描述这个画像关注什么"
                />
              </div>
              <div>
                <label className="text-xs text-zinc-500 mb-1 block">分析提示词（可留空使用默认）</label>
                <textarea
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-xs text-zinc-200 font-mono min-h-[100px]"
                  value={newDraft.analyzer_prompt || ""}
                  onChange={(e) => setNewDraft({ ...newDraft, analyzer_prompt: e.target.value })}
                  placeholder="留空使用通用提示词，否则需包含 {title} 和 {content} 占位符"
                />
              </div>
              <div>
                <label className="text-xs text-zinc-500 mb-1 block">简报提示词（可留空使用默认）</label>
                <textarea
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-xs text-zinc-200 font-mono min-h-[80px]"
                  value={newDraft.briefing_prompt || ""}
                  onChange={(e) => setNewDraft({ ...newDraft, briefing_prompt: e.target.value })}
                  placeholder="留空使用通用简报模板，否则需包含 {items_text} 占位符"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="ghost" size="sm" onClick={() => setShowAdd(false)} className="text-zinc-400">取消</Button>
                <Button size="sm" onClick={handleAdd} className="bg-amber-600 hover:bg-amber-700 text-white">创建</Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="space-y-3">
          {profiles.map((p) => (
            <Card key={p.id} className={`bg-zinc-900 ${currentProfileId === p.id ? "border-amber-500/50" : "border-zinc-800"}`}>
              <CardContent className="py-4 px-4">
                {editing === p.id ? (
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-zinc-500 mb-1 block">名称</label>
                      <Input
                        className="bg-zinc-800 border-zinc-700"
                        value={draft.name || ""}
                        onChange={(e) => setDraft({ ...draft, name: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="text-xs text-zinc-500 mb-1 block">描述</label>
                      <Input
                        className="bg-zinc-800 border-zinc-700"
                        value={draft.description || ""}
                        onChange={(e) => setDraft({ ...draft, description: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="text-xs text-zinc-500 mb-1 block">分析提示词</label>
                      <textarea
                        className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-xs text-zinc-200 font-mono min-h-[180px]"
                        value={draft.analyzer_prompt || ""}
                        onChange={(e) => setDraft({ ...draft, analyzer_prompt: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="text-xs text-zinc-500 mb-1 block">简报提示词</label>
                      <textarea
                        className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-xs text-zinc-200 font-mono min-h-[120px]"
                        value={draft.briefing_prompt || ""}
                        onChange={(e) => setDraft({ ...draft, briefing_prompt: e.target.value })}
                      />
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button variant="ghost" size="sm" onClick={() => setEditing(null)} className="text-zinc-400">
                        <X className="w-4 h-4 mr-1" />取消
                      </Button>
                      <Button size="sm" onClick={() => saveEdit(p.id)} className="bg-amber-600 hover:bg-amber-700 text-white">
                        <Save className="w-4 h-4 mr-1" />保存
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold">{p.name}</span>
                        {p.is_default && <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30 text-[10px]">默认</Badge>}
                        {currentProfileId === p.id && <Badge className="bg-green-500/20 text-green-400 border-green-500/30 text-[10px]">当前</Badge>}
                      </div>
                      {p.description && <p className="text-xs text-zinc-500 mt-1">{p.description}</p>}
                      {p.analyzer_prompt && (
                        <details className="mt-2">
                          <summary className="text-[10px] text-zinc-600 cursor-pointer hover:text-zinc-400">查看分析提示词</summary>
                          <pre className="mt-1 text-[10px] text-zinc-500 bg-zinc-950 p-2 rounded border border-zinc-800 max-h-40 overflow-auto whitespace-pre-wrap">{p.analyzer_prompt}</pre>
                        </details>
                      )}
                    </div>
                    <div className="flex items-center gap-1">
                      {currentProfileId !== p.id && (
                        <Button variant="ghost" size="sm" onClick={() => setCurrentProfileId(p.id)} className="text-zinc-400 hover:text-amber-400">
                          切换
                        </Button>
                      )}
                      <Button variant="ghost" size="sm" onClick={() => startEdit(p)} className="text-zinc-500 hover:text-amber-400">
                        <Pencil className="w-4 h-4" />
                      </Button>
                      {!p.is_default && (
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(p)} className="text-zinc-500 hover:text-red-400">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}
