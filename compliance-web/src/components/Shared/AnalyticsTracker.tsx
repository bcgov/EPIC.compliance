import { useAuth } from "react-oidc-context";
import { trackAnalytics } from "@epic/centre-analytics";
import { AppConfig } from "@/utils/config";

const AnalyticsTracker = () => {
  const authentication = useAuth();

  trackAnalytics({
    appName: "epic_compliance",
    centreApiUrl: AppConfig.centreAPIUrl,
    enabled: authentication.isAuthenticated && authentication.user !== null,
  });

  return null;
};

export default AnalyticsTracker;
