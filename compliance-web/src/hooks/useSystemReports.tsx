import { ReportFormValues } from "@/models/Report";
import { OnSuccessType, request } from "@/utils/axiosUtils";
import { useMutation } from "@tanstack/react-query";

const systemReportExport = (data: ReportFormValues = {}) => {
  const officer_ids = data.officers?.flatMap((o) => (o.id)) || [];
  const project_id = data.project?.id || null;
  const first_nation_id = data.first_nation?.id || null;
  delete data.officers;
  delete data.project;
  delete data.first_nation;
  return request({
    method: "POST",
    url: `/reports/export`,
    data: { ...data, officer_ids, project_id, first_nation_id },
    responseType: "blob",
  });
};

export const useSystemReportsExport = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: systemReportExport, onSuccess });
};
