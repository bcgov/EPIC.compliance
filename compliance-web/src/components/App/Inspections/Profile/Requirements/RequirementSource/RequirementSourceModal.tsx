import { Box, DialogContent, Stack } from "@mui/material";
import type React from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import * as yup from "yup";
import { FormProvider, useForm, useWatch } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import { RequirementSource } from "@/models/RequirementSource";
import { RequirementSourceFormData } from "@/models/InspectionRequirementSource";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import { useRequirementSourcesData } from "@/hooks/useComplaints";
import { RequirementSourceEnum } from "@/utils/constants";
import { requirementSourceNumberType } from "../RequirementUtils";
import ControlledLexicalEditor from "@/components/Shared/Controlled/ControlledLexicalEditor";
import { Appendix } from "@/models/Appendix";
import { InspectionOrder } from "@/models/InspectionOrder";
import { useInspectionOrdersProjectwiseData } from "@/hooks/useInspectionOrders";
import { CaseFile } from "@/models/CaseFile";
import { useCaseFileByNumber } from "@/hooks/useCaseFiles";
import { formatAuthorization } from "@/utils/appUtils";
import { RequirementImage } from "@/models/Image";
import ImagesRequirementSource from "../Images/ImagesRequirementSource";
import { useRequirementDetailImages } from "@/hooks/useInspectionRequirements";

type RequirementSourceModalProps = {
  onSubmit: (data: RequirementSourceFormData) => void;
  caseFile: CaseFile;
  requirementSourceFormData?: RequirementSourceFormData;
  requirementSource?: RequirementSource;
  order?: InspectionOrder;
  appendixList?: Appendix[];
  inspectionId: number;
  requirementId: number;
  isSectionModal?: boolean;
};

const requirementSourceFormSchema = yup.object().shape({
  requirementSource: yup
    .object<RequirementSource>()
    .nullable()
    .required("Requirement Source is required"),
  requirementSourceTitle: yup.string().nullable(),
  regulationNumber: yup.string().nullable(),
  exemptionOrderNumber: yup.string().nullable(),
  complianceNumber: yup.string().nullable(),
  amendmentNumber: yup.string().nullable(),
  clauseNumber: yup.string().nullable(),
  appendix: yup.object<Appendix>().nullable(),
  conditionNumber: yup.string().nullable(),
  sectionNumber: yup.string().nullable(),
  title: yup.string().nullable(),
  order: yup
    .object<InspectionOrder>()
    .nullable()
    .when("requirementSource", {
      is: (source: RequirementSource) =>
        source?.id === RequirementSourceEnum.ORDER,
      then: (schema) => schema.required("Order is required"),
      otherwise: (schema) => schema.nullable(),
    }),
  description: yup
    .object({
      html: yup.string().required("Description is required"),
      text: yup.string().required("Description is required"),
    })
    .nullable()
    .required("Description is required"),
});

type RequirementSourceSchemaType = yup.InferType<
  typeof requirementSourceFormSchema
>;

const initFormData: RequirementSourceFormData = {
  requirementSource: undefined,
  requirementSourceTitle: undefined,
  regulationNumber: undefined,
  exemptionOrderNumber: undefined,
  complianceNumber: undefined,
  amendmentNumber: undefined,
  appendix: undefined,
  conditionNumber: undefined,
  sectionNumber: undefined,
  clauseNumber: undefined,
  title: "",
  description: undefined,
  images: [],
};

