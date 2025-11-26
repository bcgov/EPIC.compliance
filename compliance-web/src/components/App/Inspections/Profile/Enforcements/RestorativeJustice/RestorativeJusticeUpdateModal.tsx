import { FC, useCallback, useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import { useQueryClient } from "@tanstack/react-query";
import { Box, DialogContent } from "@mui/material";
import dayjs from "dayjs";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import ControlledDateField from "@/components/Shared/Controlled/ControlledDateField";
import {
  useUpdateRestorativeJustice,
  useDeleteRestorativeJustice,
} from "@/hooks/useRestorativeJustice";
import { useModal } from "@/store/modalStore";
import {
  RestorativeJustice,
  RestorativeJusticeUpdateAPIData,
} from "@/models/RestorativeJustice";
import { Inspection } from "@/models/Inspection";
import { notify } from "@/store/snackbarStore";
import { RestorativeJusticeStatus } from "@/utils/constants";
import { KC_USER_GROUPS, useIsRolesAllowed } from "@/hooks/useAuthorization";

const restorativeJusticeUpdateSchema = yup.object().shape({
  restitution_details: yup.string().optional(),
  date_restitution_complete: yup.mixed().nullable().optional(),
});

type RestorativeJusticeUpdateFormType = yup.InferType<
  typeof restorativeJusticeUpdateSchema
>;

type RestorativeJusticeUpdateModalProps = {
  restorativeJustice: RestorativeJustice;
  inspectionData: Inspection;
  isPrimaryOfficerOrSuperUser: boolean;
  onSuccess: (data: RestorativeJustice) => void;
};

const RestorativeJusticeUpdateModal: FC<RestorativeJusticeUpdateModalProps> = ({
  restorativeJustice,
  inspectionData,
  isPrimaryOfficerOrSuperUser,
  onSuccess,
}) => {
  const queryClient = useQueryClient();
  const { setClose } = useModal();
  const isSuperUser = useIsRolesAllowed([KC_USER_GROUPS.SUPERUSER]);

  const defaultValues = useMemo(() => {
    return {
      restitution_details: restorativeJustice.restitution_details || "",
      date_restitution_complete: restorativeJustice.date_restitution_complete
        ? dayjs(restorativeJustice.date_restitution_complete)
        : null,
    };
  }, [restorativeJustice]);

  const isReadonlyMode = useMemo(() => {
    if (restorativeJustice.status.id === RestorativeJusticeStatus.CLOSED) {
      return !isSuperUser;
    }
    if (restorativeJustice.status.id !== RestorativeJusticeStatus.CLOSED) {
      return !isPrimaryOfficerOrSuperUser;
    }
    return true;
  }, [restorativeJustice.status, isPrimaryOfficerOrSuperUser, isSuperUser]);
  const methods = useForm<RestorativeJusticeUpdateFormType>({
    resolver: yupResolver(restorativeJusticeUpdateSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { reset, handleSubmit, watch } = methods;
  const dateRestitutionComplete = watch("date_restitution_complete");

  // Determine if save confirmation is required
  const requireSaveConfirmation = useMemo(() => {
    return (
      dateRestitutionComplete !== null && dateRestitutionComplete !== undefined
    );
  }, [dateRestitutionComplete]);

  useEffect(() => {
    reset(defaultValues);
  }, [reset, defaultValues]);

  const handleSuccess = (data: RestorativeJustice) => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-restorative-justice", inspectionData.id],
    });
    notify.success("Restorative Justice updated successfully");
    onSuccess(data);
    setClose();
  };

  const { mutate: updateRestorativeJustice, isPending: isPendingUpdate } =
    useUpdateRestorativeJustice(handleSuccess);

  const { mutate: deleteRestorativeJustice, isPending: isPendingDelete } =
    useDeleteRestorativeJustice(() => {
      queryClient.invalidateQueries({
        queryKey: ["inspection-restorative-justice", inspectionData.id],
      });
      notify.success("Restorative Justice deleted successfully");
      onSuccess(restorativeJustice);
      setClose();
    });

  const handleSubmitForm = useCallback(
    (data: RestorativeJusticeUpdateFormType) => {
      const updateData: RestorativeJusticeUpdateAPIData = {
        restitution_details: data.restitution_details,
        date_restitution_complete: data.date_restitution_complete
          ? (data.date_restitution_complete as dayjs.Dayjs).format(
              "YYYY-MM-DDTHH:mm:ss.SSS[Z]"
            )
          : undefined,
      };

      updateRestorativeJustice({
        restorativeJusticeId: restorativeJustice.id,
        restorativeJustice: updateData,
        inspectionId: inspectionData.id,
      });
    },
    [updateRestorativeJustice, restorativeJustice.id, inspectionData.id]
  );

  const handleCancel = () => {
    onSuccess(restorativeJustice);
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(handleSubmitForm)}>
        <ModalTitleBar title={restorativeJustice.restorative_justice_number} />
        <DialogContent dividers sx={{ p: 0 }}>
          <Box sx={{ p: "1rem 1.5rem" }}>
            <Box>
              <ControlledTextField
                name="restitution_details"
                label="Restitution Details"
                type="text"
                fullWidth
                multiline
                minRows={1}
                disabled={isReadonlyMode}
              />
            </Box>
            <Box sx={{ mb: 1, width: "50%" }}>
              <ControlledDateField
                name="date_restitution_complete"
                label="Date Restitution Complete"
                disabled={isReadonlyMode}
              />
            </Box>
          </Box>
        </DialogContent>
        {!isReadonlyMode && (
          <ModalActions
            onSecondaryAction={handleCancel}
            onPrimaryAction={handleSubmit(handleSubmitForm)}
            isLoading={isPendingUpdate || isPendingDelete}
            primaryActionButtonText="Save"
            secondaryActionButtonText="Cancel"
            onDeleteAction={() => {
              deleteRestorativeJustice({
                restorativeJusticeId: restorativeJustice.id,
              });
            }}
            requireSaveConfirmation={requireSaveConfirmation}
          />
        )}
      </form>
    </FormProvider>
  );
};

export default RestorativeJusticeUpdateModal;
