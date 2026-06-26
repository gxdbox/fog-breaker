"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, Profile } from "@/lib/api";

interface ProfileContextValue {
  profiles: Profile[];
  currentProfileId: number | null;
  currentProfile: Profile | null;
  setCurrentProfileId: (id: number | null) => void;
  reload: () => Promise<void>;
  loading: boolean;
}

const ProfileContext = createContext<ProfileContextValue | null>(null);

const STORAGE_KEY = "fogbreaker.currentProfileId";

export function ProfileProvider({ children }: { children: React.ReactNode }) {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [currentProfileId, setCurrentProfileIdState] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  const reload = useCallback(async () => {
    try {
      const data = await api.profiles.list();
      setProfiles(data);
      setCurrentProfileIdState((prev) => {
        if (prev != null && data.some((p) => p.id === prev)) return prev;
        const stored = typeof window !== "undefined" ? window.localStorage.getItem(STORAGE_KEY) : null;
        const storedId = stored ? Number(stored) : null;
        if (storedId != null && data.some((p) => p.id === storedId)) return storedId;
        const defaultProfile = data.find((p) => p.is_default) || data[0];
        return defaultProfile ? defaultProfile.id : null;
      });
    } catch (e) {
      console.error("Failed to load profiles", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const setCurrentProfileId = useCallback((id: number | null) => {
    setCurrentProfileIdState(id);
    if (typeof window !== "undefined") {
      if (id != null) window.localStorage.setItem(STORAGE_KEY, String(id));
      else window.localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const currentProfile = useMemo(
    () => profiles.find((p) => p.id === currentProfileId) || null,
    [profiles, currentProfileId],
  );

  const value = useMemo(
    () => ({ profiles, currentProfileId, currentProfile, setCurrentProfileId, reload, loading }),
    [profiles, currentProfileId, currentProfile, setCurrentProfileId, reload, loading],
  );

  return <ProfileContext.Provider value={value}>{children}</ProfileContext.Provider>;
}

export function useProfile() {
  const ctx = useContext(ProfileContext);
  if (!ctx) throw new Error("useProfile must be used within ProfileProvider");
  return ctx;
}
