import { ALERT_SEVERITY_COLORS } from "@/utils/constants";
import { create } from "zustand";

interface SnackbarState {
  isOpen: boolean;
  severity: ALERT_SEVERITY_COLORS;
  message: string;
  setOpen: (
    message: string,
    severity?: ALERT_SEVERITY_COLORS,
  ) => void;
  setClose: () => void;
}

export const useSnackbar = create<SnackbarState>((set) => ({
  isOpen: false,
  severity: "success", // default severity
  message: "",
  setOpen: (message, severity = "success") =>
    set({ isOpen: true, message, severity }),
  setClose: () => set({ isOpen: false }),
}));

// Helper function to notify with different severities
export const notify = {
  success: (message: string) =>
    useSnackbar.getState().setOpen(message, "success"),
  error: (message: string) => useSnackbar.getState().setOpen(message, "error"),
  warning: (message: string) =>
    useSnackbar.getState().setOpen(message, "warning"),
  info: (message: string) => useSnackbar.getState().setOpen(message, "info"),
};
