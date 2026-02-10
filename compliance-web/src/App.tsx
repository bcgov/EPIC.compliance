import { ThemeProvider } from "@mui/material";
import { QueryClient } from "@tanstack/query-core";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { AuthProvider } from "react-oidc-context";
import { AppConfig, OidcConfig } from "@/utils/config";
import { theme } from "@/styles/theme";
import RouterProviderWithAuthContext from "@/router/RouterProviderWithAuthContext";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";
import SnackBarProvider from "@/components/Shared/Popups/SnackBarProvider";
import DrawerProvider from "@/components/Shared/Drawer/DrawerProvider";
import PopoverProvider from "@/components/Shared/Popover/PopoverProvider";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import AnalyticsTracker from "./components/Shared/AnalyticsTracker";

const queryClient = new QueryClient();

function App() {
  const environment = AppConfig.environment;

  return (
    <>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <AuthProvider {...OidcConfig}>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <AnalyticsTracker />
              <DrawerProvider />
              <ModalProvider />
              <SnackBarProvider />
              <PopoverProvider />
              <RouterProviderWithAuthContext />
            </LocalizationProvider>
          </AuthProvider>
        </ThemeProvider>
        {environment === "local" && (
          <ReactQueryDevtools initialIsOpen={false} buttonPosition="bottom-left" />
        )}
      </QueryClientProvider>
    </>
  );
}

export default App;
