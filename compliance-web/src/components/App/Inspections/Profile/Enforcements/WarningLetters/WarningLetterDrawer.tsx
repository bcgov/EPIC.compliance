import DrawerActionBarBottom from "@/components/Shared/Drawer/DrawerActionBarBottom";
import DrawerTitleBar from "@/components/Shared/Drawer/DrawerTitleBar";
import { Inspection } from "@/models/Inspection";
import { useMenuStore } from "@/store/menuStore";
import { yupResolver } from "@hookform/resolvers/yup";
import { Box, Button, Stack } from "@mui/material";
import { useCallback, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { StaffUser } from "@/models/Staff";
import dayjs, { Dayjs } from "dayjs";
import ControlledLexicalEditor from "@/components/Shared/Controlled/ControlledLexicalEditor";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import ControlledDateField from "@/components/Shared/Controlled/ControlledDateField";
import { BCDesignTokens } from "epic.theme";
import {
  InspectionWarningLetter,
  InspectionWarningLetterAPIData,
} from "@/models/InspectionWarningLetter";
import {
  useDeleteWarningLetter,
  useResetWarningLetterTemplate,
  useUpdateWarningLetter,
} from "@/hooks/useInspectionWarningLetters";
import EnforcementDownloadPDFButton from "@/components/App/Inspections/Profile/Enforcements/EnforcementDownloadPDFButton";
import {
  EnforcementActionEnum,
  WarningLetterProgressEnum,
  WarningLetterStatusEnum,
} from "@/utils/constants";
import WarningLetterApprovalButtons from "@/components/App/Inspections/Profile/Enforcements/WarningLetters/WarningLetterApprovalButtons";
import EnforcementStatusFlag from "@/components/App/Inspections/Profile/Enforcements/EnforcementStatusFlag";
import { RestartAltRounded } from "@mui/icons-material";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import { useModal } from "@/store/modalStore";
import { useQueryClient } from "@tanstack/react-query";

type WarningLetterDrawerProps = {
  onSubmit: (submitMsg: string, isCloseDrawer?: boolean) => void;
  inspection: Inspection;
  warningLetter: InspectionWarningLetter;
  staffUsersList: StaffUser[];
  isReadonlyMode?: boolean;
};

const warningLetterFormSchema = yup.object().shape({
  content: yup
    .object({
      html: yup.string(),
      text: yup.string(),
    })
    .nullable(),
  issuingOfficer: yup
    .object<StaffUser>()
    .nullable()
    .required("Issuing Officer is required"),
  intendedIssuanceDate: yup.mixed<Dayjs>().nullable().typeError("Invalid date"),
});

type EnforcementFormType = yup.InferType<typeof warningLetterFormSchema>;

const initFormData = {
  content: { html: "", text: "" },
  issuingOfficer: {} as StaffUser,
  intendedIssuanceDate: undefined,
};

const WarningLetterDrawer: React.FC<WarningLetterDrawerProps> = ({
  onSubmit,
  inspection,
  warningLetter,
  staffUsersList,
  isReadonlyMode,
}) => {
  const { appHeaderHeight } = useMenuStore();
  const { setOpen: setModalOpen, setClose: setModalClose } = useModal();
  const queryClient = useQueryClient();

  const isDrafting = useMemo(
    () => warningLetter.progress?.id === WarningLetterProgressEnum.DRAFTING,
    [warningLetter.progress]
  );

  const isWarningLetterClosed = useMemo(
    () => warningLetter.status?.id === WarningLetterStatusEnum.ISSUED,
    [warningLetter.status]
  );

  const formatFormData = useCallback((data: InspectionWarningLetter) => {
    return {
      content: {
        html: data.content,
        text: data.content,
      },
      issuingOfficer: data.issuing_officer as StaffUser,
      intendedIssuanceDate: data.intended_issuance_date
        ? dayjs(data.intended_issuance_date)
        : undefined,
    };
  }, []);

  const defaultValues = useMemo<EnforcementFormType>(() => {
    if (warningLetter) {
      return formatFormData(warningLetter);
    }
    return initFormData;
  }, [warningLetter, formatFormData]);

  const methods = useForm<EnforcementFormType>({
    resolver: yupResolver(warningLetterFormSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { handleSubmit, reset } = methods;

  const onSuccess = useCallback(
    (data: InspectionWarningLetter) => {
      // Update the specific warning letter in cache with new data
      queryClient.setQueryData(
        ["inspection-warning-letters", inspection.id],
        (oldData: InspectionWarningLetter[] | undefined) => {
          if (!oldData) return oldData;
          return oldData.map((wl) => (wl.id === data.id ? data : wl));
        }
      );

      onSubmit("Changes saved successfully!");
      reset(formatFormData(data));
    },
    [onSubmit, reset, formatFormData, queryClient, inspection.id]
  );

  const {
    mutate: updateWarningLetter,
    isPending: isUpdateWarningLetterPending,
  } = useUpdateWarningLetter(onSuccess);

  const onSubmitHandler = useCallback(
    (formData: EnforcementFormType) => {
      if (warningLetter) {
        const warningLetterData: InspectionWarningLetterAPIData = {
          inspection_id: inspection.id,
          inspection_requirement_ids:
            warningLetter.warning_letter_requirement_maps?.map(
              (map) => map.inspection_requirement_id
            ) || [],
          content: formData.content?.html || undefined,
          issuing_officer_id: (formData.issuingOfficer as StaffUser).id,
          intended_issuance_date:
            formData.intendedIssuanceDate?.toISOString() || undefined,
        };

        updateWarningLetter({
          inspectionWarningLetterId: warningLetter.id || 0,
          inspectionWarningLetter: warningLetterData,
        });
      }
    },
    [inspection.id, updateWarningLetter, warningLetter]
  );

  const onDeleteSuccess = useCallback(() => {
    onSubmit("Warning letter deleted successfully!", true);
    reset();
  }, [onSubmit, reset]);

  const { mutate: deleteWarningLetter } =
    useDeleteWarningLetter(onDeleteSuccess);

  const onDeleteWarningLetter = useCallback(() => {
    deleteWarningLetter({
      inspectionWarningLetterId: warningLetter.id || 0,
    });
  }, [deleteWarningLetter, warningLetter.id]);

  const { mutate: resetWarningLetterTemplate } =
    useResetWarningLetterTemplate(onSuccess);

  const onResetTemplate = useCallback(() => {
    setModalOpen({
      content: (
        <ConfirmationModal
          title="Reset Template"
          description="This will reset the template to its default version. All your changes will be permanently removed and cannot be undone. Do you want to proceed?"
          confirmButtonText="Yes, Reset"
          cancelButtonText="No, Keep Changes"
          onConfirm={() => {
            resetWarningLetterTemplate({
              inspectionWarningLetterId: warningLetter.id || 0,
              fieldName: "content",
            });
            setModalClose();
          }}
        />
      ),
    });
  }, [
    resetWarningLetterTemplate,
    warningLetter.id,
    setModalOpen,
    setModalClose,
  ]);

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <DrawerTitleBar
          title={warningLetter.warning_letter_number || "Edit Warning Letter"}
          isFormDirtyCheck
          statusFlag={
            <EnforcementStatusFlag
              enforcementActionType={EnforcementActionEnum.WARNING_LETTER}
              warningLetter={warningLetter}
            />
          }
        />
        <Box
          sx={{
            backgroundColor: BCDesignTokens.surfaceColorBackgroundLightGray,
            padding: "0.75rem 2rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 1,
          }}
        >
          <Button
            variant="text"
            size="small"
            onClick={onResetTemplate}
            startIcon={<RestartAltRounded />}
            disabled={!isDrafting}
          >
            Reset Template
          </Button>
          <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
            {!isReadonlyMode && (
              <WarningLetterApprovalButtons
                warningLetter={warningLetter}
                inspectionId={inspection.id}
              />
            )}
            <EnforcementDownloadPDFButton
              enforcementId={warningLetter.id || 0}
              fileNumber={warningLetter.warning_letter_number || ""}
              enforcementType={EnforcementActionEnum.WARNING_LETTER}
            />
          </Box>
        </Box>
        <Stack
          /** 64px (DrawerTitleBar height) + 65px (DrawerActionBar height) + 64px (DrawerActionBarTop preview height) */
          height={`calc(100vh - ${appHeaderHeight + 193 - (isWarningLetterClosed ? 65 : 0)}px)`}
          direction={"row"}
        >
          <Box
            sx={{
              background: BCDesignTokens.surfaceColorBackgroundLightGray,
              padding: "0.5rem 1rem 1rem 2rem",
              width: "718px",
              overflow: "auto",
              boxSizing: "border-box",
            }}
          >
            <ControlledLexicalEditor
              label=""
              name="content"
              isAdvanced={true}
              height={`calc(100vh - ${appHeaderHeight + 235}px)`}
              disabled={isWarningLetterClosed}
            />
          </Box>
          <Box
            sx={{
              padding: "1.5rem 2rem 1rem 1rem",
              width: "510px",
              overflow: "auto",
              boxSizing: "border-box",
            }}
          >
            <ControlledAutoComplete
              name="issuingOfficer"
              label="Issuing Officer Name"
              options={staffUsersList}
              getOptionLabel={(option) => option.name}
              getOptionKey={(option) => option.id}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              fullWidth
              isSortOptions
              isRequired={true}
              disabled={isWarningLetterClosed}
            />
            <ControlledDateField
              className="cy-intended-issuance-date"
              name="intendedIssuanceDate"
              label="Intended Issuance Date"
              sx={{ width: "100%" }}
              disabled={isWarningLetterClosed}
            />
          </Box>
        </Stack>
        <DrawerActionBarBottom
          isShowActionBar={!!warningLetter && !isWarningLetterClosed}
          onDeleteAction={onDeleteWarningLetter}
          onDeleteTitle="Delete Warning Letter"
          onDeleteDescription={`You are about to delete Warning Letter ${warningLetter.warning_letter_number}. Are you sure?`}
          isLoading={isUpdateWarningLetterPending}
        />
      </form>
    </FormProvider>
  );
};

export default WarningLetterDrawer;
