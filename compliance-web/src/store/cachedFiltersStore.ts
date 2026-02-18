import { create } from "zustand";
import { persist } from "zustand/middleware";
import { MasterTableColumnFilter } from "@/components/Shared/FilterSelect/type";
import { MRT_SortingState } from "material-react-table";

interface CachedFilterState {
  columnFilters: MasterTableColumnFilter[];
  externalFilters?: Record<string, unknown>;
  sorting?: MRT_SortingState;
}

interface CachedFiltersState {
  filters: { [key: string]: CachedFilterState };
  hasHydrated: boolean;
  setHasHydrated: (value: boolean) => void;
  setFilters: (storageKey: string, filters: MasterTableColumnFilter[], externalFilters?: Record<string, unknown>, sorting?: MRT_SortingState) => void;
  getFilters: (storageKey: string) => MasterTableColumnFilter[];
  getExternalFilters: (storageKey: string) => Record<string, unknown> | undefined;
  getSorting: (storageKey: string) => MRT_SortingState | undefined;
  getCachedFilterState: (storageKey: string) => CachedFilterState;
  clearFilters: (storageKey: string) => void;
  clearAllFilters: () => void;
}

export const cachedFiltersStore = create<CachedFiltersState>()(
  persist(
    (set, get) => ({
      filters: {},
      hasHydrated: false,
      setHasHydrated: (value: boolean) =>
        set({ hasHydrated: value }),
      setFilters: (storageKey: string, filters: MasterTableColumnFilter[], externalFilters?: Record<string, unknown>, sorting?: MRT_SortingState) => {
        set((state) => ({
          filters: {
            ...state.filters,
            [storageKey]: {
              columnFilters: filters,
              ...(externalFilters && { externalFilters }),
              ...(sorting && { sorting }),
            },
          },
        }));
      },
      getFilters: (storageKey: string) => {
        return get().filters[storageKey]?.columnFilters || [];
      },
      getExternalFilters: (storageKey: string) => {
        return get().filters[storageKey]?.externalFilters;
      },
      getSorting: (storageKey: string) => {
        return get().filters[storageKey]?.sorting;
      },
      getCachedFilterState: (storageKey: string) => {
        return get().filters[storageKey] || { columnFilters: [] };
      },
      clearFilters: (storageKey: string) => {
        set((state) => {
          const newFilters = { ...state.filters };
          delete newFilters[storageKey];
          return { filters: newFilters };
        });
      },
      clearAllFilters: () => {
        set({ filters: {} });
      },
    }),
    {
      name: "cached-filters-storage",
      storage: {
        getItem: (name) => {
          try {
            const data = sessionStorage.getItem(name);
            return data ? JSON.parse(data) : null;
          } catch (error) {
            return null;
          }
        },
        setItem: (name, value) => {
          try {
            sessionStorage.setItem(name, JSON.stringify(value));
          } catch (error) {
            // Silently handle error
          }
        },
        removeItem: (name) => {
          try {
            sessionStorage.removeItem(name);
          } catch (error) {
            // Silently handle error
          }
        },
      },
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);

