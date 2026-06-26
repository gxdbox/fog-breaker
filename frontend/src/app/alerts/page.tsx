"use client";

import { useCallback, useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AppHeader } from "@/components/app-header";
import { useProfile } from "@/lib/profile-context";
import { api, AlertRule, AlertLog } from "@/lib/api";
import { formatRelativeTime } from "@/lib/utils";
import { Plus, Bell, Check, AlertTriangle } from "lucide-react";

export default function AlertsPage() {
  const { currentProfileId, currentProfile, loading: profileLoading } = useProfile();
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [logs, setLogs] = useState<AlertLog[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [newName, setNewName] = useState("");
  const [newKeywords, setNewKeywords] = useState("");

  const loadData = useCallback(async () => {
    try {
      const [r, l] = await Promise.all([
        api.alerts.rules(currentProfileId),
        api.alerts.logs(currentProfileId),
      ]);
      setRules(r);
      setLogs(l);
    } catch (e) {
      console.error(e);
    }
  }, [currentProfileId]);

  useEffect(() => {
    if (profileLoading) return;
    loadData();
  }, [loadData, profileLoading]);

  async function handleAdd() {
    if (!newName.trim() || !newKeywords.trim()) return;
    try {
      await api.alerts.createRule({
        name: newName,
        rule_type: "keyword",
        conditions: { keywords: newKeywords.split(",").map((k) => k.trim()).filter(Boolean) },
        channels: ["browser"],
        profile_id: currentProfileId,
      } as Partial<AlertRule>);
      setShowAdd(false);
      setNewName("");
      setNewKeywords("");
      loadData();
    } catch (e) {
      console.error(e);
    }
  }

  async function handleMarkRead(id: number) {
    try {
      await api.alerts.markRead(id);
      loadData();
    } catch (e) {
      console.error(e);
    }
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <AppHeader />

      <main className="max-w-5xl mx-auto px-6 py-6">
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <Bell className="w-5 h-5 text-amber-500" />
                  预警记录
                </h2>
                <p className="text-xs text-zinc-500 mt-1">
                  当前画像: <span className="text-amber-400">{currentProfile?.name || "—"}</span>
                </p>
              </div>
            </div>
            {logs.length === 0 ? (
              <Card className="bg-zinc-900 border-zinc-800">
                <CardContent className="py-8 text-center text-zinc-500">暂无预警记录</CardContent>
              </Card>
            ) : (
              <div className="space-y-2">
                {logs.map((log) => (
                  <Card key={log.id} className={`bg-zinc-900 ${log.is_read ? "border-zinc-800" : "border-red-500/30"}`}>
                    <CardContent className="py-3 px-4 flex items-center gap-3">
                      <AlertTriangle className={`w-4 h-4 flex-shrink-0 ${log.is_read ? "text-zinc-600" : "text-red-400"}`} />
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm ${log.is_read ? "text-zinc-500" : "text-zinc-200"}`}>{log.message}</p>
                        <p className="text-[10px] text-zinc-600 mt-0.5">{formatRelativeTime(log.triggered_at)}</p>
                      </div>
                      {!log.is_read && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleMarkRead(log.id)}
                          className="text-zinc-500 hover:text-green-400"
                        >
                          <Check className="w-4 h-4" />
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">预警规则</h2>
              <Button
                onClick={() => setShowAdd(!showAdd)}
                size="sm"
                className="bg-amber-500/20 text-amber-400 border border-amber-500/30 hover:bg-amber-500/30"
              >
                <Plus className="w-4 h-4 mr-1" />
                新增
              </Button>
            </div>

            {showAdd && (
              <Card className="bg-zinc-900 border-amber-500/30 mb-4">
                <CardContent className="pt-4 space-y-3">
                  <div>
                    <label className="text-xs text-zinc-500 mb-1 block">规则名称</label>
                    <Input
                      className="bg-zinc-800 border-zinc-700"
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                      placeholder="例: Ozon 罚款预警"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-zinc-500 mb-1 block">关键词（逗号分隔）</label>
                    <Input
                      className="bg-zinc-800 border-zinc-700"
                      value={newKeywords}
                      onChange={(e) => setNewKeywords(e.target.value)}
                      placeholder="Ozon, 罚款, 下架"
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button variant="ghost" size="sm" onClick={() => setShowAdd(false)} className="text-zinc-400">取消</Button>
                    <Button size="sm" onClick={handleAdd} className="bg-amber-600 hover:bg-amber-700 text-white">添加</Button>
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="space-y-2">
              {rules.length === 0 ? (
                <Card className="bg-zinc-900 border-zinc-800">
                  <CardContent className="py-6 text-center text-zinc-500 text-xs">当前画像下暂无规则</CardContent>
                </Card>
              ) : (
                rules.map((rule) => (
                  <Card key={rule.id} className="bg-zinc-900 border-zinc-800">
                    <CardContent className="py-3 px-4">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium">{rule.name}</span>
                        {rule.is_active ? (
                          <Badge className="bg-green-500/20 text-green-400 text-[10px]">启用</Badge>
                        ) : (
                          <Badge className="bg-zinc-700 text-zinc-400 text-[10px]">停用</Badge>
                        )}
                      </div>
                      <div className="text-[10px] text-zinc-500">
                        类型: {rule.rule_type} ·
                        {rule.rule_type === "keyword" && rule.conditions.keywords
                          ? ` 关键词: ${(rule.conditions.keywords as string[]).join(", ")}`
                          : ` 条件: ${JSON.stringify(rule.conditions)}`}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
