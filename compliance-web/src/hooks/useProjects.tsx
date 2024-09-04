import { Project } from "@/models/Project";
import { request, requestTrackAPI } from "@/utils/axiosUtils";
import { UNAPPROVED_PROJECT_ID } from "@/utils/constants";
import { useQuery } from "@tanstack/react-query";

const fetchProjects = (): Promise<Project[]> => {
  return request({ url: "/projects" });
};

/** FETCH project details from TRACK API */
const fetchProjectById = (id: number): Promise<Project> => {
  return requestTrackAPI({ url: `/projects/${id}` });
};

export const useProjectsData = (args?: { includeUnapproved?: boolean }) => {
  return useQuery({
    queryKey: ["projects"],
    queryFn: fetchProjects,
    select: (data: Project[]) => {
      const projects = data.sort((a, b) => a.name.localeCompare(b.name));
      if (args?.includeUnapproved) {
        const UnApprovedProject: Project = {
          id: UNAPPROVED_PROJECT_ID,
          name: "Unapproved Project",
        };
        // Include the UnApprovedProject as the first entry in the fetched projects
        return [UnApprovedProject, ...projects];
      }
      return projects;
    },
  });
};

export const useProjectById = (projectId: number) => {
  return useQuery({
    queryKey: ["projects", projectId],
    queryFn: () => fetchProjectById(projectId),
    enabled: !!projectId,
  });
};
