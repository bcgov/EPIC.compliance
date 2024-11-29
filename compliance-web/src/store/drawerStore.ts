import { create } from "zustand";

// Define the store state and actions
interface DrawerStore {
  isOpen: boolean;
  drawerContent: React.ReactNode | null;
  drawerWidth: string;
  setOpen: (args: { content: React.ReactNode; width?: string }) => Promise<void>;
  setClose: () => void;
}

// Create the Zustand store
export const useDrawer = create<DrawerStore>((set) => ({
  isOpen: false,
  drawerContent: null,
  drawerWidth: "",

  setOpen: async ({ content, width = "450px" }) => {
    if (content) {
      set(() => ({
        drawerContent: content,
        drawerWidth: width,
        isOpen: true,
      }));
    }
  },

  setClose: () => {
    set({
      isOpen: false,
      drawerContent: null,
    });
  },
}));
