import { DocumentJob, DocumentJobStatus } from "@/models/documentJob";
import { request, requestSilent } from "@/utils/axiosUtils";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useRef } from "react";

const fetchMostRecentDocumentJobForUser = (
  inspectionReportID: number,
  outputFormat: "pdf" | "docx"
): Promise<DocumentJob> => {
  return request({
    url: `/document-jobs/inspections/${inspectionReportID}/recent`,
    params: { output_format: outputFormat },
  });
};

const fetchLastGeneratedTimeForUser = (
  inspectionReportID: number,
  outputFormat: "pdf" | "docx"
): Promise<{ last_generated_time: string }> => {
  return request({
    url: `/document-jobs/inspections/${inspectionReportID}/last-generated`,
    params: { output_format: outputFormat },
  });
};

// Used only by the background "stuck job" watchdog below - silent because
// the user never triggered this call directly, so a failure shouldn't
// surface as an error toast.
const markDocumentJobFailedSilently = (jobId: string): Promise<DocumentJob> => {
  return requestSilent({
    url: `/document-jobs/${jobId}`,
    method: "PUT",
    data: { status: DocumentJobStatus.FAILED },
  });
};

const cancelDocumentJob = (jobId: string): Promise<DocumentJob> => {
  return request({
    url: `/document-jobs/${jobId}/cancel`,
    method: "POST",
  });
};

const deleteDocumentJob = (jobId: string): Promise<void> => {
  return request({
    url: `/document-jobs/${jobId}`,
    method: "DELETE",
  });
};

export const useMostRecentDocumentJobForUser = (
  inspectionReportID: number,
  outputFormat: "pdf" | "docx" = "pdf"
) => {
  const watchdogFiredRef = useRef(new Set<string>());

  return useQuery<DocumentJob, Error>({
    queryKey: ["mostRecentDocumentJob", inspectionReportID, outputFormat],
    queryFn: () =>
      fetchMostRecentDocumentJobForUser(inspectionReportID ?? 0, outputFormat),
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
        // If the job has been in progress for more than 10 minutes, mark it as failed.
        // Only fire once per stale job, and re-check the status right before writing
        if (
          elapsed > allowedWaitTime &&
          query.state.data?.id &&
          !watchdogFiredRef.current.has(query.state.data.id)
        ) {
          watchdogFiredRef.current.add(query.state.data.id);
          markDocumentJobFailedSilently(query.state.data.id).catch(() => {
            // A failure here isn't user-actionable, so make it silent.
          });
        }
      }
      return 5000;
    },
    enabled: !!inspectionReportID,
  });
};

export const useLastGeneratedTimeForUser = (
  inspectionReportID: number,
  outputFormat: "pdf" | "docx" = "pdf"
) => {
  return useQuery<{ last_generated_time: string }, Error>({
    queryKey: ["lastGeneratedTime", inspectionReportID, outputFormat],
    queryFn: () =>
      fetchLastGeneratedTimeForUser(inspectionReportID ?? 0, outputFormat),
    refetchInterval: 30000,
    enabled: !!inspectionReportID,
  });
};

export const useCancelDocumentJob = () => {
  return useMutation<DocumentJob, Error, string>({
    mutationFn: (jobId: string) => cancelDocumentJob(jobId),
  });
};

export const useDeleteDocumentJobs = () => {
  return useMutation<void, Error, string>({
    mutationFn: (jobId: string) => deleteDocumentJob(jobId),
  });
};
