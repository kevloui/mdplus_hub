import { create } from "zustand";

interface ViewerState {
  isLoading: boolean;
  error: string | null;
  selectedAtoms: number[];
  representationType: "cartoon" | "ball-and-stick" | "surface";
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedAtoms: (atoms: number[]) => void;
  setRepresentationType: (type: "cartoon" | "ball-and-stick" | "surface") => void;
  reset: () => void;
}

export const useViewerStore = create<ViewerState>((set) => ({
  isLoading: false,
  error: null,
  selectedAtoms: [],
  representationType: "cartoon",
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setSelectedAtoms: (selectedAtoms) => set({ selectedAtoms }),
  setRepresentationType: (representationType) => set({ representationType }),
  reset: () =>
    set({
      isLoading: false,
      error: null,
      selectedAtoms: [],
      representationType: "cartoon",
    }),
}));
