import { Project } from "@/models/Project";
import { UNAPPROVED_PROJECT_ID } from "@/utils/constants";
import { Stack } from "@mui/material";
import { FC, useEffect, useState } from "react";
import { useProjectById } from "@/hooks/useProjects";
import { useDrawer } from "@/store/drawerStore";
import { useFormContext } from "react-hook-form";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import { formatAuthorization } from "@/utils/appUtils";

type ProjectDetailsFormProps = {
  projectList: Project[];
  isEditMode?: boolean;
};

const ProjectDetailsForm: FC<ProjectDetailsFormProps> = ({
  projectList,
  isEditMode,
}) => {
  const { isOpen } = useDrawer();
  const { setValue, resetField } = useFormContext();
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(
    null
  );

  const { data: projectData } = useProjectById(selectedProjectId!);

  useEffect(() => {
    if (selectedProjectId && projectData) {
      setValue(
        "authorization",
        formatAuthorization(projectData?.ea_certificate)
      );
      setValue("regulatedParty", projectData?.proponent?.name ?? "");
      setValue("projectDescription", projectData?.description ?? "");
      setValue("projectType", projectData?.type?.name ?? "");
      setValue("projectSubType", projectData?.sub_type?.name ?? "");
    } else {
      resetField("authorization");
      resetField("regulatedParty");
      resetField("projectDescription");
      resetField("projectType");
      resetField("projectSubType");
    }
  }, [projectData, resetField, selectedProjectId, setValue]);

  // Resetting states when the drawer closes
  useEffect(() => {
    if (!isOpen) {
      setSelectedProjectId(null);
    }
  }, [isOpen]);

  return (
    <Stack flex={1}>
      <ControlledAutoComplete
        name="project"
        label="Project"
        options={projectList}
        getOptionLabel={(option) => option.name}
        getOptionKey={(option) => option.id}
        isOptionEqualToValue={(option, value) =>
          option.id.toString() === value.id.toString()
        }
        fullWidth
        onChange={(_, value) => {
          const projId = (value as Project)?.id;
          if (projId === UNAPPROVED_PROJECT_ID) {
            setSelectedProjectId(null);
          } else {
            setSelectedProjectId(projId);
          }
        }}
        disabled={isEditMode}
      />
      <ControlledTextField
        name="authorization"
        label="Authorization"
        placeholder="Authorization"
        disabled={!!selectedProjectId || isEditMode}
        fullWidth
      />
      <ControlledTextField
        name="regulatedParty"
        label="Regulated Party"
        placeholder="Regulated Party"
        disabled={!!selectedProjectId || isEditMode}
        fullWidth
      />
      <ControlledTextField
        name="projectType"
        label="Project Type"
        placeholder="Project Type"
        disabled={!!selectedProjectId || isEditMode}
        fullWidth
      />
      <ControlledTextField
        name="projectSubType"
        label="Project Subtype"
        placeholder="Project Subtype"
        disabled={!!selectedProjectId || isEditMode}
        fullWidth
      />
    </Stack>
  );
};

export default ProjectDetailsForm;
