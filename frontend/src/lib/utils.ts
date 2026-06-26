

import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

const categoryConfig: Record<string, { label: string; color: string }> = {
  tech: { label: "技术", color: "bg-blue-500/20 text-blue-400 border-blue-500/30" },
  business: { label: "商业", color: "bg-green-500/20 text-green-400 border-green-500/30" },
  policy: { label: "政策合规", color: "bg-orange-500/20 text-orange-400 border-orange-500/30" },
  social: { label: "社会", color: "bg-purple-500/20 text-purple-400 border-purple-500/30" },
  general: { label: "综合", color: "bg-gray-500/20 text-gray-400 border-gray-500/30" },
  product: { label: "选品机会", color: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" },
  logistics: { label: "物流风险", color: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30" },
  marketing: { label: "营销节点", color: "bg-pink-500/20 text-pink-400 border-pink-500/30" },
  fx: { label: "汇率", color: "bg-amber-500/20 text-amber-400 border-amber-500/30" },
  competitor: { label: "竞品动态", color: "bg-rose-500/20 text-rose-400 border-rose-500/30" },
};

export function getCategoryStyle(category: string) {
  return categoryConfig[category] || categoryConfig.general;
}

export function getCategoryLabel(category: string) {
  return categoryConfig[category]?.label || "综合";
}

export function getRatingStars(rating: number | null): string {
  if (!rating) return "—";
  return "★".repeat(rating) + "☆".repeat(5 - rating);
}

export function formatRelativeTime(dateStr: string | null): string {
  if (!dateStr) return "—";
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "刚刚";
  if (minutes < 60) return `${minutes}分钟前`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}小时前`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}天前`;
  return date.toLocaleDateString("zh-CN");
}

export function truncate(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen) + "...";
}
