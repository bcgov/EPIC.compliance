import { Box, Collapse, DialogContent, Typography } from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import * as yup from "yup";
import { FormProvider, useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import { useDocumentTypesData } from "@/hooks/useInspectionRequirements";
import {
  RequirementRelatedDocumentSectionFormData,
  RequirementRelatedDocumentData,
  RequirementSourceFormData,
  RequirementRelatedDocumentSectionData,
} from "@/models/InspectionRequirementSource";
import { RequirementDocumentType } from "@/models/RequirementDocumentType";
import { BCDesignTokens } from "epic.theme";
import {
  RequirementDocumentTypeEnum,
  RequirementSourceEnum,
} from "@/utils/constants";
import ControlledLexicalEditor from "@/components/Shared/Controlled/ControlledLexicalEditor";
import { Appendix } from "@/models/Appendix";
import { requirementSourceNumberType } from "@/components/App/Inspections/Profile/Requirements/RequirementUtils";
import ImagesRequirementSource from "../Images/ImagesRequirementSource";
import { RequirementImage } from "@/models/Image";
import { ExpandMoreRounded } from "@mui/icons-material";
import { MQ } from "@/styles/responsive";

type RequirementRelatedDocumentModalProps = {
  onSubmit: (data: RequirementRelatedDocumentData, requirementSourceId?: string, sectionNumber?: string) => void;
  requirementSourceData: RequirementSourceFormData;
  relatedDocumentData?: RequirementRelatedDocumentData;
  relatedDocumentSectionData?: RequirementRelatedDocumentSectionData;
  documentTitle?: string;
  appendixList?: Appendix[];
  isEditSection?: boolean;
  inspectionId: number;
  relatedDocumentImages?: RequirementImage[];
  isSectionModal?: boolean;
};

const relatedDocumentFormSchema = yup.object().shape({
  relatedDocument: yup
    .object<RequirementDocumentType>()
    .nullable()
    .required("Related Document is required"),
  appendix: yup.object<Appendix>().nullable(),
  documentTitle: yup.string().nullable(),
  sectionNumber: yup.string().nullable(),
  sectionTitle: yup.string().nullable(),
  description: yup
    .object({
      html: yup.string().required("Description is required"),
      text: yup.string().required("Description is required"),
    })
    .nullable()
    .required("Description is required"),
});

type RequirementRelatedDocumentSchemaType = yup.InferType<
  typeof relatedDocumentFormSchema
>;

const DocumentTitleInfo = () => {
  const [isInfoExpanded, setIsInfoExpanded] = useState(false);

  return (
    <Box
      sx={{ display: "flex", gap: 1, cursor: "pointer" }}
      onClick={() => setIsInfoExpanded(!isInfoExpanded)}
    >
      <ExpandMoreRounded
        sx={{
          marginTop: "-0.125rem",
          fontSize: "1.25rem",
          transform: isInfoExpanded ? "rotate(180deg)" : "rotate(270deg)",
        }}
      />
      <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
        <Typography variant="caption">How to record Document Title</Typography>
        <Collapse in={isInfoExpanded}>
          <Typography variant="caption">
            Record the Document Title in the format of [Plan
            Name], [Version], [Date], ex., Water Management Plan,
            Rev3, Dec. 21, 2023.
          </Typography>
        </Collapse>
      </Box>
    </Box>
  );
};

const RequirementRelatedDocumentModal: React.FC<
  RequirementRelatedDocumentModalProps
> = ({
  onSubmit,
  requirementSourceData,
  relatedDocumentData,
  relatedDocumentSectionData,
  documentTitle,
  appendixList,
  isEditSection,
  inspectionId,
  relatedDocumentImages,
  isSectionModal,
}) => {
    const { data: documentTypeList } = useDocumentTypesData();
    const [uploadedImages, setUploadedImages] = useState<RequirementImage[]>(
      relatedDocumentImages ?? []
    );

    const isScheduleB =
      requirementSourceData.requirementSource?.id ===
      RequirementSourceEnum.SCHEDULE_B;

    const isOrder =
      requirementSourceData.requirementSource?.id === RequirementSourceEnum.ORDER;

    const sourceNumberType = requirementSourceNumberType(
      requirementSourceData.requirementSource?.id ?? ""
    );

    const defaultValues =
      useMemo<RequirementRelatedDocumentSectionFormData>(() => {
        const defaultData: RequirementRelatedDocumentSectionFormData = {
          documentTitle: documentTitle,
          sectionNumber: "",
          sectionTitle: "",
          description: undefined,
          appendix: undefined,
        };
        if (relatedDocumentData) {
          defaultData.relatedDocument =
            relatedDocumentData.relatedDocument ?? undefined;
          defaultData.documentTitle = relatedDocumentData.documentTitle ?? "";
          defaultData.appendix = relatedDocumentData?.appendix ?? undefined;
          if (isEditSection) {
            defaultData.sectionNumber =
              relatedDocumentSectionData?.sectionNumber ?? "";
            defaultData.sectionTitle =
              relatedDocumentSectionData?.sectionTitle ?? "";
            defaultData.description =
              relatedDocumentSectionData?.description ?? undefined;
          }
        }
        if (!isScheduleB) {
          return {
            ...defaultData,
            relatedDocument: documentTypeList?.find(
              (doc) => doc.id === RequirementDocumentTypeEnum.OTHER_DOCUMENT
            ), // auto select "Other Document" if not Schedule B
          };
        }
        return defaultData;
      }, [
        relatedDocumentData,
        isScheduleB,
        documentTypeList,
        isEditSection,
        relatedDocumentSectionData,
        documentTitle,
      ]);

    const methods = useForm<RequirementRelatedDocumentSchemaType>({
      resolver: yupResolver(relatedDocumentFormSchema),
      mode: "onBlur",
      defaultValues,
    });

    const { handleSubmit, reset } = methods;

    useEffect(() => {
      reset(defaultValues);
    }, [defaultValues, reset]);

    const onSubmitHandler = (data: RequirementRelatedDocumentSchemaType) => {
      const formData = data as RequirementRelatedDocumentSectionFormData;

      // Process images similar to RequirementSourceModal
      uploadedImages.forEach((image) => {
        if (image.dbId) {
          image.id = image.dbId;
        } else {
          image.id = Date.now();
        }
      });

      const reqRelatedDocumentData: RequirementRelatedDocumentData = {
        id: relatedDocumentData?.id ?? Date.now(),
        sourceFormId: requirementSourceData.id,
        relatedDocument: formData.relatedDocument,
        documentTitle: formData.documentTitle,
        appendix: formData.appendix,
        sections: relatedDocumentData?.sections ?? [],
      };
      const reqSectionData: RequirementRelatedDocumentSectionData = {
        id: relatedDocumentSectionData?.id ?? Date.now(),
        dbId: relatedDocumentSectionData?.dbId ?? undefined,
        sourceFormId: requirementSourceData.id,
        relatedDocumentFormId:
          relatedDocumentData?.id ?? reqRelatedDocumentData.id,
        appendix: formData.appendix,
        sectionNumber: formData.sectionNumber,
        sectionTitle: formData.sectionTitle,
        description: formData.description,
        images: uploadedImages,
      };
      if (isEditSection) {
        reqRelatedDocumentData.sections = reqRelatedDocumentData.sections?.map(
          (section) =>
            section.id === reqSectionData.id ? reqSectionData : section
        );
      } else {
        reqRelatedDocumentData.sections?.push(reqSectionData);
      }
      onSubmit(reqRelatedDocumentData, requirementSourceData.requirementSource?.id, requirementSourceData.sectionNumber);
    };
    return (
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmitHandler)}>
          <ModalTitleBar
            title={
              relatedDocumentData
                ? isEditSection
                  ? "Edit Related Document"
                  : "Add Section"
                : "Add Related Document"
            }
          />
          <DialogContent
            dividers
            sx={{ height: "50vh", display: "flex", flexDirection: "column" }}
          >
            <Box
              gap={2}
              sx={{
                flex: 1,
                minHeight: 0,
                display: "flex",
                flexDirection: "row",
                [MQ.mdToLg]: {
                  flexDirection: "column",
                  overflow: "auto",
                  gap: 0,
                }
              }}>
              <Box flex={1}>
                <Box
                  sx={{
                    display: "flex",
                    gap: 3,
                    mb: 2,
                    p: "0.75rem",
                    backgroundColor:
                      BCDesignTokens.surfaceColorBackgroundLightBlue,
                    borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
                  }}
                >
                  <Box
                    width={isOrder ? "100%" : "40%"}
                    display="flex"
                    flexDirection="column"
                    gap={0.5}
                  >
                    <Typography variant="caption" fontWeight={700}>
                      Title:
                    </Typography>
                    <Typography variant="body2">
                      {requirementSourceData.requirementSource?.name}
                      {isOrder &&
                        ` — ${requirementSourceData.order?.order_number ?? ""}`}
                    </Typography>
                  </Box>
                  {!isOrder && (
                    <Box display="flex" flexDirection="column" gap={0.5}>
                      <Typography variant="caption" fontWeight={700}>
                        {sourceNumberType} #:
                      </Typography>
                      <Typography variant="body2">
                        {String(
                          requirementSourceData[
                          `${sourceNumberType.toLowerCase()}Number` as keyof RequirementSourceFormData
                          ] ?? ""
                        )}
                      </Typography>
                    </Box>
                  )}
                </Box>
                <ControlledAutoComplete
                  name="relatedDocument"
                  label="Related Document"
                  options={documentTypeList ?? []}
                  getOptionLabel={(option) => option.name}
                  getOptionKey={(option) => option.id}
                  isOptionEqualToValue={(option, value) => option.id === value.id}
                  disabled={!isScheduleB || isEditSection}
                  isRequired={true}
                />
                <ControlledTextField
                  name="documentTitle"
                  label="Document Title"
                  placeholder="Water Management Plan, Rev3, Dec. 21, 2023"
                  multiline
                  fullWidth
                  disabled={isSectionModal}
                />
                <DocumentTitleInfo />
                <ControlledTextField
                  name="sectionNumber"
                  label="Section #"
                  fullWidth
                />
                <ControlledTextField
                  name="sectionTitle"
                  label="Section Title"
                  fullWidth
                  multiline
                />
                <ControlledAutoComplete
                  name="appendix"
                  label="Inspection Record Appendix #"
                  options={appendixList ?? []}
                  getOptionLabel={(option) =>
                    `Appendix ${option.appendix_no}: ${option.document_title}`
                  }
                  getOptionKey={(option) => option.id ?? ""}
                  isOptionEqualToValue={(option, value) => option.id === value.id}
                />
              </Box>
              <Box
                width={"680px"}
                display="flex"
                flexDirection="column"
                height="100%"
                sx={{
                  minHeight: 0,
                  [MQ.mdToLg]: {
                    width: "auto",
                    minHeight: "unset",
                  }
                }}
              >
                <Box
                  flex={1}
                  display="flex"
                  flexDirection="column"
                  sx={{ minHeight: 0 }}
                >
                  <Box
                    sx={{
                      flex: 1,
                      display: "flex",
                      flexDirection: "column",
                      minHeight: 0,
                      "& .MuiFormControl-root": {
                        marginBottom: 0,
                        height: "100%",
                        display: "flex",
                        flexDirection: "column",
                        flex: 1,
                      },
                      "& .editor-container": {
                        flex: 1,
                        minHeight: 0,
                      },
                    }}
                  >
                    <ControlledLexicalEditor
                      label="Description"
                      name="description"
                      isAdvanced
                      isRequired={true}
                      height={"100%"}
                    />
                  </Box>
                </Box>
                <ImagesRequirementSource
                  uploadedImages={uploadedImages}
                  setUploadedImages={setUploadedImages}
                  inspectionId={inspectionId}
                />
              </Box>
            </Box>
          </DialogContent>
          <ModalActions
            primaryActionButtonText={
              relatedDocumentData ? (isEditSection ? "Save" : "Add") : "Add"
            }
          />
        </form>
      </FormProvider>
    );
  };

export default RequirementRelatedDocumentModal;
