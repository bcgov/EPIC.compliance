import { DialogContent } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import { FC, useEffect, useMemo } from "react";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import { CaseFile } from "@/models/CaseFile";
import { useCaseFileOptions } from "@/hooks/useCaseFiles";
import { CaseFileOption } from "@/models/CaseFile";

type LinkCaseFileModalProps = {
  onSubmit: (caseFileId: number) => void;
  linkedCaseFiles?: CaseFile[];
  fileNumber: string;
  isEdit?: boolean;
};

const linkCaseFileSchema = yup.object().shape({
  caseFile: yup
    .object<CaseFile>()
    .nullable()
    .required("Please select a case file"),
});

type LinkCaseFileFormType = yup.InferType<typeof linkCaseFileSchema>;

const initFormData = {
  caseFile: undefined,
};

const LinkCaseFileModal: FC<LinkCaseFileModalProps> = ({
  onSubmit,
  linkedCaseFiles,
  fileNumber,
  isEdit,
}) => {
  const { data: caseFileOptions } = useCaseFileOptions();
  const linkedCaseFilesOptions = useMemo<CaseFileOption[]>(() => {
    return linkedCaseFiles?.map((linked) => {
      return {
        id: linked.id,
        name: linked.case_file_number,
      };
    }) ?? [];
  }, [linkedCaseFiles]);
  const filteredCaseFileList =
    (caseFileOptions ?? [])
      .filter(
        (caseFileOption) =>
          caseFileOption.name !== fileNumber &&
          !linkedCaseFiles?.some((linked) => linked.id === caseFileOption.id)
      )
      .sort((a, b) => (a.name || "").localeCompare(b.name || ""));

  const caseFilesList = isEdit ? linkedCaseFilesOptions : filteredCaseFileList;

  const methods = useForm<LinkCaseFileFormType>({
    resolver: yupResolver(linkCaseFileSchema),
    mode: "onChange",
    defaultValues: initFormData,
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset(initFormData);
  }, [reset]);

  const onSubmitHandler = async (data: LinkCaseFileFormType) => {
    const caseFileId = (data.caseFile as CaseFile).id;
    onSubmit(caseFileId);
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <ModalTitleBar
          title={isEdit ? "Unlink from Case File" : "Link to Case File"}
        />
        <DialogContent dividers>
          <ControlledAutoComplete
            name="caseFile"
            label="Case File"
            placeholder="Select Case File"
            options={caseFilesList ?? []}
            getOptionLabel={(option) => option.name ?? ""}
            getOptionKey={(option) => option.id}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            fullWidth
            sx={{ mb: "-0.5rem" }}
            disabled={!caseFilesList?.length}
            isRequired={true}
          />
        </DialogContent>
        {caseFilesList && caseFilesList.length > 0 && (
          <ModalActions
            primaryActionButtonText={isEdit ? "Unlink" : "Link"}
            isButtonValidation
          />
        )}
      </form>
    </FormProvider>
  );
};

export default LinkCaseFileModal;
