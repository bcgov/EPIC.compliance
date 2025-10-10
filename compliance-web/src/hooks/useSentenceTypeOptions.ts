import { request } from "@/utils/axiosUtils";
import { useQuery } from "@tanstack/react-query";

export interface SentenceTypeOption {
  id: number;
  name: string;
  sort_order?: number;
}

const fetchSentenceTypeOptions = (): Promise<SentenceTypeOption[]> => {
  return request({ url: "/sentence-type-options" });
};

export const useSentenceTypeOptionsData = () => {
  return useQuery({
    queryKey: ["sentence-type-options"],
    queryFn: () => fetchSentenceTypeOptions(),
  });
};
