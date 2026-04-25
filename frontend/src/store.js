import { create } from 'zustand';

export const useStore = create((set) => ({
  status: null,
  history: [],
  setStatus: (status) => set({ status }),
  setHistory: (history) => set({ history }),
  addHistory: (item) => set((state) => ({ history: [item, ...state.history] })),
  clearHistory: () => set({ history: [] })
}));
