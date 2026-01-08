import { DocumentJob, DocumentJobStatus } from "@/models/documentJob";
import { request } from "@/utils/axiosUtils";
import { useQuery, useMutation } from "@tanstack/react-query";

const fetchMostRecentDocumentJobForUser = (
  inspectionReportID: number
): Promise<DocumentJob> => {
  return request({
    url: `/document-jobs/inspections/${inspectionReportID}/recent`,
  });
};

const fetchLastGeneratedTimeForUser = (
  inspectionReportID: number
): Promise<{ last_generated_time: string }> => {
  return request({
    url: `/document-jobs/inspections/${inspectionReportID}/last-generated`,
  });
};

const updateDocumentJob = (
  jobId: string,
  data: Partial<DocumentJob>
): Promise<DocumentJob> => {
  return request({
    url: `/document-jobs/${jobId}`,
    method: "PUT",
    data,
  });
};

const deleteDocumentJob = (jobId: string): Promise<void> => {
  return request({
    url: `/document-jobs/${jobId}`,
    method: "DELETE",
  });
};

export const useMostRecentDocumentJobForUser = (inspectionReportID: number) => {
  return useQuery<DocumentJob, Error>({
    queryKey: ["mostRecentDocumentJob", inspectionReportID],
    queryFn: () => fetchMostRecentDocumentJobForUser(inspectionReportID ?? 0),
    refetchInterval: (query) => {
      const isInProgress =
        query.state.data &&
        query.state.data.status === DocumentJobStatus.IN_PROGRESS;

      if (isInProgress) {
        const startedAt = query.state.data?.started_at
          ? new Date(query.state.data?.started_at).getTime()
          : 0;
        const now = new Date().getTime();
        const elapsed = now - startedAt;
        const allowedWaitTime = 10 * 60 * 1000; // 10 minutes
        // If the job has been in progress for more than 10 minutes, mark it as failed and stop polling
        if (elapsed > allowedWaitTime && query.state.data?.id) {
          updateDocumentJob(query.state.data.id, {
            status: DocumentJobStatus.FAILED,
          }).then(() => {
            return false;
          });
        }
      }
      return 5000;
    },
    enabled: !!inspectionReportID,
  });
};

export const useLastGeneratedTimeForUser = (inspectionReportID: number) => {
  return useQuery<{ last_generated_time: string }, Error>({
    queryKey: ["lastGeneratedTime", inspectionReportID],
    queryFn: () => fetchLastGeneratedTimeForUser(inspectionReportID ?? 0),
    refetchInterval: 30000,
    enabled: !!inspectionReportID,
  });
};

export const useDeleteDocumentJobs = () => {
  return useMutation<void, Error, string>({
    mutationFn: (jobId: string) => deleteDocumentJob(jobId),
  });
};
