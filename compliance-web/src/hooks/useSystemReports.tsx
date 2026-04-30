import { ReportFormValues } from "@/models/Report";
import { setAuthToken } from "@/utils/axiosUtils";
import { AppConfig } from "@/utils/config";
import { useMutation } from "@tanstack/react-query";
import axios from "axios";

const systemReportExport = (data: ReportFormValues = {}) => {
  const officer_ids =
    data.officers?.flatMap((o) => o.id).filter((o) => o) || [];
  const project_id = data.project?.id || null;
  const first_nation_id = data.first_nation?.id || null;
  delete data.officers;
  delete data.project;
  delete data.first_nation;
  const client = axios.create({ baseURL: AppConfig.apiUrl });
  setAuthToken(client);
  return client({
    method: "POST",
    url: `/reports/export`,
    data: { ...data, officer_ids, project_id, first_nation_id },
    responseType: "blob",
  }).then((response) => {
    const disposition: string =
      response.headers["content-disposition"] ?? "";
    const match = disposition.match(/filename="?([^"\s;]+)"?/);
    return { data: response.data as Blob, filename: match?.[1] ?? null };
  });
};

export const useSystemReportsExport = (
  onSuccess: (result: { data: Blob; filename: string | null }) => void,
) => {
  return useMutation({ mutationFn: systemReportExport, onSuccess });
};
