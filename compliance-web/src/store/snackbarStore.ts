import { ALERT_SEVERITY_COLORS } from "@/utils/constants";
import { create } from "zustand";

interface SnackbarState {
  isOpen: boolean;
  severity: ALERT_SEVERITY_COLORS;
  message: string;
  duration: number;
  setOpen: (
    message: string,
    severity?: ALERT_SEVERITY_COLORS,
    duration?: number
  ) => void;
  setClose: () => void;
}

export const useSnackbar = create<SnackbarState>((set) => ({
  isOpen: false,
  severity: "success", // default severity
  message: "",
  duration: 2000,
  setOpen: (message, severity = "success", duration = 2000) =>
    set({ isOpen: true, message, severity, duration }),
  setClose: () => set({ isOpen: false }),
}));

// Helper function to notify with different severities
export const notify = {
  success: (message: string, duration?: number) =>
    useSnackbar.getState().setOpen(message, "success", duration),
  error: (message: string, duration?: number) => 
    useSnackbar.getState().setOpen(message, "error", duration),
  warning: (message: string, duration?: number) =>
    useSnackbar.getState().setOpen(message, "warning", duration),
  info: (message: string, duration?: number) => 
    useSnackbar.getState().setOpen(message, "info", duration),
};
