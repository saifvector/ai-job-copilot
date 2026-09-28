import { create } from 'zustand';
import { User, Profile } from '@/types';

interface UserState {
  currentUser: User | null;
  currentProfile: Profile | null;
  isLoading: boolean;
  error: string | null;
  setCurrentUser: (user: User | null) => void;
  setCurrentProfile: (profile: Profile | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  currentUser: null,
  currentProfile: null,
  isLoading: false,
  error: null,
};

export const useUserStore = create<UserState>((set) => ({
  ...initialState,
  setCurrentUser: (user) => set({ currentUser: user, error: null }),
  setCurrentProfile: (profile) => set({ currentProfile: profile, error: null }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error, isLoading: false }),
  reset: () => set(initialState),
}));
