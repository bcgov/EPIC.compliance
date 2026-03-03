import { FirstNation } from "@/models/FirstNation";
import { request } from "@/utils/axiosUtils";
import { useStaticQuery } from "@/hooks/useCustomQueries";

/** FETCH First Nations from Compliance API (proxied from TRACK API) */
const fetchFirstNations = (): Promise<FirstNation[]> => {
  return request({ url: "/first-nations" });
};


export const useFirstNationsData = () => {
  return useStaticQuery({
    queryKey: ["first-nations"],
    queryFn: fetchFirstNations,
  });
};