const RequirementSourceModal: React.FC<RequirementSourceModalProps> = ({
  onSubmit,
  caseFile,
  requirementSourceFormData,
  requirementSource,
  order,
  appendixList,
  inspectionId,
  requirementId,
  isSectionModal = false,
}) => {
  const { data: requirementSourceList } = useRequirementSourcesData();
  const { data: orderList } = useInspectionOrdersProjectwiseData(caseFile.id);
  const { data: caseFileData } = useCaseFileByNumber(caseFile.case_file_number);
  
  // Fetch requirement detail images in edit mode (when requirementSourceFormData has an id)
  const detailId = requirementSourceFormData?.id;
  const { data: fetchedImages } = useRequirementDetailImages(
    inspectionId,
    requirementId,
    detailId
  );
  const defaultValues = useMemo<RequirementSourceFormData>(() => {
    return (
      requirementSourceFormData ?? {
        ...initFormData,
        requirementSource: requirementSource ?? undefined,
        order: order ?? undefined,
      }
    );
  }, [requirementSourceFormData, requirementSource, order]);

  const methods = useForm<RequirementSourceSchemaType>({
    resolver: yupResolver(requirementSourceFormSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { handleSubmit, reset, control, getValues, setValue } = methods;
  const hasUserEditedTitle = useRef(false);
  const hasUserEditedDescription = useRef(false);
  const currentRequirementSourceId = useRef<string | null>(null);

  const selectedRequirementSource = useWatch({
    control,
    name: "requirementSource",
    defaultValue: getValues("requirementSource") ?? undefined,
  }) as RequirementSource;

  const selectedOrder = useWatch({
    control,
    name: "order",
    defaultValue: getValues("order") ?? undefined,
  }) as InspectionOrder;

  const descriptionValue = useWatch({
    control,
    name: "description",
  });

  // Track when user manually edits the description
  useEffect(() => {
    if (descriptionValue && !hasUserEditedDescription.current) {
      const currentDescription = getValues("description");
      if (currentDescription?.html !== selectedOrder?.now_therefore) {
        hasUserEditedDescription.current = true;
      }
    }
  }, [descriptionValue, getValues, selectedOrder]);

  useEffect(() => {
    if (
      !requirementSourceFormData &&
      selectedOrder?.now_therefore &&
      !hasUserEditedDescription.current
    ) {
      const newValue = {
        html: selectedOrder.now_therefore,
        text: selectedOrder.now_therefore,
      };
      setValue("description", newValue);

      // Auto-fill source title for Order
      if (
        selectedRequirementSource?.id === RequirementSourceEnum.ORDER &&
        !hasUserEditedTitle.current
      ) {
        // Extract order number without project code prefix
        let orderNumber = selectedOrder.order_number || "";
        // strip the project code prefix if orderNumber matches the expected format (e.g., "FRARIV_20250007_OR002")
        // The expected format is: <projectCode>_<number>_<suffix>
        if (/^[A-Z]+_\d+_/.test(orderNumber)) {
          const underscoreIndex = orderNumber.indexOf("_");
          if (underscoreIndex !== -1) {
            orderNumber = orderNumber.substring(underscoreIndex + 1);
          }
        }

        // Set the source title as "Order orderNumber"
        setValue("requirementSourceTitle", `Order ${orderNumber}`);
      }
    }
  }, [
    selectedOrder,
    setValue,
    requirementSourceFormData,
    selectedRequirementSource,
  ]);

  useEffect(() => {
    reset(defaultValues);
    // Reset the user edit flags when form is reset
    hasUserEditedTitle.current = false;
    hasUserEditedDescription.current = false;
    currentRequirementSourceId.current = null;
  }, [defaultValues, reset]);

  useEffect(() => {
    if (selectedRequirementSource) {
      // Check if requirement source has changed
      const hasSourceChanged =
        currentRequirementSourceId.current !== selectedRequirementSource.id;

      if (hasSourceChanged) {
        // Reset the edit flag when source changes
        hasUserEditedTitle.current = false;
        currentRequirementSourceId.current = selectedRequirementSource.id;

        let sourceTitle = selectedRequirementSource.source_title;
        if (sourceTitle && sourceTitle.includes("${eac#}")) {
          sourceTitle = sourceTitle.replace(
            "${eac#}",
            caseFileData?.authorization ?? ""
          );
        }
        if (sourceTitle && sourceTitle.includes("${eac_type}")) {
          const eacType = formatAuthorization(
            caseFileData?.authorization,
            true
          );
          sourceTitle = sourceTitle.replace("${eac_type}", eacType);
        }
        setValue("requirementSourceTitle", sourceTitle);
      }
    }
  }, [selectedRequirementSource, setValue, caseFileData]);

  const [uploadedImages, setUploadedImages] = useState<RequirementImage[]>(
    requirementSourceFormData?.images ?? []
  );
  // Update uploadedImages when fetched images are available (edit mode)
  useEffect(() => {
    if (fetchedImages && detailId && uploadedImages.length == 0) {
      setUploadedImages(fetchedImages);
    }
  }, [fetchedImages, detailId, uploadedImages]);

  const onSubmitHandler = (data: RequirementSourceSchemaType) => {
    const formData = data as RequirementSourceFormData;
    if (!requirementSourceFormData) {
      formData.id = Date.now();
    }
    uploadedImages.forEach((image) => {
      if (image.dbId) {
        image.id = image.dbId;
      } else {
        image.id = Date.now();
      }
    });
    formData.images = uploadedImages;
    onSubmit(formData);
  };

  const handleTitleChange = () => {
    hasUserEditedTitle.current = true;
  };

  return (
    <>
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmitHandler)}>
          <ModalTitleBar
            title={
              requirementSourceFormData
                ? "Edit Requirement Source"
                : "Add Requirement Source"
            }
          />
          <DialogContent
            dividers
            sx={{ height: "60vh", display: "flex", flexDirection: "column" }}
          >
            <Stack direction={"row"} gap={2} sx={{ flex: 1, minHeight: 0 }}>
              <Box flex={1}>
                <ControlledAutoComplete
                  name="requirementSource"
                  label="Requirement Source"
                  options={requirementSourceList ?? []}
                  getOptionLabel={(option) => option.name}
                  getOptionKey={(option) => option.id}
                  isOptionEqualToValue={(option, value) =>
                    option.id === value.id
                  }
                  disabled={!!requirementSourceFormData || !!requirementSource}
                  isRequired={true}
                />
                {selectedRequirementSource?.id ===
                  RequirementSourceEnum.ORDER && (
                  <ControlledAutoComplete
                    name="order"
                    label="Order Number"
                    options={orderList ?? []}
                    getOptionLabel={(option) => option.order_number ?? ""}
                    getOptionKey={(option) => option.id ?? ""}
                    isOptionEqualToValue={(option, value) =>
                      option.id === value.id
                    }
                    disabled={!!requirementSourceFormData || !!order}
                    isRequired={true}
                  />
                )}
                {selectedRequirementSource && (
                  <Stack direction={"row"} gap={2}>
                    {!isSectionModal && (
                      <ControlledTextField
                        name="requirementSourceTitle"
                        label="Source Title"
                        fullWidth
                        onChange={handleTitleChange}
                        multiline
                      />
                    )}
                    {selectedRequirementSource?.id ===
                      RequirementSourceEnum.REGULATION && (
                      <ControlledTextField
                        name="regulationNumber"
                        label="Regulation #"
                        fullWidth
                      />
                    )}
                    {selectedRequirementSource?.id ===
                      RequirementSourceEnum.COMPLAINCE_AGREEMENT && (
                      <ControlledTextField
                        name="complianceNumber"
                        label="#"
                        fullWidth
                      />
                    )}
                    {selectedRequirementSource?.id ===
                      RequirementSourceEnum.EACA && (
                      <ControlledTextField
                        name="amendmentNumber"
                        label="Amendment #"
                        fullWidth
                      />
                    )}
                  </Stack>
                )}
                <ControlledAutoComplete
                  name="appendix"
                  label="Inspection Record Appendix #"
                  options={appendixList ?? []}
                  getOptionLabel={(option) => {
                    return `Appendix ${option.appendix_no}: ${option.document_title}`;
                  }}
                  getOptionKey={(option) => option.id ?? ""}
                  isOptionEqualToValue={(option, value) =>
                    option.id === value.id
                  }
                />
                {selectedRequirementSource?.id !==
                  RequirementSourceEnum.ORDER && (
                  <>
                    {requirementSourceNumberType(
                      selectedRequirementSource?.id ?? ""
                    ).toLowerCase() === "condition" && (
                      <ControlledTextField
                        name="conditionNumber"
                        label="Condition #"
                        fullWidth
                      />
                    )}
                    {requirementSourceNumberType(
                      selectedRequirementSource?.id ?? ""
                    ).toLowerCase() === "section" && (
                      <ControlledTextField
                        name="sectionNumber"
                        label="Section #"
                        fullWidth
                      />
                    )}
                    {requirementSourceNumberType(
                      selectedRequirementSource?.id ?? ""
                    ).toLowerCase() === "clause" && (
                      <ControlledTextField
                        name="clauseNumber"
                        label="Clause #"
                        fullWidth
                      />
                    )}
                    <ControlledTextField
                      name="title"
                      label="Title"
                      fullWidth
                      multiline
                    />
                  </>
                )}
              </Box>
              <Box
                width={"680px"}
                display="flex"
                flexDirection="column"
                height="100%"
                sx={{ minHeight: 0 }}
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
                  inspectionId={caseFile.id}
                />
              </Box>
            </Stack>
          </DialogContent>
          <ModalActions
            primaryActionButtonText={requirementSourceFormData ? "Save" : "Add"}
          />
        </form>
      </FormProvider>
    </>
  );
};

export default RequirementSourceModal;
