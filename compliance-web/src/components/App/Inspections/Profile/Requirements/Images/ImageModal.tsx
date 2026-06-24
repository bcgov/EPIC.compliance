import { Box, DialogContent, Grid } from "@mui/material";
import * as yup from "yup";
import { FormProvider, useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import { StaffUser } from "@/models/Staff";
import { useStaffUsersData } from "@/hooks/useStaff";
import { BCDesignTokens } from "epic.theme";
import GridLabelValuePair from "@/components/Shared/GridLabelValuePair";
import { ImageFormData, RequirementImage } from "@/models/Image";
import { useEffect, useMemo } from "react";
import { useImageUpload } from "@/hooks/useImageUpload";
import dayjs from "dayjs";
import dateUtils from "@/utils/dateUtils";
import { ImageTypeEnum } from "@/components/App/Inspections/Profile/Requirements/RequirementUtils";
import { downscaleImage } from "@/utils/imageDownscale";

type ImageModalProps = {
  file?: File;
  onSubmit: (data: RequirementImage) => void;
  onDelete?: (imageId: number) => void;
  requirementImage?: RequirementImage;
  inspectionId: number;
  imageType: ImageTypeEnum;
  imageIndex?: number;
  primaryOfficer?: StaffUser;
};

const OTHER_STAFF_ID = -1;

const imageFormSchema = (isPhoto: boolean) =>
  yup.object().shape({
    ...(isPhoto && {
      takenBy: yup
        .object<StaffUser>()
        .nullable()
        .required("Taken By is required"),
      takenByOther: yup
        .string()
        .nullable()
        .when("takenBy", {
          is: (takenBy: StaffUser | null | undefined) =>
            !!takenBy &&
            (takenBy.id === OTHER_STAFF_ID || takenBy.name === "Other"),
          then: (schema) =>
            schema.required("Please specify who took the photo"),
          otherwise: (schema) => schema.strip(),
        }),
    }),
    caption: yup.string().nullable().required("Caption is required"),
  });

type ImageSchemaType = yup.InferType<ReturnType<typeof imageFormSchema>>;

const getInitFormData = (primaryOfficer?: StaffUser): ImageFormData => ({
  takenBy: primaryOfficer,
  caption: "",
  takenByOther: "",
});

const ImageModal: React.FC<ImageModalProps> = ({
  file,
  onSubmit,
  onDelete,
  requirementImage,
  inspectionId,
  imageType,
  imageIndex,
  primaryOfficer,
}) => {
  const { data: staffUserList } = useStaffUsersData();
  const isPhoto = imageType === ImageTypeEnum.PHOTO;
  const ImageTypeLabel = isPhoto ? "Photo" : "Figure";
  const staffOptions = useMemo<StaffUser[]>(() => {
    if (!isPhoto) return staffUserList ?? [];
    const list = staffUserList ?? [];
    // Avoid duplicate "Other"
    const hasOther = list.some(
      (s) => s.id === OTHER_STAFF_ID || s.name === "Other"
    );
    return hasOther
      ? list
      : [
          { id: OTHER_STAFF_ID, name: "Other", is_active: true } as StaffUser,
          ...list,
        ];
  }, [isPhoto, staffUserList]);
  const defaultValues = useMemo<ImageFormData>(() => {
    return requirementImage
      ? {
          takenBy:
            requirementImage.taken_by ??
            staffOptions?.find((s) => s.id === OTHER_STAFF_ID),
          takenByOther: requirementImage.taken_by_text ?? "",
          caption: requirementImage.caption,
        }
      : getInitFormData(primaryOfficer);
  }, [requirementImage, primaryOfficer, staffOptions]);

  const methods = useForm<ImageSchemaType>({
    resolver: yupResolver(imageFormSchema(isPhoto)),
    mode: "onBlur",
    defaultValues,
  });

  const { handleSubmit, reset, getValues, watch } = methods;
  const selectedTakenBy = watch("takenBy") as StaffUser | null | undefined;

  const onSuccess = (uploadedFile: {
    presigned_url: string;
    relative_url: string;
  }) => {
    const selected = isPhoto
      ? (getValues("takenBy") as StaffUser)
      : primaryOfficer;
    const isOtherSelected =
      isPhoto && (selected as StaffUser | undefined)?.id === OTHER_STAFF_ID;
    const takenBy = isOtherSelected ? undefined : selected;
    const imageFormData: RequirementImage = {
      id: Date.now(),
      relative_url: uploadedFile.relative_url,
      url: uploadedFile.presigned_url,
      caption: getValues("caption"),
      taken_by: takenBy,
      taken_by_id: takenBy?.id,
      taken_by_text: isOtherSelected ? getValues("takenByOther") : undefined,
      original_file_name: file?.name ?? "",
      date_taken: file?.lastModified
        ? dateUtils.dateToISO(dayjs(file.lastModified))
        : undefined,
      image_type: ImageTypeLabel,
    };
    onSubmit(imageFormData);
  };

  const { mutate: uploadImage, isPending } = useImageUpload(onSuccess);

  useEffect(() => {
    reset(defaultValues);
  }, [defaultValues, reset]);

  const onSubmitHandler = async (data: ImageSchemaType) => {
    if (requirementImage) {
      const formData = data as ImageFormData;
      const isOtherSelected =
        isPhoto &&
        (formData.takenBy as StaffUser | undefined)?.id === OTHER_STAFF_ID;
      const takenBy = isOtherSelected
        ? undefined
        : isPhoto
          ? formData.takenBy
          : primaryOfficer;
      onSubmit({
        ...requirementImage,
        caption: formData.caption,
        taken_by_id: takenBy?.id,
        taken_by: takenBy,
        taken_by_text: isOtherSelected ? formData.takenByOther : undefined,
      });
    } else {
      const processedFile = file ? await downscaleImage(file) : new File([], "");
      uploadImage({
        inspectionId,
        fileName: processedFile.name,
        file: processedFile,
      });
    }
  };

  const onDeleteHandler = () => {
    onDelete?.(requirementImage?.id ?? 0);
  };

  return (
    <>
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmitHandler)}>
          <ModalTitleBar
            title={`${requirementImage ? "Edit" : "Add"} ${ImageTypeLabel}`}
          />
          <DialogContent dividers>
            <Box
              sx={{
                width: "100%",
                height: "300px",
                borderRadius: "4px",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                marginBottom: "1rem",
              }}
            >
              <img
                src={
                  file
                    ? URL.createObjectURL(file)
                    : (requirementImage?.url ?? "")
                }
                alt="Preview"
                style={{ maxHeight: "100%", maxWidth: "100%" }}
              />
            </Box>
            <Grid
              container
              spacing={1}
              wrap="nowrap"
              sx={{
                padding: 1.5,
                borderRadius: 0.5,
                background: BCDesignTokens.surfaceColorBackgroundLightBlue,
                marginLeft: 0,
                width: "100%",
                my: 2,
              }}
            >
              <GridLabelValuePair
                label={`${ImageTypeLabel} #`}
                value={imageIndex ?? requirementImage?.sort_order ?? 0}
                gridProps={{ xs: 2 }}
                isBold
              />
              <GridLabelValuePair
                label="File Name"
                value={
                  file
                    ? file.name
                    : requirementImage?.original_file_name || "No file selected"
                }
                gridProps={{ xs: 6 }}
                isBold
              />
              <GridLabelValuePair
                label="File Date"
                value={
                  file
                    ? dateUtils.formatDate(
                        dayjs(file.lastModified).toISOString()
                      )
                    : dateUtils.formatDate(
                        requirementImage?.date_taken ?? ""
                      ) || "No file selected"
                }
                gridProps={{ xs: 4 }}
                isBold
              />
            </Grid>
            {isPhoto && (
              <>
                <ControlledAutoComplete
                  name="takenBy"
                  label="Taken By"
                  options={staffOptions}
                  getOptionLabel={(option) => option.name}
                  getOptionKey={(option) => option.id}
                  isOptionEqualToValue={(option, value) =>
                    option.id === value.id
                  }
                  isRequired={true}
                />
                {(selectedTakenBy?.id === OTHER_STAFF_ID ||
                  selectedTakenBy?.name === "Other") && (
                  <ControlledTextField
                    name="takenByOther"
                    label="Taken By Other"
                    fullWidth
                    isRequired={true}
                  />
                )}
              </>
            )}
            <ControlledTextField
              name="caption"
              label="Caption"
              fullWidth
              multiline
              isRequired={true}
            />
          </DialogContent>
          <ModalActions
            primaryActionButtonText={requirementImage ? "Save" : "Add"}
            onDeleteAction={requirementImage ? onDeleteHandler : undefined}
            onDeleteConfirmationText={`Are you sure you want to delete this ${ImageTypeLabel}?`}
            isLoading={isPending}
          />
        </form>
      </FormProvider>
    </>
  );
};

export default ImageModal;
